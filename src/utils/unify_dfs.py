import pandas as pd
import numpy as np
import json

def unify(pm_df=None, sc_df=None, sd_df=None):

    pubmed = pm_df

    # Formatação de alguns elementos
    pm_formated_auth = []
    for row in pubmed['authors']:
        if row != '':
            authors_list = row.split(';')
            formated_auth_str = ''
            for author in authors_list:
                info = author.split('|')
                lastname, firstname = info[0], info[1]
                formated_auth_str += f'{lastname} {firstname}; '
            pm_formated_auth.append(formated_auth_str)
        else:
            pm_formated_auth.append(np.nan)

    pm_formated_type = []
    for row in pubmed['publication_types']:
        if ';' in row:
            type_list = row.split(';')
            formated_type_str = [''.join(type.split(":", 1)[1:]) for type in type_list]
            pm_formated_type.append('; '.join(formated_type_str))

        else:
            pm_formated_type.append(''.join(row.split(":", 1)[1:]))

    # Converte em dataframes padronizados
    pm = pd.DataFrame({
        'Title': pubmed['title'],
        'Abstract': pubmed['abstract'],
        'Pages': pubmed['pages'],
        'Journal': pubmed['journal'],
        'Authors': pm_formated_auth,
        'Date': pubmed['pubdate'],
        'Type': pm_formated_type,
        'DOI': pubmed['doi'],
        'Affiliations': pubmed['affiliations'],
        'MeSH Terms': pubmed['mesh_terms'],
        })


    # SCOPUS
    scopus = sc_df

    sc_formated_affil = []
    for row in scopus['affiliation']:
        sc_formated_affil.append('; '.join([entry['affilname'] for entry in row]))

    sc = pd.DataFrame({
        'Title': scopus['dc:title'],
        'Abstract': scopus['Abstract'],
        'Pages': scopus['prism:pageRange'],
        'Journal': scopus['prism:publicationName'],
        'Authors': scopus['dc:creator'],
        'Date': scopus['prism:coverDate'],
        'Type': scopus['subtypeDescription'],
        'DOI': scopus['prism:doi'],
        'Affiliations': sc_formated_affil,
        'MeSH Terms': np.nan
        })


    # SCIENCE DIRECT
    scidir = sd_df

    sd_formated_auth = []
    for row in scidir['authors']:
        sd_formated_auth.append('; '.join([entry['$'] for entry in row['author']]))
    
    sd_formated_pages = []
    for start, end in zip(scidir['prism:startingPage'], scidir['prism:endingPage']):
        sd_formated_pages.append(f'{start}-{end}')

    sd = pd.DataFrame({
        'Title': scidir['dc:title'],
        'Abstract': scidir['abstract'],
        'Pages': sd_formated_pages,
        'Journal': scidir['prism:publicationName'],
        'Authors': sd_formated_auth,
        'Date': scidir['prism:coverDate'],
        'Type': scidir['pubtype'],
        'DOI': scidir['prism:doi'],
        'Affiliations': np.nan,
        'MeSH Terms': np.nan
    })


    # Concatenação dos dataframes
    return pd.concat([pm, sc, sd])

