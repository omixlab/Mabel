import os

from dotenv import load_dotenv

from .. import db
from ..models import Results

load_dotenv()
_ = os.getenv("NCBI_API_KEY")
apikey = os.getenv("X_ELS_APIKey")
insttoken = os.getenv("X_ELS_Insttoken")
dumps_path = os.getenv("DUMPS_PATH")

import json
from json import dumps, loads

import pandas as pd
import pubmed_parser as pp
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc, FullDoc
from elsapy.elssearch import ElsSearch
from metapub import PubMedFetcher

from src import celery
from src.utils.unify_dfs import unify
from src.utils.optional_features import scispacy_ner, flashtext_kp, flashtext_kp_string
from flashtext import KeywordProcessor
import json


def pubmed(keyword, num_of_articles):
    print(
        f"Starting data extraction of {num_of_articles} articles from Pubmed using the keyword: {keyword}"
    )

    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(keyword, retmax=num_of_articles)

    xmls = {}
    for pmid in pmids:
        xmls[pmid] = fetch.article_by_pmid(pmid).xml

    data_pubmed = pd.DataFrame()

    for value in xmls.values():
        dicts_out = pp.parse_medline_xml(
            value,
            year_info_only=False,
            nlm_category=False,
            author_list=False,
            reference_list=False,
        )
        data_pubmed = pd.concat(
            [data_pubmed, pd.DataFrame(dicts_out)], ignore_index=True
        )

    print("PubMed extraction done!")
    return data_pubmed


def scopus(keyword, num_of_articles):
    print(
        f"Starting data extraction of {num_of_articles} articles from Scopus using the keyword: {keyword}"
    )
    client = ElsClient(apikey)
    client.inst_token = insttoken

    doc_srch_scopus = ElsSearch(keyword, "scopus")
    t = doc_srch_scopus.execute(
        client, get_all=(num_of_articles == 5000)
    )  # get_all=True <- if num_of_articles is 5000
    print(f"doc_srch has {len(doc_srch_scopus.results)} results")

    dicts = {}

    for i in doc_srch_scopus.results_df["prism:url"]:
        scp_doc = AbsDoc(uri=i)
        if scp_doc.read(client):
            if "dc:description" in scp_doc.data["coredata"]:
                dicts[i] = scp_doc.data["coredata"]["dc:description"]
            else:
                dicts[i] = "None"
        else:
            dicts[i] = "Failed"

        print("Scopus extraction done!")

    abstracts_df = pd.DataFrame(dicts.items(), columns=["prism:url", "Abstract"])
    doc_srch_scopus.results_df = doc_srch_scopus.results_df.merge(
        abstracts_df, on="prism:url", how="left"
    )

    return doc_srch_scopus.results_df


def scidir(keyword, num_of_articles):
    print(
        f"Starting data extraction of {num_of_articles} articles from ScienceDirect using the keyword: {keyword}"
    )

    client = ElsClient(apikey)
    client.inst_token = insttoken

    doc_srch = ElsSearch(keyword, "sciencedirect")
    t = doc_srch.execute(
        client, get_all=(num_of_articles == 5000)
    )  # get_all=True <- if num_of_articles is 5000
    print("doc_srch has", len(doc_srch.results), "results.")

    abstract = []
    pubtype = []

    for i in doc_srch.results_df["prism:doi"]:

        doi_doc = FullDoc(doi=i)
        if doi_doc.read(client):
            abstract.append(doi_doc.data["coredata"]["dc:description"])
            pubtype.append(doi_doc.data["coredata"]["pubType"])
        else:
            print("Read document failed.")

    doc_srch.results_df["abstract"] = abstract
    doc_srch.results_df["pubtype"] = pubtype

    return doc_srch.results_df


def preprints(query, num_of_articles):
    keywords = query.split(", ")
    dumps = ["biorxiv.jsonl", "chemrxiv.jsonl", "medrxiv.jsonl"]

    print(f'Extracting preprints with keywords: "{keywords}"')

    def process_jsonl_file(file_path):
        with open(file_path, "r", encoding="utf-8") as jsonl_file:
            decoder = json.JSONDecoder()
            buffer = ""
            for line in jsonl_file:
                buffer += line
                while buffer:
                    try:
                        obj, idx = decoder.raw_decode(buffer)
                        yield obj
                        buffer = buffer[idx:].lstrip()
                    except json.JSONDecodeError as e:
                        break

    data_list = []
    for dump in dumps:
        file_path = os.path.join(dumps_path, dump)

        # Write model
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keywords_from_list(keywords)

        for data in process_jsonl_file(file_path):
            abstract = data.get("abstract")

            if set(kp.extract_keywords(abstract)):
                data_list.append(data)

            if len(data_list) == num_of_articles:
                break

    results_df = pd.DataFrame(data_list)
    print("Success: Preprints extracted")

    return results_df


@celery.task(bind=True, serializer="json")
def execute(
    self,
    pubmed_query="",
    elsevier_query="",
    preprints_query="",
    check_pubmed=False,
    check_scopus=False,
    check_scidir=False,
    check_preprints=False,
    pm_num_of_articles=25,
    sc_num_of_articles=25,
    sd_num_of_articles=25,
    ppr_num_of_articles=25,
    ner=None,
    kp=None,
):
    try:
        if check_pubmed or check_scopus or check_scidir or check_preprints:
            results = {}
            if check_pubmed:
                response_pubmed = pubmed(pubmed_query, pm_num_of_articles)
                results["pm"] = response_pubmed
            if check_scopus:
                response_scopus = scopus(elsevier_query, sc_num_of_articles)
                results["sc"] = response_scopus
            if check_scidir:
                response_scidir = scidir(elsevier_query, sd_num_of_articles)
                results["sd"] = response_scidir
            if check_preprints:
                response_preprints = preprints(preprints_query, ppr_num_of_articles)
                results["ppr"] = response_preprints

            # Unify results in a single dataframe
            unified_df = unify(results)
            print(unified_df.columns)

            # Prevent error from empty results
            if unified_df.empty:
                result = (
                    db.session.query(Results)
                    .filter_by(celery_id=self.request.id)
                    .first()
                )
                result.status = "NO RESULTS"
                db.session.commit()
                return "No results"

            # Scispacy NER
            if ner:
                print(f"Running NER for {ner} entities")
                unified_df = scispacy_ner(unified_df, ner)

            # Flashtext Keyword Processor
            if type(kp) is str:
                print(f"Filtering {kp} with Flashtext")
                unified_df = flashtext_kp_string(unified_df, kp)
            if type(kp) is list:
                print(f"Filtering {kp} with Flashtext")
                unified_df = flashtext_kp(unified_df, kp)

            # Return as json
            result_json = unified_df.to_json(orient="records", indent=4)
            result = (
                db.session.query(Results).filter_by(celery_id=self.request.id).first()
            )
            result.status = "DONE"
            result.result_json = result_json
            db.session.commit()
            return result_json

        else:
            return "None database selected"

    except Exception as e:
        # exception_message = str(e)
        result = db.session.query(Results).filter_by(celery_id=self.request.id).first()
        result.status = "FAILED"
        db.session.commit()
        raise
