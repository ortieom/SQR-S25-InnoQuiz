import streamlit as st
from typing import List, Dict, Optional
from frontend.app.utils.api import get_quiz_info, add_question, load_external_questions, get_quiz_questions, submit_quiz


def show_add_questions_page():
    st.title("Add Questions to Quiz")

    if not st.session_state.user:
        st.warning("Please login to add questions")
        return

    if not st.session_state.quiz_id:
        st.warning("Please create a quiz first")
        return

    # Display quiz ID
    st.code(f"Quiz ID: {st.session_state.quiz_id}", language="text")

    # Get quiz info using our API utility
    quiz = get_quiz_info(st.session_state.quiz_id)
    if not quiz:
        return

    st.subheader(f"Adding questions to: {quiz['name']}")
    st.write(f"Category: {quiz.get('category', 'N/A')}")

    # Manual question addition
    st.subheader("Add Question")
    with st.form("add_question_form"):
        question_text = st.text_area("Question")

        # Allow multiple options with correctness flags
        st.write("Add Answer Options:")
        options = []
        correct_options = []

        for i in range(4):  # 4 options by default
            col1, col2 = st.columns([4, 1])
            with col1:
                option = st.text_input(f"Option {i + 1}", key=f"option_{i}")
            with col2:
                is_correct = st.checkbox("Correct", key=f"correct_{i}")

            if option:
                options.append(option)
                if is_correct:
                    correct_options.append(option)

        submitted = st.form_submit_button("Add Question")

        if submitted:
            if not question_text or len(options) < 2:
                st.error("Please add a question with at least 2 options")
                return

            if not correct_options:
                st.error("Please mark at least one option as correct")
                return

            # Prepare the question data
            # Convert correct_options from text to indexes
            correct_indexes = [options.index(option)
                               for option in correct_options if option in options]

            question_data = {
                "text": question_text,  # Changed from question_text to text
                "options": options,
                "correct_options": correct_indexes  # Now sending indexes instead of text
            }

            # Use our API utility to add the question
            result = add_question(st.session_state.quiz_id, question_data)
            if result:
                st.success("Question added successfully!")

    # Generate questions from Open Trivia DB
    st.subheader("Generate Questions")
    with st.form("generate_questions_form"):
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input(
                "Number of questions", min_value=1, max_value=20, value=5)
        with col2:
            category = st.selectbox(
                "Category",
                ["general", "science", "history", "geography", "entertainment", "sports"]
            )

        if st.form_submit_button("Load Questions"):
            # Use our API utility to load external questions
            result = load_external_questions(
                st.session_state.quiz_id,
                count=num_questions,
                category=category
            )

            if result:
                st.success(f"Generated {num_questions} questions successfully!")
                # Refresh to show new questions
                st.rerun()

    # Display existing questions
    st.subheader("Existing Questions")

    # Use our API utility to get quiz questions
    questions_data = get_quiz_questions(st.session_state.quiz_id)

    if questions_data and "questions" in questions_data and questions_data["questions"]:
        questions = questions_data["questions"]
        st.write(f"Total questions: {len(questions)}")

        for i, question in enumerate(questions, 1):
            # Handle both possible field names (question_text from older code or text from backend)
            question_text = question.get("text", question.get("question_text", ""))
            with st.expander(f"Question {i}: {question_text[:50]}..."):
                st.write(question_text)

                # Display options with correct ones highlighted
                st.write("Options:")
                for i, option in enumerate(question.get("options", [])):
                    # Check if this option's index is in correct_options
                    is_correct = i in question.get("correct_options", [])
                    if is_correct:
                        st.success(f"✓ {option} (Correct)")
                    else:
                        st.write(f"• {option}")

                # Only allow deletion if there are multiple questions
                if len(questions) > 1:
                    if st.button(f"Delete Question", key=f"delete_{question.get('id', i)}"):
                        # This endpoint is not implemented in our API utility yet
                        # We'll need to add it and update this code
                        st.error("Delete functionality not implemented yet")
    else:
        st.info("No questions added yet")

    # Final submit button
    if st.button("Submit Quiz"):
        # Get latest quiz info first
        quiz_data = get_quiz_info(st.session_state.quiz_id)

        # Check if quiz is already submitted
        quiz_published = quiz_data and quiz_data.get("is_submitted", False)

        if quiz_published:
            st.info("Quiz already published!")
        else:
            # Call the proper endpoint
            result = submit_quiz(st.session_state.quiz_id)
            if result:
                st.success("Quiz is ready for participants!")
                st.code(f"Quiz ID: {st.session_state.quiz_id}", language="text")
            else:
                st.error("Failed to submit quiz")
