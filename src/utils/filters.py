import streamlit as st


def filter():
    if "selected_filters" not in st.session_state:
        st.session_state.selected_filters = []

    with st.expander("Filters", expanded=False):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Availability", "Type", "Age", "Language", "Others"]
        )
        with tab1:
            filters1 = ["Abstract", "Free full text", "Full text"]
            for filter in filters1:
                if st.checkbox(filter):
                    st.session_state.selected_filters.append(filter)

    return


dict = {"Abstract": "fha", "Free full text": "ffrtf", "Full text": "fft"}
