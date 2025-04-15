import streamlit as st
import pandas as pd
import hashlib
from fpdf import FPDF


# Function to generate PDF
def generate_pdf(
    selected_recipe,
    ingredients,
    total_cost,
    error_margin_cost,
    preparation_cost,
    cost_per_gram,
    cost_per_portion,
    potential_price,
    cost_percentage,
    recipe_price,
):

    def calculate_column_widths(ingredients, headers):
        column_widths = []
        for header in headers:
            # Get the max width between the header and the longest item in each column
            max_width = max(
                pdf.get_string_width(header),  # width of the header
                max(
                    ingredients[header].apply(lambda x: pdf.get_string_width(str(x)))
                ),  # max width of the column data
            )
            # Adding some padding to the column width
            column_widths.append(max_width + 10)  # 10 is the padding
        return column_widths

    pdf = FPDF(orientation="L")
    pdf.add_page()
    pdf.image("logo_for_pdf.png", x=10, y=8, w=50)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(200, 10, txt=f"{selected_recipe.upper()}", ln=True, align="C")
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", "B", 12)
    headers = [
        "name",
        "initial_quantity",
        "final_quantity",
        "yield_pct",
        "unit",
        "price_per_unit",
        "cost",
    ]

    # Call the function to calculate column widths
    column_widths = calculate_column_widths(ingredients, headers)

    # Set column width for each header based on calculated widths
    for i, header in enumerate(headers):
        pdf.cell(column_widths[i], 10, header, border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", "", 12)
    for _, row in ingredients.iterrows():
        pdf.cell(column_widths[0], 9, str(row["name"]), border=1)
        pdf.cell(column_widths[1], 9, str(row["initial_quantity"]), border=1)
        pdf.cell(column_widths[2], 9, str(row["final_quantity"]), border=1)
        pdf.cell(column_widths[3], 9, str(row["yield_pct"]), border=1)
        pdf.cell(column_widths[4], 9, str(row["unit"]), border=1)
        pdf.cell(column_widths[5], 9, f"${row['price_per_unit']:.2f}", border=1)
        pdf.cell(column_widths[6], 9, f"${row['cost']:.2f}", border=1)
        pdf.ln()

    # Summary section
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 9, txt="Total Raw Material Cost:", ln=False)
    pdf.set_font("Arial", "", 12)
    pdf.cell(50, 9, txt=f"${total_cost:.2f}", ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 9, txt="Error Margin Cost:", ln=False)
    pdf.set_font("Arial", "", 12)
    pdf.cell(50, 9, txt=f"${error_margin_cost:.2f}", ln=True)

    if preparation_cost != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Total Preparation Cost:", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"${preparation_cost:.2f}", ln=True)

    if cost_per_gram != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Cost per Gram:", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"${cost_per_gram:.2f}", ln=True)

    if cost_per_portion != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Cost per Portion:", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"${cost_per_portion:.2f}", ln=True)

    if potential_price != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Potential Selling Price:", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"${potential_price:.2f}", ln=True)

    if cost_percentage != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Cost Percentage (Target: 35%):", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"{cost_percentage:.1f}%", ln=True)

    if recipe_price != 0:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 9, txt="Menu Price:", ln=False)
        pdf.set_font("Arial", "", 12)
        pdf.cell(50, 9, txt=f"${recipe_price:.2f}", ln=True)

    # Save to file
    pdf_output_path = f"{selected_recipe.replace(' ', '_').lower()}_recipe.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path


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

# Main app only for logged-in users
if st.session_state["authenticated"]:
    # Logout button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    st.image("logo.png", width=600)
    st.title("Standard Recipe Calculator 🍽️")

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
                # Default values if it's a sub-recipe
                cost_per_portion = 0
                potential_price = 0
                cost_percentage = 0
                recipe_price = 0
    else:
        st.info("Please select a recipe to proceed.")

    # Display results
    if selected_recipe != "-- Select recipe --" and selected_recipe != "":
        st.subheader("Ingredients & Cost Breakdown")
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

    # Add the "Generate PDF" button
    if selected_recipe != "-- Select recipe --" and selected_recipe != "":
        # Always show the "Generate PDF" button
        if st.button("Generate PDF"):
            pdf_output_path = generate_pdf(
                selected_recipe,
                ingredients,
                total_cost,
                error_margin_cost,
                preparation_cost,
                cost_per_gram,
                cost_per_portion,
                potential_price,
                cost_percentage,
                recipe_price,
            )

            # Make the file downloadable
            with open(pdf_output_path, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=pdf_output_path,
                    mime="application/pdf",
                )
