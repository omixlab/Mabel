import pandas as pd

pubmed = pd.read_csv('/home/gabrielliston/Downloads/pubmed_df.csv')
scopus = pd.read_csv('/home/gabrielliston/Downloads/scopus_df.csv')
scidir = pd.read_csv('/home/gabrielliston/Downloads/scidir_df.csv')

pm = pd.DataFrame({
    'Title': pubmed['title'],
    'Abstract': pubmed['abstract'],
    'Pages': pubmed['pages'],
    'Journal': pubmed['journal'],
    'Authors': pubmed['authors'],
    'Date': pubmed['pubdate'],
    'Type': pubmed['publication_types'],
    'DOI': pubmed['doi'],
    'Affiliations': pubmed['affiliations'],
    'Country': pubmed['country'],
    'MeSH Terms': pubmed['mesh_terms'],
})

sc = pd.DataFrame({
    'Title': scopus['dc:title'],
    'Abstract': scopus['Abstract'],
    'Pages': scopus['prism:pageRange'],
    'Journal': scopus['prism:publicationName'],
    'Authors': scopus['dc:creator'],
    'Date': scopus['prism:coverDate'],
    'Type': scopus['prism:aggregationType'],
    'DOI': scopus['prism:doi'],
    'Affiliations': scopus['affiliation'],
    'Country': scopus['affiliation'],
    'MeSH Terms': None
})

sd = pd.DataFrame({
    'Title': scidir['dc:title'],
    'Abstract': scidir['abstract'],
    'Pages': scidir['prism:startingPage'],
    'Journal': scidir['prism:publicationName'],
    'Authors': scidir['authors'],
    'Date': scidir['prism:coverDate'],
    'Type': scidir['pubtype'],
    'DOI': scidir['prism:doi'],
    'Affiliations': None,
    'Country': None,
    'MeSH Terms': None
})

dataframes = [pubmed, scopus, scidir]

