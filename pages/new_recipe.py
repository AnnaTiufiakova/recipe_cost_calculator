import streamlit as st
import pandas as pd
import datetime
from utils.session import go_to

DATA_PATH1 ="data/recipe.csv"
DATA_PATH2 ="data/recipe_ingredient.csv"
DATA_PATH3 ="data/item_master.csv"

def render():
    st.title("Add New Recipe")
    if st.button("🔙 Go to home page"):
        go_to("home")
        st.rerun()

    def load_csv():
        recipe = pd.read_csv(DATA_PATH1, encoding="latin1", parse_dates=["updated_at"])
        recipe_ingredient = pd.read_csv(DATA_PATH2, encoding="latin1")
        item_master = pd.read_csv(DATA_PATH3, encoding="latin1")
        return recipe, recipe_ingredient, item_master
    recipe, recipe_ingredient, item_master = load_csv()

    if "ingredient_rows" not in st.session_state:
        st.session_state.ingredient_rows = [{}]  # start with one blank row

    with st.expander("➕ Add a new recipe"):
        with st.form("add_new_recipe"):
            recipe_name = st.text_input("Enter recipe name")
            is_subrecipe = st.selectbox("Is it subrecipe", ["", "yes", "no"] )
            error_margin = st.selectbox("Select error margin", ["", 0.03] )

            # Multiple ingredient inputs
            for i, row in enumerate(st.session_state.ingredient_rows):
                cols = st.columns([2, 1])
                row["ingredient_name"] = cols[0].selectbox(
                    f"Ingredient {i+1}",
                    [""] + item_master["name"].tolist(),
                    key=f"ingredient_{i}"
                )
                row["initial_quantity"] = cols[1].number_input(
                    "Initial quantity",
                    min_value=0.0,
                    format="%.2f",
                    key=f"initial_quantity_{i}"
                )
                st.session_state.ingredient_rows[i] = row  # update session

            # Add more rows
            if st.form_submit_button("➕ Add another ingredient"):
                st.session_state.ingredient_rows.append({})
                st.rerun()

            submit_button = st.form_submit_button("Save")

    # Handle Save logic outside form
    if submit_button and recipe_name:
        recipe_name = recipe_name.strip()
        error_margin = float(error_margin) if error_margin else None
        if recipe_name.lower() in recipe["name"].str.lower().str.strip().tolist():
            st.error(f"The ingredient '{recipe_name}' already exists.")
        else:
            recipe_id = recipe_ingredient["recipe_id"].max() + 1 if not recipe_ingredient.empty else 1
            updated_at = datetime.date.today()

            # Add recipe row
            new_recipe = pd.DataFrame([{
                "id": recipe_id,
                "name": recipe_name,
                "is_subrecipe": is_subrecipe,
                "error_margin": error_margin,
                "updated_at": pd.to_datetime(updated_at)
            }])
            recipe = pd.concat([recipe, new_recipe], ignore_index=True)
            recipe.to_csv(DATA_PATH1, index=False, encoding="latin1")

            # Add all ingredients
            new_ingredients = []
            for row in st.session_state.ingredient_rows:
                if row.get("ingredient_name") and row.get("initial_quantity", 0) > 0:
                    item_id = item_master[item_master["name"] == row["ingredient_name"]]["item_id"].values[0]
                    new_ingredients.append({
                        "recipe_id": recipe_id,
                        "item_id": item_id,
                        "initial_quantity": row["initial_quantity"]
                    })

            recipe_ingredient = pd.concat([recipe_ingredient, pd.DataFrame(new_ingredients)], ignore_index=True)
            recipe_ingredient.to_csv(DATA_PATH2, index=False, encoding="latin1")

            # Clear form state
            st.session_state.ingredient_rows = [{}]
            st.success("✅ Recipe with ingredients added successfully!")