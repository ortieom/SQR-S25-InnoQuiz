import streamlit as st
from frontend.app.utils.api import create_quiz


def show_create_quiz_page():
    st.title("Create New Quiz")

    if not st.session_state.user:
        st.warning("Please login to create a quiz")
        return

    # Category options with their IDs
    categories = {
        "General Knowledge": 9,
        "Entertainment: Books": 10,
        "Entertainment: Film": 11,
        "Entertainment: Music": 12,
        "Entertainment: Music & Theatres": 13,
        "Entertainment: Television": 14,
        "Entertainment: Video Games": 15,
        "Entertainment: Board Games": 16,
        "Science & Nature": 17,
        "Science: Computers": 18,
        "Science: Mathematics": 19,
        "Mythology": 20,
        "Sports": 21,
        "Geography": 22,
        "History": 23,
        "Politics": 24,
        "Art": 25,
        "Celebrities": 26,
        "Animals": 27,
        "Vehicles": 28,
        "Entertainment: Comics": 29,
        "Science: Gadgets": 30,
        "Entertainment: Japanese Anime & Manga": 31,
        "Entertainment: Cartoons & Animations": 32
    }

    with st.form("create_quiz_form"):
        title = st.text_input("Quiz Title")
        category = st.selectbox("Category", options=list(categories.keys()))
        submitted = st.form_submit_button("Create Quiz")

    if submitted:
        if not title:
            st.error("Please fill in all required fields")
            return

        # Use our API utility to create the quiz
        quiz_data = create_quiz(title=title, category=str(categories[category]))

        if quiz_data:
            # Store the UUID as a string
            quiz_id = str(quiz_data.get("id"))
            st.session_state.quiz_id = quiz_id
            st.success(f"Quiz created successfully!")
            st.code(f"Quiz ID: {quiz_id}", language="text")
            st.info("Now you can add questions to your quiz")

    # Add Questions button outside the form
    if st.session_state.quiz_id:
        if st.button("Add Questions"):
            st.query_params.clear()
            st.query_params["page"] = "add_questions"
            st.rerun()
