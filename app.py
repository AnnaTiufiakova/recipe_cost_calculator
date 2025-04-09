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

    st.title("Welcome to Recipe Cost Calculator! 🍽️")

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

    # Step 1: Choose a recipe
    selected_recipe = st.selectbox("Choose a recipe", recipe["name"].unique())

    # Step 2: Get recipe ID
    recipe_id = recipe.loc[recipe["name"] == selected_recipe, "id"].values[0]

    # Step 3: Get ingredients for that recipe
    ingredients = recipe_ingredient[recipe_ingredient["recipe_id"] == recipe_id]

    # Step 4: Add item names by joining with item_master
    ingredients = ingredients.merge(item_master, on="item_id", how="left")

    # Step 5: Get the latest price per item
    def get_latest_price(price_df):
        latest = (
            price_df.sort_values("start_date", ascending=False)
            .drop_duplicates("item_id")
            .set_index("item_id")["price_per_unit"]
        )
        return latest

    latest_prices = get_latest_price(item_price_history)

    # Step 6: Map prices to ingredients
    ingredients["price_per_unit"] = ingredients["item_id"].map(latest_prices)

    # Step 7: Calculate cost per ingredient
    ingredients["cost"] = (
        ingredients["initial_quantity"] * ingredients["price_per_unit"]
    )
    total_cost = ingredients["cost"].sum()

    # Step 8: Display results
    st.subheader("Ingredients & Cost Breakdown")
    st.dataframe(
        ingredients[["name", "initial_quantity", "unit", "price_per_unit", "cost"]]
    )

    st.subheader("Total Recipe Cost")
    st.success(f"${total_cost:.2f}")
