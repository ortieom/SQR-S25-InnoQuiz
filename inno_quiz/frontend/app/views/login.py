import streamlit as st
from frontend.app.utils.api import is_backend_available, register_user, login_user

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
                
            result = login_user(username, password)
            if result:
                # Create a user session object with username and token
                user_info = {
                    "username": username,
                    "id": None,  # We don't have the ID from the token response
                    "token": result.get("access_token")
                }
                st.session_state.user = user_info
                st.query_params.clear()
                st.query_params["page"] = "create_quiz"
                st.success("Logged in successfully!")
                st.rerun()
    
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
                
            result = register_user(new_username, new_password)
            if result:
                st.success("Registration successful! Please login.") 