import streamlit as st
from frontend.app.utils.api import create_quiz

def show_create_quiz_page():
    st.title("Create New Quiz")
    
    if not st.session_state.user:
        st.warning("Please login to create a quiz")
        return
    
    with st.form("create_quiz_form"):
        title = st.text_input("Quiz Title")
        category = st.text_input("Category")
        
        submitted = st.form_submit_button("Create Quiz")
        
        if submitted:
            if not title or not category:
                st.error("Please fill in all required fields")
                return
                
            # Use our API utility to create the quiz
            quiz_data = create_quiz(title=title, category=category)
            
            if quiz_data:
                quiz_id = quiz_data.get("id")
                st.session_state.quiz_id = quiz_id
                st.success(f"Quiz created successfully! Quiz ID: {quiz_id}")
                st.info("Now you can add questions to your quiz")
                
                # Automatically navigate to add questions page
                if st.button("Add Questions"):
                    st.query_params.clear()
                    st.query_params["page"] = "add_questions"
                    st.rerun() 