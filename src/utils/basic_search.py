import streamlit as st
import utils.pubmed as pubmed
import utils.scopus as scopus

def basic():
    keyword = st.text_input("Keyword")





    st.write('Select your desired databases')
    col1, col2 = st.columns([1,2])
    with col1:
        pubmed_check = st.checkbox('PubMed', True)
    with col2:
        articles_range = list(range(1, 25)) + list(range(25, 50, 5)) + list(range(50, 250, 10)) + list(range(250, 1000, 50)) + list(range(1000, 5001, 100))
        num_pubmed = st.select_slider('Number of PubMed articles: ', options=articles_range, value=5000, disabled=(not pubmed_check))

    col1, col2 = st.columns([1,2])
    with col1:
        scopus_check = st.checkbox('Scopus', True)
    with col2:
        num_scopus = st.select_slider('Number of Scopus articles: ', options=[25, 5000], value=5000, disabled=(not scopus_check))

    col1, col2 = st.columns([1,2])
    with col1:
        scidir_check = st.checkbox('ScienceDirect', True)
    with col2:
        num_scidir = st.select_slider('Number of ScienceDirect articles: ', options=[25, 5000], value=5000, disabled=(not scidir_check))


    request = {
        'pm_keyword': keyword,
        'sc_keyword': keyword,
        'sd_keyword': keyword,
        'pm_check': pubmed_check,
        'sc_check': scopus_check,
        'sd_check': scidir_check,
        'pm_num': num_pubmed,
        'sc_num': num_scopus,
        'sd_num': num_scidir
    }
    return request