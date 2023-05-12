import os
from dotenv import load_dotenv
load_dotenv()
_ = os.getenv("NCBI_API_KEY")
ELSEVIER_API_KEY = os.getenv('ELSEVIER_API_KEY')
X_ELS_Insttoken = os.getenv('X_ELS_Insttoken')

import pandas as pd
import numpy as np
import metapub
import pubmed_parser as pp
from metapub import PubMedFetcher
from functools import reduce
import json
from json import loads
import requests
import urllib.parse


class Extractor:
    def __init__(self, keyword, num_of_articles):
        self.keyword = keyword
        self.num_of_articles = num_of_articles

        self.pubmed_kw = self.keyword.replace(')', '[MeSH Terms])')
        self.elsevier_kw = elsevier_kw = urllib.parse.quote_plus(self.keyword)
        # Deveria colocar em lower case?
        # (cancer of the prostate) AND (molecular targeted therapy)                                     RAW
        #   -> (cancer of the prostate[MeSH Terms]) AND (molecular targeted therapy[MeSH Terms])        PUBMED
        #   -> %28cancer+of+the+prostate%29+AND+%28+molecular+targeted+therapy%29                       ELSEVIER


        if num_of_articles > 25:
            self.scopus_num = 25
        else: 
            self.scopus_num = num_of_articles

        if num_of_articles > 100:
            self.scidir_num = 100
        else:
            self.scidir_num = num_of_articles

    

    def pubmed(self):
        print(f"Starting data extraction of {self.num_of_articles} articles from Pubmed using the keyword: {self.pubmed_kw}")

        fetch = PubMedFetcher()
        pmids = fetch.pmids_for_query(self.pubmed_kw, retmax=self.num_of_articles)

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

        data_pubmed.to_csv('data/csv/pubmed_data.csv')

        print('PubMed extraction done!')
        return data_pubmed
    

    def scopus(self):
        print(f"Starting data extraction of {self.scopus_num} articles from Elsevier (Scopus) using the keyword: {self.elsevier_kw}")

        url = f"http://api.elsevier.com/content/search/scopus?query=KEY{self.elsevier_kw}"

        resp = requests.get(url,
                            headers = {'Accept': 'application/json',
                                    'X-ELS-APIKey': ELSEVIER_API_KEY,
                                    'X-ELS-Insttoken': X_ELS_Insttoken,
                                    'X-RateLimit-Reset': None})

        try:
            print(resp.header['X-RateLimit-Remaining'])
        except:
            pass


        dic = loads(resp.content)

        data = pd.DataFrame.from_dict(dic)

        for i in data.iloc[0]:
            scopus_data = pd.DataFrame(i)
            
        scopus_data.to_csv('data/csv/scopus_data.csv')

        print('Scopus extraction done!')
        return scopus_data
    

    def scidir(self):
        print(f"Starting data extraction of {self.scidir_num} articles from Elsevier (ScienceDirect) using the keyword: {self.elsevier_kw}")

        url = f"https://api.elsevier.com/content/search/sciencedirect?query={self.elsevier_kw}&count={self.scidir_num}"

        resp = requests.get(url,
                            headers = {'Accept': 'application/json',
                                    'X-ELS-APIKey': ELSEVIER_API_KEY,
                                    'X-ELS-Insttoken': X_ELS_Insttoken,
                                    'X-RateLimit-Reset': None})
        

        try:
            print(resp.header['X-RateLimit-Remaining'])
        except:
            pass


        dic = loads(resp.content)

        data = pd.DataFrame.from_dict(dic)

        for i in data.iloc[0]:
            scidir_data = pd.DataFrame(i)
            
        scidir_data.to_csv('data/csv/scidir_data.csv')

        print('ScienceDirect extraction done!')
        return scidir_data
