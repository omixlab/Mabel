import streamlit as st
import time


def main():

    st.title("Systematic Review")
    st.write("""## Insert your keyword & chose database""")
    # email = st.text_input('To login tell me your email, please')

    # ADMIN_USERS = {
    #    'gratidutra@gmail.com',
    #    'test@localhost.com'
    # }

    # if st.button("Send"):

    #    if st.experimental_user.email in ADMIN_USERS:

    #        st.write("Welcome, ", email)

    keyword = st.sidebar.text_input("Keyword", "Cancer prostata")

    database_name = st.sidebar.selectbox(
        "Select Database", ("Pubmed", "Scopus", "Science Direct", "All")
    )

    if st.sidebar.button("Submit"):
        with st.spinner(
            f"Searching articles with keyword {keyword} in {database_name} wait..."
        ):
            time.sleep(2.5)

            st.download_button(
                label="Download data as CSV",
                data="-",
                file_name="large_df.csv",
                mime="text/csv",
            )

            st.success("Done!")
    # else:
    #    st.error("## O nooo!! your email don't is in us database")


if __name__ == "__main__":
    main()
