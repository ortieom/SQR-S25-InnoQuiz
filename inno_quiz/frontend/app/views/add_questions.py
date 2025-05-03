import streamlit as st
import requests
from typing import List, Dict

def show_add_questions_page():
    st.title("Add Questions to Quiz")
    
    if not st.session_state.user:
        st.warning("Please login to add questions")
        return
        
    if not st.session_state.quiz_id:
        st.warning("Please create a quiz first")
        return
    
    # Get quiz info
    try:
        quiz_response = requests.get(f"http://localhost:8000/quizzes/{st.session_state.quiz_id}")
        if quiz_response.status_code == 200:
            quiz = quiz_response.json()
            st.subheader(f"Adding questions to: {quiz['title']}")
            st.write(f"Theme: {quiz['theme']}")
            st.write(f"Description: {quiz['description']}")
        else:
            st.error("Could not load quiz information")
            return
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server")
        return
    
    # Manual question addition
    st.subheader("Add Question")
    with st.form("add_question_form"):
        question_text = st.text_area("Question")
        options = st.text_input("Options (comma-separated)")
        correct_answer = st.text_input("Correct Answer")
        
        submitted = st.form_submit_button("Add Question")
        
        if submitted:
            if not question_text or not options or not correct_answer:
                st.error("Please fill in all fields")
                return
                
            try:
                response = requests.post(
                    f"http://localhost:8000/quizzes/{st.session_state.quiz_id}/questions",
                    json={
                        "question_text": question_text,
                        "options": [opt.strip() for opt in options.split(",")],
                        "correct_answer": correct_answer
                    }
                )
                
                if response.status_code == 200:
                    st.success("Question added successfully!")
                else:
                    st.error("Failed to add question")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")
    
    # Generate questions from Open Trivia DB
    st.subheader("Generate Questions")
    with st.form("generate_questions_form"):
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
        with col2:
            category = st.selectbox(
                "Category",
                ["general", "science", "history", "geography", "entertainment", "sports"]
            )
        
        difficulty = st.select_slider(
            "Difficulty",
            options=["easy", "medium", "hard"],
            value="medium"
        )
        
        if st.form_submit_button("Generate Questions"):
            try:
                response = requests.post(
                    f"http://localhost:8000/quizzes/{st.session_state.quiz_id}/generate",
                    json={
                        "num_questions": num_questions,
                        "category": category,
                        "difficulty": difficulty
                    }
                )
                
                if response.status_code == 200:
                    st.success(f"Generated {num_questions} questions successfully!")
                else:
                    st.error("Failed to generate questions")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")
    
    # Display existing questions
    st.subheader("Existing Questions")
    try:
        response = requests.get(f"http://localhost:8000/quizzes/{st.session_state.quiz_id}/questions")
        if response.status_code == 200:
            questions = response.json()
            for i, question in enumerate(questions, 1):
                with st.expander(f"Question {i}"):
                    st.write(question["question_text"])
                    st.write("Options:", ", ".join(question["options"]))
                    st.write("Correct Answer:", question["correct_answer"])
                    
                    if st.button(f"Delete Question {i}"):
                        try:
                            delete_response = requests.delete(
                                f"http://localhost:8000/quizzes/{st.session_state.quiz_id}/questions/{question['id']}"
                            )
                            if delete_response.status_code == 200:
                                st.success("Question deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete question")
                        except requests.exceptions.RequestException:
                            st.error("Could not connect to the server")
        else:
            st.info("No questions added yet")
    except requests.exceptions.RequestException:
        st.error("Could not connect to the server") 