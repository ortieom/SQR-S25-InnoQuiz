import streamlit as st
import uuid
import pandas as pd
from frontend.app.utils.api import get_quiz_info, get_quiz_leaderboard, ensure_uuid_format


def is_valid_uuid(val):
    """Check if a string is a valid UUID"""
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def show_quiz_info_page():
    st.title("Quiz Information")

    quiz_id = st.text_input("Enter Quiz ID")
    search_button = st.button("Search Quiz")

    if search_button and quiz_id:
        if not is_valid_uuid(quiz_id):
            st.error("Invalid Quiz ID format. Please enter a valid UUID.")
            return

        # Format to proper UUID string
        formatted_quiz_id = ensure_uuid_format(quiz_id)

        # Use our API utility to get quiz info
        quiz = get_quiz_info(formatted_quiz_id)

        if quiz:
            st.subheader(quiz["name"])
            st.write(f"Category: {quiz.get('category', 'N/A')}")

            # Show quiz details
            with st.container():
                st.subheader("Quiz Details")
                st.write(f"Questions: {quiz.get('question_count', 0)}")
                st.write(f"Created by: {quiz.get('author', 'Anonymous')}")

                # Show status badge based on is_submitted field
                is_submitted = quiz.get('is_submitted', False)
                if is_submitted:
                    st.success("Status: Published")
                else:
                    st.warning("Status: Draft")

            # Fetch and display leaderboard
            st.subheader(f"Quiz Leaderboard - Top Scores")

            # Get leaderboard data from API
            leaderboard_data = get_quiz_leaderboard(formatted_quiz_id)

            if leaderboard_data and "entries" in leaderboard_data and leaderboard_data["entries"]:
                # Convert leaderboard to DataFrame for better display
                leaderboard_entries = []

                for i, entry in enumerate(leaderboard_data["entries"], 1):
                    leaderboard_entries.append(
                        {
                            "Rank": i, "Username": entry.get(
                                'username', 'User'), "Score": entry.get(
                                'score', 0), "Time (sec)": round(
                                entry.get(
                                    'completion_time', 0), 1), "Date": entry.get(
                                'date', 'N/A').split('T')[0] if isinstance(
                                entry.get('date'), str) else str(
                                    entry.get(
                                        'date', 'N/A'))})

                df = pd.DataFrame(leaderboard_entries)

                # Display top scores with styling
                st.dataframe(
                    df, column_config={
                        "Rank": st.column_config.NumberColumn(
                            help="Position on leaderboard"), "Username": st.column_config.TextColumn(
                            help="Player name"), "Score": st.column_config.NumberColumn(
                            help="Total points", format="%d pts"), "Time (sec)": st.column_config.NumberColumn(
                            help="Time to complete the quiz", format="%.1f s"), "Date": st.column_config.TextColumn(
                            help="Completion date")}, hide_index=True, use_container_width=True)

                # Add a small explanation
                st.caption(
                    "Leaderboard shows the highest scores achieved by users who completed this quiz, sorted by score and completion time.")
            else:
                st.info("No scores yet for this quiz. Be the first to complete it!")

            # Join quiz button
            if st.session_state.user:
                if st.button("Join Quiz"):
                    st.session_state.quiz_id = str(formatted_quiz_id)
                    st.query_params.clear()
                    st.query_params["page"] = "play_quiz"
                    st.rerun()
            else:
                st.warning("Please login to join this quiz")
        else:
            st.error("Quiz not found")
