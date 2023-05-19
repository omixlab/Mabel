import streamlit as st

def basic():
    keyword = st.text_input("Keyword")

    st.write('Select your desired databases')
    col1, col2 = st.columns([1,2])
    with col1:
        pubmed_check = st.checkbox('PubMed', True)
    with col2:
        articles_range = [1, 5, 10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
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

def advanced():
    # PubMed
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('PubMed')
        pubmed_check = st.checkbox('Enabled', False, key='p')
    with col2:
        articles_range = [1, 5, 10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
        num_pubmed = st.select_slider('Number of articles: ', options=articles_range, value=5000, disabled=(not pubmed_check), key='pm_num')

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        tag = st.selectbox(
            '',
            ('All Fields', 'Date', 'Filter',
             'Author', 'Affiliation' 'Book', 'Journal', 'Volume', 'Pagination', 'Title', 'Title/Abstract', 'Transliterated Title', 'Text Word',
             'Language', 'MeSH', 'Pharmacological Action', 'Conflict of Interest Statements', 'EC/RN Number', 'Grant Number', 'ISBN', 'Investigator',
             'Issue', 'Location ID', 'Secondary Source ID', 'Other Term', 'Publication Type', 'Publisher', 'Subject - Personal Name', 'Supplementary Concept',  
             ), key='pm_tag', disabled=(not pubmed_check), label_visibility="visible"
             )
    with col2:
        term = st.text_input('Search term', key='pm_term', disabled=(not pubmed_check))
    with col3:
        boolean = st.selectbox('', ('AND', 'OR', 'NOT'))
    
    if 'query' not in st.session_state:
        st.session_state.query = None


    if st.button('Add'):
        if st.session_state.query is None:
            st.session_state.query = f'({term})'
        else:
            if tag == 'All Fields':
                st.session_state.query += f' {boolean} ({term})'
            else:
                st.session_state.query += f' {boolean} ({term})[{tag}]'
        
    with st.container():
        st.write(st.session_state.query)
        pm_keyword = st.session_state.query
    

    # Scopus
    st.markdown('***')    
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('Scopus')
        scopus_check = st.checkbox('Enabled', False, key='sc')
    with col2:
        num_scopus = st.select_slider('Number of articles: ', options=[25, 5000], value=5000, disabled=(not scopus_check), key='sc_num')

    st.markdown('***')
    # ScienceDirect
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('ScienceDirect')
        scidir_check = st.checkbox('Enabled', False, key='sd')
    with col2:
        num_scidir = st.select_slider('Number of articles: ', options=[25, 5000], value=5000, disabled=(not scidir_check), key='sd_num')


    request = {
        'pm_keyword': pm_keyword,
        #'sc_keyword': sc_keyword,
        #'sd_keyword': sd_keyword,
        'pm_check': pubmed_check,
        'sc_check': scopus_check,
        'sd_check': scidir_check,
        'pm_num': num_pubmed,
        'sc_num': num_scopus,
        'sd_num': num_scidir
    }
    return request