import os
from dotenv import load_dotenv

load_dotenv()
_ = os.getenv("NCBI_API_KEY")

import pandas as pd
import numpy as np
import metapub
import pubmed_parser as pp
from metapub import PubMedFetcher
from functools import reduce

import json
from json import loads
import requests
import urllib 


# PubMed Extractor
def extractor_pubmed(keyword, num_of_articles):
    print(f"Starting data extraction of {num_of_articles} articles from Pubmed using the keyword: {keyword}")

    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(keyword, retmax=num_of_articles)

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

    print('Extraction done!')
    return data_pubmed



# Elsevier Extractor
ELSEVIER_API_KEY = os.getenv('ELSEVIER_API_KEY')
X_ELS_Insttoken = os.getenv('X_ELS_Insttoken')

# SCOPUS
def extractor_scopus(keyword, num_of_articles=25):
    print(f"Starting data extraction of {num_of_articles} articles from Elsevier (Scopus) using the keyword: {keyword}")

    url = f"http://api.elsevier.com/content/search/scopus?query=KEY{keyword}"

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

    print('Done!')
    return scopus_data


# SCIENCE DIRECT
def extractor_scidir(keyword, num_of_articles=100):
    print(f"Starting data extraction of {num_of_articles} articles from Elsevier (ScienceDirect) using the keyword: {keyword}")

    url = f"https://api.elsevier.com/content/search/sciencedirect?query={keyword}&count={num_of_articles}"

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

    print('Done!')
    return scidir_data


# MAIN
def main(num_of_articles=None, *args):
    # Caso os parâmetros não sejam fornecidos (temporário)
    if not args:
        args = [input("Insert your keyword: ")]
        while True:
            extra = input("Insert more keywords or leave blank to continue: ")
            if extra == '':
                break
            args.append(extra)

        keyword = f'({args[0]})'
        for arg in args:
            if arg != args[0]:
                keyword += f' AND ({arg})'
            
    if not num_of_articles:
        num_of_articles = int(input('Provide a number of articles to extract: '))

    
    # Converter keyword
    pubmed_kw = keyword.replace(')', '[MeSH Terms])') 
    elsevier_kw = keyword.replace('AND ', '').replace(' ', '+').replace('(', '%28').replace(')', '%29')         # Deveria colocar em lower case?
    # (cancer of the prostate) AND (molecular targeted therapy)                                     RAW
    #   -> (cancer of the prostate[MeSH Terms]) AND (molecular targeted therapy[MeSH Terms])        PUBMED
    #   -> %28cancer+of+the+prostate%29+%28+molecular+targeted+therapy%29                           ELSEVIER

    # Chamar as funções                       
    extractor_pubmed(pubmed_kw, num_of_articles)
    
    if num_of_articles > 100:
        num_of_articles = 100
    extractor_scidir(elsevier_kw, num_of_articles)

    if num_of_articles > 25:
        num_of_articles = 25
    extractor_scopus(elsevier_kw, num_of_articles)


if __name__ == '__main__':
    main()
