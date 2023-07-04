import streamlit as st
import utils.dicts.basic as basics


def basic():
    if "pm_query" not in st.session_state:
        st.session_state.pm_query = None
        st.session_state.sc_query = None

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        # Tags
        select = st.selectbox("Tags", basics.tags, key="tag", label_visibility="hidden")
        tag = select

    with col2:
        # Text input
        term = st.text_input("Search term", key="term")

        # Filter
        if st.checkbox("Open access"):
            if st.session_state.pm_query is None:
                st.session_state.pm_query = "(ffrft[Filter])"
            elif "(ffrft[Filter])" not in st.session_state.pm_query:
                st.session_state.pm_query += " AND (ffrft[Filter])"

            if st.session_state.sc_query is None:
                st.session_state.sc_query = "OPENACCESS(1)"
            elif "OPENACCESS(1)" not in st.session_state.sc_query:
                st.session_state.sc_query += " AND OPENACCESS(1)"

    with col3:
        # Boolean operator
        boolean = st.selectbox(
            "Bool", ("AND", "OR", "NOT"), key="bool", label_visibility="hidden"
        )

        if st.button("Add"):
            # PubMed query constructor
            if st.session_state.pm_query is None:
                st.session_state.pm_query = f"({term}{basics.to_pubmed[tag]})"
            else:
                st.session_state.pm_query += (
                    f" {boolean} ({term}{basics.to_pubmed[tag]})"
                )

            # Elsevier query constructor
            if st.session_state.sc_query is None:
                st.session_state.sc_query = f"{basics.to_scopus[tag]}({term})"
            else:
                st.session_state.sc_query += (
                    f" {boolean} {basics.to_scopus[tag]}({term})"
                )

    # Queries
    pm_keyword = st.text_area(
        "PubMed query", st.session_state.pm_query, key="pm_keyword"
    )
    if st.session_state.pm_query is not None:
        st.session_state.pm_query = pm_keyword

    sc_keyword = st.text_area(
        "Elsevier query", st.session_state.sc_query, key="sc_keyword"
    )
    if st.session_state.sc_query is not None:
        st.session_state.sc_query = sc_keyword

    # DATABASES SELECTION
    st.write("Select your desired databases")
    col1, col2 = st.columns([1, 2])
    with col1:
        pubmed_check = st.checkbox("PubMed", True)
    with col2:
        articles_range = (
            list(range(1, 25))
            + list(range(25, 50, 5))
            + list(range(50, 250, 10))
            + list(range(250, 1000, 50))
            + list(range(1000, 5001, 100))
        )
        num_pubmed = st.select_slider(
            "Number of PubMed articles: ",
            options=articles_range,
            value=5000,
            disabled=(not pubmed_check),
        )

    col1, col2 = st.columns([1, 2])
    with col1:
        scopus_check = st.checkbox("Scopus", True)
    with col2:
        num_scopus = st.select_slider(
            "Number of Scopus articles: ",
            options=[25, 5000],
            value=5000,
            disabled=(not scopus_check),
        )

    col1, col2 = st.columns([1, 2])
    with col1:
        scidir_check = st.checkbox("ScienceDirect", True)
    with col2:
        num_scidir = st.select_slider(
            "Number of ScienceDirect articles: ",
            options=[25, 5000],
            value=5000,
            disabled=(not scidir_check),
        )

    with st.expander("Scispacy"):
        st.write('See key elements of abstracts in a separated column of your dataframe using Scispacy')
        options = {'Gene or gene products': 'genes'}

        scispacy_param = []
        for opt in options:
            if st.checkbox(f'{opt}'):
                scispacy_param.append(options[opt])


    # RETURN AS DICT
    request = {
        "pm_keyword": pm_keyword,
        "sc_keyword": sc_keyword,
        "sd_keyword": sc_keyword,
        "pm_check": pubmed_check,
        "sc_check": scopus_check,
        "sd_check": scidir_check,
        "pm_num": num_pubmed,
        "sc_num": num_scopus,
        "sd_num": num_scidir,
        "scispacy_param": set(scispacy_param)
    }
    return request
