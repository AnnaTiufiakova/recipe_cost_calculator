import streamlit as st
import pandas as pd
from utils.session import go_to


def render():
    st.title("Quick Cost Estimator")
    if st.button("🔙 Go to home page"):
        go_to("home")
        st.rerun()

    if "estimator_rows" not in st.session_state:
        st.session_state.estimator_rows = [{}]

    with st.form("quick_cost_estimator"):
        # Cost percentage (established 35%) , error margin
        type_of_recipe = st.selectbox(
            "Select type of recipe", ["", "dish recipe", "sub-recipe"], index=0
        )
        cost_pct = st.number_input("Enter target cost percentage", min_value=0.0)
        error_margin = st.number_input("Enter error margin", min_value=0.0)
        for i, row in enumerate(st.session_state.estimator_rows):
            cols = st.columns([2, 1, 1, 1, 1, 1])
            row["ingredient_name"] = cols[0].text_input(
                f"Ingredient {i+1}", key=f"name_{i}"
            )
            row["quantity"] = cols[1].number_input("Qty", min_value=0.0, key=f"qty_{i}")
            row["yield_pct"] = cols[2].number_input(
                "Yield %", min_value=0.0, max_value=100.0, key=f"yield_{i}"
            )
            row["units"] = cols[3].selectbox(
                "Units", ["", "gr", "kg", "ml", "litre", "unit"], key=f"units_{i}"
            )
            row["unit_price"] = cols[4].number_input(
                "Price x unit", min_value=0.0, key=f"price_{i}"
            )

            cost = (0.01 * row.get("quantity", 0) * row.get("yield_pct", 0)) * row.get(
                "unit_price", 0
            )
            cols[5].write("Cost")
            cols[5].write(f"${cost:.2f}")
            row["cost"] = cost

            st.session_state.estimator_rows[i] = row

        if st.form_submit_button("➕ Add another row"):
            st.session_state.estimator_rows.append({})
            st.rerun()

        calculate = st.form_submit_button("Calculate")

    # Calculations 
    
        total = 0
        total_raw_cost = 0
        error_margin_cost = 0
        total_prepar_cost = 0
        cost_per_gram = 0
        cost_portion = 0
        potential_price = 0
        total_yield_qty = 0
        for row in st.session_state.estimator_rows:
            qty = row.get("quantity", 0)
            yield_pct = row.get("yield_pct", 0)
            price = row.get("unit_price", 0)
            cost = (0.01 * qty * yield_pct) * price
            total += cost

            # shared calculations
        if calculate:    
            total_raw_cost += total
            total_yield_qty += qty * (yield_pct / 100)
            error_margin_cost += (total * error_margin)/100
            total_prepar_cost += total + error_margin_cost
            cost_per_gram += (total_prepar_cost / total_yield_qty if total_yield_qty > 0 else 0)

            st.write(f"Total Raw Material Cost: ${total_raw_cost:.2f}")
            st.write(f"Error Margin Cost: ${error_margin_cost:.2f}")
            st.write(f"Total Preparation Cost: ${total_prepar_cost:.2f}")
            st.write(f"Cost per Gram: ${cost_per_gram:.2f}")

            if type_of_recipe == "dish recipe":
                cost_portion += total_prepar_cost
                potential_price += (100 * cost_portion) / yield_pct
                st.write(f"Cost per Portion: ${cost_portion:.2f}")
                st.write(f"Potential Selling price: ${potential_price: .2f}")

