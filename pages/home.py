import streamlit as st
from utils.session import go_to


def render():
    st.title("Standard Recipe Calculator 🍽️")
    st.subheader("Content")

    if st.button("📋 View All Recipes"):
        go_to("recipes")
        st.rerun()
    if st.button("🔍 See Ingredients"):
        go_to("ingredients")
        st.rerun()
    if st.button("➕ Add New Recipe"):
        go_to("new_recipe")
        st.rerun()
    if st.button("⚖️ Quick Cost Estimator"):
        go_to("quick_cost_estimator")
        st.rerun()
