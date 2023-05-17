import time

import streamlit as st

from extractor import Extractor


def main():
    st.title("Systematic Review")
        
    # email = st.text_input('To login tell me your email, please')

    # ADMIN_USERS = {
    #    'gratidutra@gmail.com',
    #    'test@localhost.com'
    # }

    # if st.button("Send"):

    #    if st.experimental_user.email in ADMIN_USERS:

    #        st.write("Welcome, ", email)


    keyword = st.sidebar.text_input("Keyword")

    st.sidebar.write('Select your desired databases')
    articles_range = [1, 5, 10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    
    pubmed_check = st.sidebar.checkbox('PubMed', True)
    if pubmed_check:
        num_pubmed = st.sidebar.select_slider('Number of PubMed articles: ', options=articles_range, value=5000)

    scopus_check = st.sidebar.checkbox('Scopus', True)
    if scopus_check:
        num_scopus = st.sidebar.select_slider('Number of Scopus articles: ', options=articles_range, value=5000)

    scidir_check = st.sidebar.checkbox('ScienceDirect', True)
    if scidir_check:
        num_scidir = st.sidebar.select_slider('Number of ScienceDirect articles: ', options=articles_range, value=5000)

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    if st.sidebar.button("Submit"):
        st.write("""## Extracting, please wait""")
        # BUSCA PARA O PUBMED
        if pubmed_check:
            with st.spinner(f'Searching articles with keyword "{keyword}" in PubMed ({num_pubmed}) wait...'):
                data_tmp = Extractor(keyword, 3).pubmed()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download PubMed data as CSV",
                    data=data,
                    file_name=f"pubmed_df.csv",
                    mime="text/csv",
                )

                st.success("PubMed Done!")

        # BUSCA PARA O Scopus
        if scopus_check:
            with st.spinner(f'Searching articles with keyword "{keyword}" in Scopus ({num_scopus}) wait...'):
                data_tmp = Extractor(keyword, 3).scopus()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download Scopus data as CSV",
                    data=data,
                    file_name=f"scopus_df.csv",
                    mime="text/csv",
                )

                st.success("Scopus Done!")
        
        # BUSCA PARA O Science Direct
        if scidir_check:
            with st.spinner(f'Searching articles with keyword "{keyword}" in ScienceDirect ({num_scidir}) wait...'):
                data_tmp = Extractor(keyword, 3).scidir()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download ScienceDirect data as CSV",
                    data=data,
                    file_name=f"scidir_df.csv",
                    mime="text/csv",
                )

                st.success("ScienceDirect Done!")

    else:
        st.write("""## Insert your keyword & choose database""")



if __name__ == "__main__":
    main()
