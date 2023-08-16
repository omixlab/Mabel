import os

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
from dataclasses import dataclass
from src.utils.dicts_tuples.basic_tuple import to_pubmed

@dataclass
class Extractor:
    pubmed_query: str
    elsevier_query: str
    num_of_articles: int


def query_constructor(pm_query, els_query, tag, keyword, boolean, open_access):
    # PubMed query
    if not pm_query:
        pm_query = f"({keyword}{to_pubmed[tag]})"
    else:
        pm_query += f" {boolean} ({keyword}{to_pubmed[tag]})"

    # Elsevier query
    if not els_query:
        els_query = f'{tag}({keyword})'
    else:
        els_query += f' {boolean} {tag}({keyword})'

    # Filter
    if open_access and 'ffrft[Filter]' not in pm_query:
        pm_query += ' AND (ffrft[Filter])'
    if open_access and 'OPENACCESS(1)' not in els_query:
        els_query += ' AND OPENACCESS(1)'

    return pm_query, els_query


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
    data_pubmed = pd.concat([data_pubmed, pd.DataFrame(dicts_out)], ignore_index=True)

    print("PubMed extraction done!")
    # return  data_pubmed
    results = data_pubmed.to_json(orient="records")
    parsed = loads(results)

    return dumps(parsed, indent=4)


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
    print("doc_srch has", len(doc_srch_scopus.results), "results.")

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
    doc_srch_scopus.results_df

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


@celery.task(serializer="json")
def execute(
    pubmed_query="Cancer Prostata",
    elsevier_query="Prostate Cancer",
    check_pubmed=False,
    check_scopus=False,
    check_scidir=False,
    pm_num_of_articles=25,
    sc_num_of_articles=25,
    sd_num_of_articles=25,
):
    if check_pubmed or check_scopus or check_scidir:
        results = []
        if check_pubmed:
            response_pubmed = pubmed(pubmed_query, pm_num_of_articles)
            results.append(response_pubmed)
        if check_scopus:
            response_scopus = scopus(elsevier_query, sc_num_of_articles)
            results.append(response_scopus)
        if check_scidir:
            response_scidir = scidir(elsevier_query, sd_num_of_articles)
            results.append(response_scidir)
        #ta retornando null por conta do print aqui 
        return print(results)

    else:
        return "None database selected"
