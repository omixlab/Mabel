import streamlit as st

import utils.globals as globals
from utils import extractor
from utils.streamlit import basic_search
from utils.streamlit import advanced_search
from utils.streamlit import unify_dfs
from utils.streamlit import spacy


def main():
    st.title("Systematic Review")
    mode = st.radio("Mode:", options=("Basic", "Advanced"))

    # BASIC INPUT
    if mode == "Basic":
        request = basic_search.basic()

    # ADVANCED INPUT
    if mode == "Advanced":
        request = advanced_search.advanced()

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    # RESULTADOS
    if "boolean_error" in st.session_state:  # Avoid submitting with error
        st.error("Boolean operators might not work within these fields")

    if st.button("Submit"):
        st.sidebar.write("""## Extracting...""")
        st.session_state.dataframes = {}
        st.session_state.unify_parameters = {}

        globals.stop_extraction = False
        if st.button("Stop Extraction"):
            globals.stop_extraction = True

        # BUSCA PARA O PUBMED
        if request["pm_check"]:
            with st.spinner(
                f'Searching articles with keyword "{request["pm_keyword"]}" in PubMed ({request["pm_num"]} articles) wait...'
            ):
                data_tmp = extractor.Extractor(
                    request["pm_keyword"], request["pm_num"]
                ).pubmed()

                if not globals.stop_extraction:
                    st.session_state.dataframes["pubmed_df"] = data_tmp
                    st.session_state.unify_parameters["pm"] = data_tmp
                    st.success("PubMed Done!")
                else:
                    st.error("Stopped")

        # BUSCA PARA O Scopus
        if request["sc_check"]:
            with st.spinner(
                f'Searching articles with keyword "{request["sc_keyword"]}" in Scopus ({request["sc_num"]}) wait...'
            ):
                data_tmp = extractor.Extractor(
                    request["sc_keyword"], request["sc_num"]
                ).scopus()

                if not globals.stop_extraction:
                    st.session_state.dataframes["scopus_df"] = data_tmp
                    st.session_state.unify_parameters["sc"] = data_tmp
                    st.success("Scopus Done!")
                else:
                    st.error("Stopped")

        # BUSCA PARA O Science Direct
        if request["sd_check"]:
            with st.spinner(
                f'Searching articles with keyword "{request["sd_keyword"]}" in ScienceDirect ({request["sd_num"]}) wait...'
            ):
                data_tmp = extractor.Extractor(
                    request["sd_keyword"], request["sd_num"]
                ).scidir()

                if not globals.stop_extraction:
                    st.session_state.dataframes["scidir_df"] = data_tmp
                    st.session_state.unify_parameters["sd"] = data_tmp
                    st.success("ScienceDirect Done!")
                else:
                    st.error("Stopped")


        # UNIFICA AS TABELAS
        unified_df = unify_dfs.unify(st.session_state.unify_parameters)

        # SCISPACY
        if request["scispacy_param"]:
            with st.spinner(f'Analyzing with ScispaCy'):
                unified_df = spacy.scispacy(unified_df, request["scispacy_param"])

        st.session_state.dataframes["unified_df"] = unified_df


    # Renderiza os downloads
    if not globals.stop_extraction:
        if hasattr(st.session_state, "dataframes"):
            st.sidebar.success("Extraction complete!")

            st.sidebar.write("Raw data")
            for df in st.session_state.dataframes:
                if df == "unified_df":
                    st.sidebar.markdown("***")
                    st.sidebar.write("Unified results")
                st.sidebar.download_button(
                    label=f"Download {df} as CSV",
                    data=convert_df(st.session_state.dataframes[df]),
                    file_name=f"{df}.csv",
                    mime="text/csv",
                )

            # Show unified dataframes
            st.dataframe(st.session_state.dataframes["unified_df"])

    else:
        st.sidebar.error("Extraction stopped by the user")


if __name__ == "__main__":
    main()
