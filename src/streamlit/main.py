import sys
import streamlit as st

sys.path.insert(0, "src/utils/")
from extractor import Extractor
from search_input import basic, advanced


from search_input import basic, advanced


def main():
    mode = st.radio('Mode:', options=("Basic", "Advanced"))
        
    # BASIC INPUT
    if mode == "Basic":
        request = basic()
    
    # ADVANCED INPUT
    if mode == "Advanced":
        request = advanced()

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

# RESULTADOS
    if st.button("Submit"):
        st.sidebar.write("""## Extracting...""")

        # BUSCA PARA O PUBMED
        if request['pm_check']:
            with st.spinner(f'Searching articles with keyword "{request["pm_keyword"]}" in PubMed ({request["pm_num"]} articles) wait...'):
                data_tmp = Extractor(request["pm_keyword"], request["pm_num"]).pubmed()

                data = convert_df(data_tmp)

                st.sidebar.download_button(
                    label="Download PubMed data as CSV",
                    data=data,
                    file_name=f"pubmed_df.csv",
                    mime="text/csv",
                )

                st.success("PubMed Done!")

        # BUSCA PARA O Scopus
        if request["sc_check"]:
            with st.spinner(f'Searching articles with keyword "{request["sc_keyword"]}" in Scopus ({request["sc_num"]}) wait...'):
                data_tmp = Extractor(request["sc_keyword"], request["sc_num"]).scopus()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download Scopus data as CSV",
                    data=data,
                    file_name=f"scopus_df.csv",
                    mime="text/csv",
                )

                st.success("Scopus Done!")
        
        # BUSCA PARA O Science Direct
        if request["sd_check"]:
            with st.spinner(f'Searching articles with keyword "{request["sd_keyword"]}" in ScienceDirect ({request["sd_num"]}) wait...'):
                data_tmp = Extractor(request["sd_keyword"], request["sd_num"]).scidir()

                data = convert_df(data_tmp)

                st.sidebar.download_button(
                    label="Download ScienceDirect data as CSV",
                    data=data,
                    file_name=f"scidir_df.csv",
                    mime="text/csv",
                )

                st.success("ScienceDirect Done!")
        st.sidebar.success("Extraction complete!")


if __name__ == "__main__":
    main()
