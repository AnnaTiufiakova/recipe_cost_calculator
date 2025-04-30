import streamlit as st
from utils.session import go_to


def render():
    st.title("Add New Ingredient")
    if st.button("🔙 Go to home page"):
        go_to("home")
        st.rerun()
