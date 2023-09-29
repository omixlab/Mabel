import os

from .. import db
from ..models import Results
from dotenv import load_dotenv

load_dotenv()
_ = os.getenv("NCBI_API_KEY")
apikey = os.getenv("X_ELS_APIKey")
insttoken = os.getenv("X_ELS_Insttoken")

import pandas as pd
import pubmed_parser as pp
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc, FullDoc
from elsapy.elssearch import ElsSearch
from metapub import PubMedFetcher
from src import celery
from json import loads, dumps
from src.utils.unify_dfs import unify
from src.utils.spacy import scispacy_ner, only_genes_ner
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
    return  data_pubmed

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
        
@celery.task(bind=True, serializer="json")
def execute(
    self,
    pubmed_query="Cancer Prostata",
    elsevier_query="Prostate Cancer",
    check_pubmed=False,
    check_scopus=False,
    check_scidir=False,
    pm_num_of_articles=25,
    sc_num_of_articles=25,
    sd_num_of_articles=25,
    ner = None,
    selected_models = None
):
    try:
        if check_pubmed or check_scopus or check_scidir:
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

            # Unify 3 results in a single dataframe
            unified_df = unify(results)

            # Prevent error from empty results
            if unified_df.empty:
                result = db.session.query(Results).filter_by(celery_id=self.request.id).first()
                result.status = 'NO RESULTS'
                db.session.commit()
                return "No results"

            # Scispacy
            if ner:
                if ner == ["genes"]:
                    print(f'Running NER for only genes entities')
                    unified_df = only_genes_ner(unified_df, selected_models)
                else:
                    print(f'Running NER for {ner} entities')
                    unified_df = scispacy_ner(unified_df, ner)

            # Return as json
            result_json = unified_df.to_json(orient='records', indent=4)
            result = db.session.query(Results).filter_by(celery_id=self.request.id).first()
            result.status = 'DONE'
            result.result_json = result_json
            db.session.commit()
            return result_json

        else:
            return "None database selected"
    
    except Exception as e:
        # exception_message = str(e)
        result = db.session.query(Results).filter_by(celery_id=self.request.id).first()
        result.status = 'FAILED'
        db.session.commit()
        raise
