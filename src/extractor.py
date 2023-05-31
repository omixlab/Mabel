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


class Extractor:
    def __init__(self, keyword, num_of_articles):
        self.keyword = keyword
        self.num_of_articles = num_of_articles

    def pubmed(self):
        print(f"Starting data extraction of {self.num_of_articles} articles from Pubmed using the keyword: {self.keyword}")

        fetch = PubMedFetcher()
        pmids = fetch.pmids_for_query(self.keyword, retmax=self.num_of_articles)

        xmls = {}
        for pmid in pmids:
            xmls[pmid] = fetch.article_by_pmid(pmid).xml

        data_pubmed = pd.DataFrame()

        for key, value in xmls.items():
            with open(f"data/xmls/{key}.xml", "wb") as f:
                f.write(value)

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

        data_pubmed.to_csv("data/csv/pubmed_data.csv")

        print("PubMed extraction done!")
        return data_pubmed

    def scopus(self):
        print(f"Starting data extraction of {self.num_of_articles} articles from Scopus using the keyword: {self.keyword}")
        client = ElsClient(apikey)
        client.inst_token = insttoken

        doc_srch_scopus = ElsSearch(self.keyword, "scopus")
        t = doc_srch_scopus.execute(client, get_all=(self.num_of_articles == 5000))      # get_all=True <- if num_of_articles is 5000
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

    def scidir(self):
        print(f"Starting data extraction of {self.num_of_articles} articles from ScienceDirect using the keyword: {self.keyword}")
        client = ElsClient(apikey)
        client.inst_token = insttoken

        doc_srch = ElsSearch(self.keyword, "sciencedirect")
        t = doc_srch.execute(client, get_all=(self.num_of_articles == 5000))            # get_all=True <- if num_of_articles is 5000
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
