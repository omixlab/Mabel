import streamlit as st
import utils.dicts.pubmed as pubmed
import utils.dicts.scopus as scopus


def advanced():
    # PUBMED

    # Start variables as session states
    if "pm_query" not in st.session_state:
        st.session_state.pm_query = None
    if "selected_filters" not in st.session_state:
        st.session_state.selected_filters = []

    if "disable_bool" not in st.session_state:
        st.session_state.disable_bool = False

    if "sc_query" not in st.session_state:
        st.session_state.sc_query = None
    if "sd_query" not in st.session_state:
        st.session_state.sd_query = None

    col1, col2 = st.columns([1, 2])
    with col1:
        # Enable Pubmed
        st.subheader("PubMed")
        pubmed_check = st.checkbox("Enabled", False, key="p")
    with col2:
        # Number of articles
        articles_range = (
            list(range(1, 25))
            + list(range(25, 50, 5))
            + list(range(50, 250, 10))
            + list(range(250, 1000, 50))
            + list(range(1000, 5001, 100))
        )
        num_pubmed = st.select_slider(
            "Number of articles: ",
            options=articles_range,
            value=5000,
            disabled=(not pubmed_check),
            key="num_pubmed",
        )

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        # Tags
        select = st.selectbox(
            "Field", pubmed.tags, key="pm_tag", disabled=(not pubmed_check)
        )

        if select == "All Fields":
            tag = ""
        elif select in pubmed.radios:
            tag = f"[{st.radio('Type', pubmed.radios[select])}]"
        else:
            tag = f"[{select}]"

    with col2:
        if select == "Date":
            # Date input
            col21, col22 = st.columns([1, 1])
            with col21:
                date1 = st.text_input("Start", help="YYYY/MM/DD", key="date1")
            with col22:
                date2 = st.text_input("End", help="YYYY/MM/DD", key="date2")
            term = f'"{date1}"[{tag}] : "{date2}"'
        else:
            # Text input
            term = st.text_input(
                "Search term", key="pm_term", disabled=(not pubmed_check)
            )

        # Filtros
        with st.expander("Filters", expanded=False):
            # Show filters
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["Availability", "Type", "Test subject", "Language", "Others"]
            )
            tabs = [tab1, tab2, tab3, tab4, tab5]
            for n in range(len(tabs)):
                with tabs[n]:
                    for filter in pubmed.filters[n]:
                        if st.checkbox(filter, disabled=(not pubmed_check)):
                            st.session_state.selected_filters.append(filter)

            # Apply filters
            if st.button("Apply filters", disabled=(not pubmed_check)):
                filters_set = set()
                for key in st.session_state.selected_filters:
                    filters_set.add(pubmed.dict.get(key))

                st.session_state.pm_query += " AND ("
                for i, filter in enumerate(filters_set):
                    if i == 0:
                        st.session_state.pm_query += f"({filter}[Filter])"
                    else:
                        st.session_state.pm_query += f" OR ({filter}[Filter])"
                st.session_state.pm_query += ")"

    with col3:
        # Boolean operator
        boolean = st.selectbox(
            "Bool",
            ("AND", "OR", "NOT"),
            key="bool",
            disabled=(not pubmed_check),
            label_visibility="hidden",
        )

        # Query constructor
        if st.button("Add", disabled=(not pubmed_check), key="pm_add"):
            if st.session_state.pm_query is None or "":
                st.session_state.pm_query = f"({term}{tag})"
            else:
                st.session_state.pm_query += f" {boolean} ({term}{tag})"

    # Query
    pm_keyword = st.text_area(
        "Query",
        st.session_state.pm_query,
        disabled=(not pubmed_check),
        key="pm_keyword",
        help="""This is the query sent for your search. You can type it manually if you prefer.
                              \n\nLeave blank and press Ctrl+Enter to reset query""",
    )

    # Change query manually
    if st.session_state.pm_query is not None:
        st.session_state.pm_query = pm_keyword
    if pm_keyword == "":
        st.session_state.pm_query = None

    # ELSEVIER
    st.markdown("***")
    col1, col2 = st.columns([1, 2])
    with col1:
        # Enable Scopus and ScienceDirect
        st.subheader("Elsevier")
        scopus_check = st.checkbox("Scopus", False, key="sc")
        scidir_check = st.checkbox("ScienceDirect", False, key="sd")
    with col2:
        # Number of articles
        num_scopus = st.select_slider(
            "Number of articles: ",
            options=[25, 5000],
            value=5000,
            disabled=(not scopus_check and not scidir_check),
            key="sc_num",
        )

    col1, col2, col3 = st.columns([2, 4, 1])
    with col1:
        # Tags
        select = st.selectbox(
            "Field", scopus.tags, disabled=(not scopus_check and not scidir_check)
        )

        if select in scopus.radios:
            # Tag subtype
            sc_tag = st.radio("Type", scopus.radios[select])
        else:
            sc_tag = select

    with col2:
        if sc_tag in scopus.selects:
            # Selection input
            sc_term = st.selectbox("Search term", scopus.selects[sc_tag])
            sc_term = scopus.selects[sc_tag][sc_term]

        elif sc_tag == "Date":
            # Date input
            col21, col22 = st.columns([1, 4])
            with col21:
                operator = st.selectbox(
                    "Operator", (" > ", " = ", " < "), label_visibility="hidden"
                )
            with col22:
                year = st.text_input("Year")
            sc_term = operator + year

        else:
            # Text input
            sc_term = st.text_input(
                "Search term",
                key="sc_term",
                disabled=(not scopus_check and not scidir_check),
            )

        # Filter
        if st.checkbox("Open access", disabled=(not scopus_check and not scidir_check)):
            if st.session_state.sc_query is None:
                st.session_state.sc_query = "OPENACCESS(1)"
            elif "OPENACCESS(1)" not in st.session_state.sc_query:
                st.session_state.sc_query += " AND OPENACCESS(1)"
        else:
            if st.session_state.sc_query == "OPENACCESS(1)":
                st.session_state.sc_query = None

    with col3:
        # Boolean operator
        boolean = st.selectbox(
            "Bool",
            ("AND", "OR", "NOT"),
            key="sc_bool",
            disabled=(not scopus_check and not scidir_check),
            label_visibility="hidden",
        )

        # Query constructor
        if st.button(
            "Add", disabled=(not scopus_check and not scidir_check), key="sc_add"
        ):
            if st.session_state.sc_query is not None:
                st.session_state.sc_query += f" {boolean} "

            if sc_tag == "Date":
                st.session_state.sc_query += f"PUBYEAR {sc_term}"
            elif sc_tag == "Reference year":
                st.session_state.sc_query += f"REFPUBYEAR IS {sc_term}"
            else:
                if st.session_state.sc_query is None:
                    st.session_state.sc_query = f"{scopus.field[sc_tag]}({sc_term})"
                else:
                    st.session_state.sc_query += f"{scopus.field[sc_tag]}({sc_term})"

            # Avoid boolean operator for ID fields
            if sc_tag in scopus.non_boolean:
                for bool in ["AND", "OR", "NOT"]:
                    if bool in st.session_state.sc_query:
                        st.session_state.boolean_error = True

    # Query
    sc_keyword = st.text_area(
        "Query",
        st.session_state.sc_query,
        disabled=(not scopus_check and not scidir_check),
        key="sc_keyword",
        help="""This is the query sent for your search. You can type it manually if you prefer.
                              \n\nLeave blank and press Ctrl+Enter to reset query
                              \n\nSearch tips: https://dev.elsevier.com/sc_search_tips.html""",
    )

    # Change query manually
    if st.session_state.sc_query is not None:
        st.session_state.sc_query = sc_keyword
    if sc_keyword == "":
        st.session_state.sc_query = None


    with st.expander("Scispacy"):
        st.write('See key elements of abstracts in a separated column of your dataframe using Scispacy')
        options = ['Gene or gene product', 'Cancer', 'Amino acid', 'Organ', 'Organism', 'Simple chemical']

        scispacy_param = set()
        for opt in options:
            if st.checkbox(f'{opt}'):
                scispacy_param.add(opt)

    # Return everything as a dictionary
    request = {
        "pm_keyword": pm_keyword,
        "sc_keyword": sc_keyword,
        "sd_keyword": sc_keyword,
        "pm_check": pubmed_check,
        "sc_check": scopus_check,
        "sd_check": scidir_check,
        "pm_num": num_pubmed,
        "sc_num": num_scopus,
        "sd_num": num_scopus,
        "scispacy_param": scispacy_param,
    }
    return request
