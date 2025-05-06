import streamlit as st
import requests
from typing import Optional
from frontend.app.utils.api import is_backend_available

def show_login_page():
    st.title("Login / Register")
    
    # Check if backend is available
    if not is_backend_available():
        st.error("Backend server is not running. Please start the backend server and try again.")
        # Display helpful instructions
        with st.expander("How to start the backend server"):
            st.code("""
cd inno_quiz
SECRET_KEY=your_secret_key_here poetry run uvicorn backend.main:app --reload
            """)
        return
    
    # Create tabs
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    # Login tab
    with login_tab:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if not username or not password:
                st.error("Please fill in all fields")
                return
                
            try:
                # Use form data instead of JSON for login
                response = requests.post(
                    "http://localhost:8000/users/login",
                    data={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Create a user session object with username and token
                    user_info = {
                        "username": username,
                        "id": None,  # We don't have the ID from the token response
                        "token": data.get("access_token")
                    }
                    st.session_state.user = user_info
                    st.query_params.clear()
                    st.query_params["page"] = "create_quiz"
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    error_detail = "Incorrect username or password"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_detail = error_data["detail"]
                    except:
                        pass
                    st.error(f"Login failed: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the server: Connection error")
            except Exception as e:
                st.error(f"Could not connect to the server: {str(e)}")
    
    # Register tab
    with register_tab:
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
                # Continue using JSON for registration as expected by the API
                response = requests.post(
                    "http://localhost:8000/users/create",
                    json={"username": new_username, "password": new_password}
                )
                
                if response.status_code in [200, 201]:
                    st.success("Registration successful! Please login.")
                else:
                    error_detail = "Registration failed"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_detail = error_data["detail"]
                    except:
                        pass
                    st.error(f"Registration failed: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the server: Connection error")
            except Exception as e:
                st.error(f"Could not connect to the server: {str(e)}") 