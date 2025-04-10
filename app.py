import streamlit as st
import pandas as pd
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# credentials
users = {"anna": hash_password("1234"), "admin": hash_password("admin123")}

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Login form
if not st.session_state["authenticated"]:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == hash_password(password):
            st.session_state["authenticated"] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# 👇 Main app only for logged-in users
if st.session_state["authenticated"]:

    st.title("Standard Recipe Calculator 🍽️")

    # Logout button
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    @st.cache_data
    def load_data():
        item_master = pd.read_csv("data/item_master.csv", encoding="latin1")
        item_price_history = pd.read_csv(
            "data/item_price_history.csv", encoding="latin1", parse_dates=["start_date"]
        )
        menu = pd.read_csv("data/menu.csv", encoding="latin1")
        recipe = pd.read_csv("data/recipe.csv", encoding="latin1")
        recipe_ingredient = pd.read_csv("data/recipe_ingredient.csv", encoding="latin1")
        return item_master, item_price_history, menu, recipe, recipe_ingredient

    item_master, item_price_history, menu, recipe, recipe_ingredient = load_data()

    # Select type of recipe
    st.markdown("### Select type of recipe")
    select_recipe_type = st.selectbox(
        "", ["-- Select type --", "Dish recipe", "Sub-recipe"]
    )
    # Filter recipes based on type
    if select_recipe_type == "Dish recipe":
        filtered_recipes = recipe[recipe["is_subrecipe"] == "no"]["name"].sort_values()
    elif select_recipe_type == "Sub-recipe":
        filtered_recipes = recipe[recipe["is_subrecipe"] == "yes"]["name"].sort_values()
    else:
        filtered_recipes = []

    # Select recipe from filtered list
    st.markdown("### Choose a Recipe")
    if len(filtered_recipes) > 0:
        selected_recipe = st.selectbox(
            "", ["-- Select recipe --"] + list(filtered_recipes)
        )
    else:
        selected_recipe = st.selectbox("", ["-- Select recipe --"])

    # Get recipe ID and ingredients
    if selected_recipe != "-- Select a recipe --" and selected_recipe != "":
        recipe_row = recipe.loc[recipe["name"] == selected_recipe]
        if not recipe_row.empty:
            recipe_id = recipe_row["id"].values[0]
            # Get ingredients based on recipe_id
            ingredients = recipe_ingredient[recipe_ingredient["recipe_id"] == recipe_id]
            # Add item names by joining with item_master
            ingredients = ingredients.merge(item_master, on="item_id", how="left")

            # Get the latest price per item
            def get_latest_price(price_df):
                latest = (
                    price_df.sort_values("start_date", ascending=False)
                    .drop_duplicates("item_id")
                    .set_index("item_id")["price_per_unit"]
                )
                return latest

            latest_prices = get_latest_price(item_price_history)

            # Map prices to ingredients
            ingredients["price_per_unit"] = ingredients["item_id"].map(latest_prices)

            # Calculate final quantity
            ingredients["final_quantity"] = (
                ingredients["initial_quantity"] * ingredients["yield_pct"] / 100
            )

            # Calculate total raw material cost
            ingredients["cost"] = (
                ingredients["initial_quantity"] * ingredients["price_per_unit"]
            )
            total_cost = ingredients["cost"].sum()

            # Calculate error margin cost
            error_margin = recipe.loc[
                recipe["name"] == selected_recipe, "error_margin"
            ].values[0]
            error_margin_cost = total_cost * error_margin

            # Calculate total preparation cost
            preparation_cost = total_cost + error_margin_cost

            # Calculate price per gram
            is_subrecipe = recipe.loc[
                recipe["name"] == selected_recipe, "is_subrecipe"
            ].values[0]
            if is_subrecipe == "yes" and selected_recipe == "alas x 1":
                cost_per_gram = preparation_cost / 18
            else:
                cost_per_gram = preparation_cost / ingredients["final_quantity"].sum()

            # Calculate cost per portion
            if is_subrecipe == "no":
                cost_per_portion = preparation_cost
                # Calculate Potential Selling Price and actual price
                potential_price = (100 * cost_per_portion) / 35

                # Fetch prices from menu
                recipe_price = menu.loc[
                    menu["name_of_dish"] == selected_recipe, "price"
                ].values
                if recipe_price.size > 0:
                    recipe_price = recipe_price[0]
                    # Calculate Cost Percentage (established 35%)
                    cost_percentage = round((cost_per_portion / recipe_price) * 100, 1)
                else:
                    recipe_price = 0
                    cost_percentage = 0
    else:
        st.info("Please select a recipe to proceed.")

    # Display results
    st.subheader("Ingredients & Cost Breakdown")
    if "ingredients" in locals():  # Ensure ingredients exists before displaying
        st.dataframe(
            ingredients[
                [
                    "name",
                    "initial_quantity",
                    "final_quantity",
                    "yield_pct",
                    "unit",
                    "price_per_unit",
                    "cost",
                ]
            ]
        )

        st.subheader("Total Raw Material Cost")
        st.success(f"${total_cost:.2f}")
        st.subheader("Error margin cost")
        st.success(f"${error_margin_cost:.2f}")
        st.subheader("Total preparation cost")
        st.success(f"${preparation_cost:.2f}")

        # Only show cost per gram if it's a subrecipe
        if is_subrecipe == "yes" and selected_recipe == "alas x 1":
            st.subheader("Cost per Unidad")
            st.success(f"${cost_per_gram:.2f}")
        else:
            st.subheader("Cost per Gram")
            st.success(f"${cost_per_gram:.2f}")

        if is_subrecipe == "no":
            st.subheader("Cost per Portion")
            st.success(f"${cost_per_portion:.2f}")
            st.subheader("Potential Selling price")
            st.success(f"${potential_price:.2f}")
            st.subheader("Cost percentage (established 35%)")
            st.success(f"{cost_percentage:.1f}%")
            st.subheader("Menu price")
            st.success(f"${recipe_price:.2f}")
