import streamlit as st
from auth import login, logout
from utils.session import init_session
from pages import home, recipes, ingredients, new_recipe


init_session()

# Handle login
if not st.session_state["authenticated"]:
    login()
else:
    logout()
    st.image("logo.png", width=600)

    # Route to the right page
    if st.session_state.page == "home":
        home.render()
    elif st.session_state.page == "recipes":
        recipes.render()
    elif st.session_state.page == "ingredients":
        ingredients.render()
    elif st.session_state.page == "new_recipe":
        new_recipe.render()
