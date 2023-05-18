import time

import streamlit as st

from extractor import Extractor


def main():
    st.title("Systematic Review")
    mode = st.radio('Mode:', options=("Basic", "Advanced"))
        
    # email = st.text_input('To login tell me your email, please')
    # ADMIN_USERS = {
    #    'gratidutra@gmail.com',
    #    'test@localhost.com'
    # }

    # if st.button("Send"):
    #    if st.experimental_user.email in ADMIN_USERS:
    #        st.write("Welcome, ", email)


    # BASIC
    if mode is "Basic":
        keyword = st.text_input("Search term")

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

        @st.cache_data
        def convert_df(df):
            return df.to_csv().encode("utf-8")
    
    # ADVANCED
    if mode is "Advanced":
        # PubMed
        col1, col2 = st.columns([1,2])
        with col1:
            st.subheader('PubMed')
            pubmed_check = st.checkbox('Enabled', False, key='p')
        with col2:
            articles_range = [1, 5, 10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
            num_pubmed = st.select_slider('Number of articles: ', options=articles_range, value=5000, disabled=(not pubmed_check), key='p_num')

        
        st.markdown('***')
        # Scopus
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
        

# RESULTADOS
    if st.button("Submit"):
        st.sidebar.write("""## Extracting...""")

        # BUSCA PARA O PUBMED
        if pubmed_check:
            with st.spinner(f'Searching articles with keyword "{keyword}" in PubMed ({num_pubmed}) wait...'):
                data_tmp = Extractor(keyword, num_pubmed).pubmed()

                data = convert_df(data_tmp)

                st.sidebar.download_button(
                    label="Download PubMed data as CSV",
                    data=data,
                    file_name=f"pubmed_df.csv",
                    mime="text/csv",
                )

                st.success("PubMed Done!")

        # BUSCA PARA O Scopus
        if scopus_check:
            with st.spinner(f'Searching articles with keyword "{keyword}" in Scopus ({num_scopus}) wait...'):
                data_tmp = Extractor(keyword, num_scopus).scopus()

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
                data_tmp = Extractor(keyword, num_scidir).scidir()

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
