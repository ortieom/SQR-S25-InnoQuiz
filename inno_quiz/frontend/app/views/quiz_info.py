import streamlit as st
from frontend.app.utils.api import get_quiz_info

def show_quiz_info_page():
    st.title("Quiz Information")
    
    quiz_id = st.text_input("Enter Quiz ID")
    search_button = st.button("Search Quiz")
    
    if search_button and quiz_id:
        # Use our API utility to get quiz info
        quiz = get_quiz_info(quiz_id)
        
        if quiz:
            st.subheader(quiz["title"])
            st.write(f"Category: {quiz.get('category', 'N/A')}")
            
            # Show quiz details
            with st.container():
                st.subheader("Quiz Details")
                st.write(f"Questions: {quiz.get('question_count', 0)}")
                st.write(f"Created by: {quiz.get('author', 'Anonymous')}")
                
                # Show status badge
                status = quiz.get('status', 'unknown')
                if status == 'published':
                    st.success("Status: Published")
                elif status == 'draft':
                    st.warning("Status: Draft")
                else:
                    st.info(f"Status: {status}")
            
            # Show leaderboard if available
            if "leaderboard" in quiz:
                st.subheader("Leaderboard")
                leaderboard = quiz["leaderboard"]
                if leaderboard:
                    for i, entry in enumerate(leaderboard, 1):
                        st.write(f"{i}. {entry.get('username', 'User')} - {entry.get('score', 0)} points")
                else:
                    st.info("No scores yet")
            
            # Join quiz button
            if st.session_state.user:
                if st.button("Join Quiz"):
                    st.session_state.quiz_id = quiz_id
                    st.query_params.clear()
                    st.query_params["page"] = "play_quiz"
                    st.rerun()
            else:
                st.warning("Please login to join this quiz") 