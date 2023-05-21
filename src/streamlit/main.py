import time

import streamlit as st

from utils.extractor import Extractor


def main():
    st.title("Systematic Review")
    st.write("""## Insert your keyword & choose database""")
    # email = st.text_input('To login tell me your email, please')

    # ADMIN_USERS = {
    #    'gratidutra@gmail.com',
    #    'test@localhost.com'
    # }

    # if st.button("Send"):

    #    if st.experimental_user.email in ADMIN_USERS:

    #        st.write("Welcome, ", email)

    #Aqui fica o campo onde escrevemos a palavra-chave. 
    #Embaixo desse podemos adicionar o número
    #de artigos que queremos

    keyword = st.sidebar.text_input("Keyword", "Cancer prostata")

    database_name = st.sidebar.selectbox(
        "Select Database", ("Pubmed", "Scopus", "Science Direct", "All")
    )

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    # BUSCA PARA O PUBMED
    if database_name == "Pubmed":
        if st.sidebar.button("Submit"):
            with st.spinner(
                f"Searching articles with keyword {keyword} in {database_name} wait..."
            ):
                #O número de artigos está fixo para 3 precisamos criar um botão para que o usuário
                #escolha e se não escolher deixar um default de 5k talvez
                
                data_tmp = Extractor(keyword, 200).pubmed()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download data as CSV",
                    data=data,
                    file_name=f"{database_name}_df.csv",
                    mime="text/csv",
                )

                st.success("Done!")
    # BUSCA PARA O Science Direct
    elif database_name == "Science Direct":
        if st.sidebar.button("Submit"):
            with st.spinner(
                f"Searching articles with keyword {keyword} in {database_name} wait..."
            ):
                data_tmp = Extractor(keyword, 5).scidir()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download data as CSV",
                    data=data,
                    file_name=f"{database_name}_df.csv",
                    mime="text/csv",
                )

                st.success("Done!")
    # BUSCA PARA O Scopus
    elif database_name == "Scopus":
        if st.sidebar.button("Submit"):
            with st.spinner(
                f"Searching articles with keyword {keyword} in {database_name} wait..."
            ):
                data_tmp = Extractor(keyword, 5).scopus()

                data = convert_df(data_tmp)

                st.download_button(
                    label="Download data as CSV",
                    data=data,
                    file_name=f"{database_name}_df.csv",
                    mime="text/csv",
                )

                st.success("Done!")
    # else:
    #    st.error("## O nooo!! your email don't is in us database")


if __name__ == "__main__":
    main()
