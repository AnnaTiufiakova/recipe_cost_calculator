import streamlit as st
import pandas as pd
from utils.session import go_to


def render():
    st.title("See all ingredients")
    if st.button("🔙 Go to home page"):
        go_to("home")
        st.rerun()

    # Load csv data
    try:
        df = pd.read_csv("data/item_master.csv", encoding="latin1")
        # Searching fiel
        search_field = st.text_input("Search ingredient by name:")
        if search_field:
            filtered_df = df[
                df["name"].str.contains(search_field, case=False, na=False)
            ]
        else:
            filtered_df = df
        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
    except FileNotFoundError:
        st.error("The file 'item_master.csv' was not found.")
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
