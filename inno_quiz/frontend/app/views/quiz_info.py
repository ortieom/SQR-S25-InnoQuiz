import streamlit as st
import requests

def show_quiz_info_page():
    st.title("Quiz Information")
    
    quiz_id = st.text_input("Enter Quiz ID")
    search_button = st.button("Search Quiz")
    
    if search_button and quiz_id:
        try:
            # Get quiz information
            quiz_response = requests.get(f"http://localhost:8000/quizzes/{quiz_id}")
            if quiz_response.status_code == 200:
                quiz = quiz_response.json()
                
                st.subheader(quiz["title"])
                st.write(f"Theme: {quiz['theme']}")
                st.write(f"Description: {quiz['description']}")
                
                # Show leaderboard
                st.subheader("Leaderboard")
                leaderboard_response = requests.get(f"http://localhost:8000/quizzes/{quiz_id}/leaderboard")
                if leaderboard_response.status_code == 200:
                    leaderboard = leaderboard_response.json()
                    for i, entry in enumerate(leaderboard, 1):
                        st.write(f"{i}. {entry['username']} - {entry['score']} points")
                else:
                    st.info("No scores yet")
                
            else:
                st.error("Quiz not found")
        except requests.exceptions.RequestException:
            st.error("Could not connect to the server") 