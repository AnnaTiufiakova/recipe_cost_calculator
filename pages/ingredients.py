import streamlit as st
import pandas as pd
from utils.session import go_to
import os
import datetime

DATA_PATH = "data/item_master.csv"

def render():
    st.title("See all ingredients")

    if st.button("🔙 Go to home page"):
        go_to("home")
        st.rerun()

    # Add a new ingredient (moved up)
    st.markdown("---")
    with st.expander("➕ Add a new ingredient"):
        with st.form("add_ingredient_form"):
            def get_next_item_id():
                try:
                    df = pd.read_csv(DATA_PATH, encoding="latin1")
                    if "item_id" in df.columns and not df.empty:
                        return df["item_id"].max() + 1
                    else:
                        return 1
                except FileNotFoundError:
                    return 1

            item_id = get_next_item_id()
            name = st.text_input("Ingredient Name")
            is_subrecipe = st.selectbox("Is it a subrecipe?", ["", "yes", "no"])
            unit = st.selectbox("Unit", ["", "gramo", "ml", "unidad"])
            price_per_unit = st.number_input("Price per unit", min_value=0.0, format="%.2f")
            yield_pct = st.number_input("Yield %", min_value=0.0, max_value=100.0, format="%.2f")
            updated_at = datetime.date.today()

            submit_button = st.form_submit_button("Save")

        if submit_button:
            try:
                df = pd.read_csv(DATA_PATH, encoding="latin1")
                if name.lower() in df["name"].str.lower().values:
                    st.error(f"The ingredient '{name}' already exists.")
                else:
                    new_ingredient = {
                        "item_id": item_id,
                        "name": name,
                        "is_subrecipe": is_subrecipe,
                        "unit": unit,
                        "price_per_unit": price_per_unit,
                        "yield_pct": yield_pct,
                        "updated_at": updated_at
                    }
                    new_row = pd.DataFrame([new_ingredient])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(DATA_PATH, index=False, encoding="latin1")
                    st.success("Ingredient added successfully!")
            except Exception as e:
                st.error(f"An error occurred while saving the data: {e}")

    # Now load and display the ingredient table
    try:
        df = pd.read_csv(DATA_PATH, encoding="latin1")
        search_field = st.text_input("Search ingredient by name:")
        if search_field:
            filtered_df = df[df["name"].str.contains(search_field, case=False, na=False)]
        else:
            filtered_df = df
        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
    except FileNotFoundError:
        st.error("The file 'item_master.csv' was not found.")
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
