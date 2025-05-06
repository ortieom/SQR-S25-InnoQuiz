import streamlit as st
import requests
from typing import Optional

def show_login_page():
    st.title("Login / Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if not username or not password:
                st.error("Please fill in all fields")
                return
                
            try:
                response = requests.post(
                    "http://localhost:8000/users/login",
                    json={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    st.session_state.user = response.json()
                    st.query_params.clear()
                    st.query_params["page"] = "create_quiz"
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
        
        if st.button("Register", key="register_button"):
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill in all fields")
                return
                
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
                
            try:
                response = requests.post(
                    "http://localhost:8000/users/create",
                    json={"username": new_username, "password": new_password}
                )
                
                if response.status_code == 200:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server") 