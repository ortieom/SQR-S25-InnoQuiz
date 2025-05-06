import streamlit as st
import requests

def show_create_quiz_page():
    st.title("Create New Quiz")
    
    if not st.session_state.user:
        st.warning("Please login to create a quiz")
        return
    
    with st.form("create_quiz_form"):
        title = st.text_input("Quiz Title")
        theme = st.text_input("Theme")
        description = st.text_area("Description")
        
        submitted = st.form_submit_button("Create Quiz")
        
        if submitted:
            if not title or not theme:
                st.error("Please fill in all required fields")
                return
                
            try:
                response = requests.post(
                    "http://localhost:8000/quizzes/create",
                    json={
                        "title": title,
                        "theme": theme,
                        "description": description,
                        "creator_id": st.session_state.user["id"]
                    }
                )
                
                if response.status_code == 200:
                    quiz_id = response.json()["id"]
                    st.session_state.quiz_id = quiz_id
                    st.success(f"Quiz created successfully! Quiz ID: {quiz_id}")
                    st.info("Now you can add questions to your quiz")
                else:
                    st.error("Failed to create quiz")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server") 