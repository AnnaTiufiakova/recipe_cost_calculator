import streamlit as st


def init_session():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "page" not in st.session_state:
        st.session_state["page"] = "home"


def go_to(page):
    st.session_state.page = page
