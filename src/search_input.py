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



def advanced():
    # PUBMED
    def force_update():
        pass

    # Start variables as session states
    if 'pm_query' not in st.session_state:
        st.session_state.pm_query = None
    if 'selected_filters' not in st.session_state:
        st.session_state.selected_filters = []

    if 'sc_query' not in st.session_state:
        st.session_state.sc_query = None

    if 'sd_query' not in st.session_state:
        st.session_state.sd_query = None


    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('PubMed')
        pubmed_check = st.checkbox('Enabled', False, key='p')
    with col2:
        # Number of articles
        articles_range = list(range(1, 25)) + list(range(25, 50, 5)) + list(range(50, 250, 10)) + list(range(250, 1000, 50)) + list(range(1000, 5001, 100))
        num_pubmed = st.select_slider('Number of articles: ', options=articles_range, value=5000, disabled=(not pubmed_check), key='num_pubmed')

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        # Tags
        select = st.selectbox('Tags',
            ('All Fields', 'Date',
             'Author', 'Affiliation', 'Book', 'Journal', 'Volume', 'Pagination', 'Title', 'Title/Abstract', 'Transliterated Title', 'Text Word',
             'Language', 'MeSH', 'Pharmacological Action', 'Conflict of Interest Statements', 'EC/RN Number', 'Grant Number', 'ISBN', 'Investigator',
             'Issue', 'Location ID', 'Secondary Source ID', 'Other Term', 'Publication Type', 'Publisher', 'Subject - Personal Name', 'Supplementary Concept',  
             ), key='pm_tag', disabled=(not pubmed_check), label_visibility="hidden"
             )
        
        if select == 'All Fields':
            tag = ''
        elif select == 'Author':
            tag = f"[{st.radio('Type', ('Author', 'Author - Corporate', 'Author - First', 'Author - Last', 'Author - Identifier'))}]"
        elif select == 'MeSH':
            tag = f"[{st.radio('Type', ('MeSH Major Topic', 'MeSH Subheading', 'MeSH Terms'))}]"
        elif select == 'Date':
            tag = f"[{st.radio('Type', ('Date - Completion', 'Date - Create', 'Date - Entry', 'Date - MeSH', 'Date Modification', 'Date Publication'))}]"
        else:
            tag = select

    with col2:
        if select == 'Date':
            # Date input
            col21, col22 = st.columns([1, 1])
            with col21:
                date1 = st.text_input('Start', help='YYYY/MM/DD', key='date1')
            with col22:
                date2 = st.text_input('End', help='YYYY/MM/DD', key='date2')
            term = f'"{date1}"[{tag}] : "{date2}"'
        else:
            # Text input
            term = st.text_input('Search term', key='pm_term', disabled=(not pubmed_check))
        
        # Filtros
        with st.expander('Filters', expanded=False):
            # Show filters
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Availability", "Type", "Test subject", "Language", "Others"])
            tabs = [tab1, tab2, tab3, tab4, tab5]
            for n in range(len(tabs)):
                with tabs[n]:
                    for filter in pubmed.pubmed_filters[n]:
                        if st.checkbox(filter, disabled=(not pubmed_check)):
                            st.session_state.selected_filters.append(filter)

            # Apply filters
            if st.button("Apply filters", disabled=(not pubmed_check)):
                filters_set = set()
                for key in st.session_state.selected_filters:
                    filters_set.add(pubmed.pubmed_dict.get(key))

                st.session_state.pm_query += ' AND ('
                for i, filter in enumerate(filters_set):
                    if i == 0:
                        st.session_state.pm_query += f'({filter}[Filter])'
                    else: st.session_state.pm_query += f' OR ({filter}[Filter])'
                st.session_state.pm_query += ')'


    with col3:
        # Boolean operator
        boolean = st.selectbox('Bool', ('AND', 'OR', 'NOT'), key='bool', disabled=(not pubmed_check), label_visibility="hidden")

        # Query
        if st.button('Add', disabled=(not pubmed_check), key='pm_add'):
            if st.session_state.pm_query is None or '':
                st.session_state.pm_query = f'({term}{tag})'
            else:
                st.session_state.pm_query += f' {boolean} ({term}{tag})'
                
            
            
    pm_keyword = st.text_area('Query', st.session_state.pm_query, disabled=(not pubmed_check), key='pm_keyword', 
                              help='This is the query sent for your search. You can type it manually if you prefer.\n\nLeave blank and press Ctrl+Enter to reset query')
    if st.session_state.pm_query is not None:
        st.session_state.pm_query = pm_keyword
    if pm_keyword == '':
        st.session_state.pm_query = None
    




#SCOPUS
    st.markdown('***')    
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('Scopus')
        scopus_check = st.checkbox('Enabled', False, key='sc')
    with col2:
        num_scopus = st.select_slider('Number of articles: ', options=[25, 5000], value=5000, disabled=(not scopus_check), key='sc_num')

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        # Tags
        select = st.selectbox('Tags', scopus.tags, disabled=(not scopus_check))

        if select in scopus.radios:
            sc_tag = st.radio('Type', scopus.radios[select])
        else:
            sc_tag = select

    with col2:
        # Search terms
        if sc_tag in scopus.selects:
            sc_term = st.selectbox('Search term', scopus.selects[sc_tag])
            sc_term = scopus.selects[sc_tag][sc_term]
            

        elif sc_tag == 'Date':
            col21, col22 = st.columns([1, 4])
            with col21:
                operator = st.selectbox('Operator', (' > ', ' = ', ' < '), label_visibility="hidden")
            with col22:
                year = st.text_input('Year')
            sc_term = operator + year

        else:
            sc_term = st.text_input('Search term', key='sc_term', disabled=(not scopus_check))

        # Filter
        if st.checkbox('Open access', disabled=(not scopus_check)):
            if st.session_state.sc_query is None:
                st.session_state.sc_query = 'OPENACCESS(1)'
            elif 'OPENACCESS(1)' not in st.session_state.sc_query:
                st.session_state.sc_query += ' AND OPENACCESS(1)'
    
    with col3:
        # Boolean operator
        boolean = st.selectbox('Bool', ('AND', 'OR', 'NOT'), key='sc_bool', disabled=(not scopus_check), label_visibility="hidden")

        # Query
        if st.button('Add', disabled=(not scopus_check), key='sc_add'):
            if st.session_state.sc_query is not None:
                st.session_state.sc_query += f' {boolean} '
            
            if sc_tag == 'Date':
                st.session_state.sc_query += f'PUBYEAR {sc_term}'
            elif sc_tag == 'Reference year':
                st.session_state.sc_query += f'REFPUBYEAR IS {sc_term}'

            else:
                if st.session_state.sc_query is None:
                    st.session_state.sc_query = f'{scopus.field[sc_tag]}({sc_term})'
                else:
                    st.session_state.sc_query += f'{scopus.field[sc_tag]}({sc_term})'


    sc_keyword = st.text_area('Query', st.session_state.sc_query, disabled=(not scopus_check), key='sc_keyword', 
                              help='This is the query sent for your search. You can type it manually if you prefer.\n\nLeave blank and press Ctrl+Enter to reset query')
    if st.session_state.sc_query is not None:
        st.session_state.sc_query = sc_keyword





    # SCIENCE DIRECT
    st.markdown('***')
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('ScienceDirect')
        scidir_check = st.checkbox('Enabled', False, key='sd')
    with col2:
        num_scidir = st.select_slider('Number of articles: ', options=[25, 5000], value=5000, disabled=(not scidir_check), key='sd_num')

    sd_keyword = st.text_area('Query', st.session_state.sd_query, disabled=(not scidir_check), key='sd_keyword', 
                              help='This is the query sent for your search. You can type it manually if you prefer.\n\nLeave blank and press Ctrl+Enter to reset query')
    if st.session_state.sd_query is not None:
        st.session_state.sd_query = sd_keyword





    # Return everything as a dictionary
    request = {
        'pm_keyword': pm_keyword,
        'sc_keyword': sc_keyword,
        'sd_keyword': sd_keyword,
        'pm_check': pubmed_check,
        'sc_check': scopus_check,
        'sd_check': scidir_check,
        'pm_num': num_pubmed,
        'sc_num': num_scopus,
        'sd_num': num_scidir
    }
    return request