import streamlit as st
import hashlib

users = {
    "anna": hashlib.sha256("1234".encode()).hexdigest(),
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login():
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


def logout():
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()
