import streamlit as st
import requests

def show_play_quiz_page():
    st.title("Play Quiz")
    
    if not st.session_state.user:
        st.warning("Please login first to play quizzes")
        return
    
    # Initialize quiz state
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'quiz_id': None,
            'questions': None,
            'current_question_index': 0,
            'score': 0,
            'answers': [],
            'correct_answers': 0,
            'wrong_answers': 0
        }
    
    # If no quiz is loaded, show input form
    if not st.session_state.quiz_state['quiz_id']:
        quiz_id = st.text_input("Enter Quiz ID to Play")
        start_button = st.button("Start Quiz")
        
        if start_button and quiz_id:
            try:
                # Get quiz information and questions
                quiz_response = requests.get(f"http://localhost:8000/quizzes/{quiz_id}")
                questions_response = requests.get(f"http://localhost:8000/quizzes/{quiz_id}/questions")
                
                if quiz_response.status_code == 200 and questions_response.status_code == 200:
                    quiz = quiz_response.json()
                    questions = questions_response.json()
                    
                    if not questions:
                        st.warning("This quiz has no questions yet")
                        return
                    
                    # Initialize quiz state
                    st.session_state.quiz_state = {
                        'quiz_id': quiz_id,
                        'questions': questions,
                        'current_question_index': 0,
                        'score': 0,
                        'answers': [],
                        'correct_answers': 0,
                        'wrong_answers': 0
                    }
                    st.rerun()
                else:
                    st.error("Quiz not found or has no questions")
            except requests.exceptions.RequestException:
                st.error("Could not connect to the server")
    else:
        # Show quiz progress
        questions = st.session_state.quiz_state['questions']
        current_index = st.session_state.quiz_state['current_question_index']
        current_question = questions[current_index]
        
        # Progress bar
        progress = (current_index + 1) / len(questions)
        st.progress(progress)
        
        # Question counter
        st.subheader(f"Question {current_index + 1}/{len(questions)}")
        st.write(current_question["question_text"])
        
        # Show options
        selected_answer = st.radio(
            "Select your answer:",
            current_question["options"],
            key=f"question_{current_index}"
        )
        
        # Submit answer button
        if st.button("Submit Answer"):
            # Check if answer is correct
            if selected_answer == current_question["correct_answer"]:
                st.session_state.quiz_state['correct_answers'] += 1
            else:
                st.session_state.quiz_state['wrong_answers'] += 1
            
            # Move to next question or finish quiz
            if current_index < len(questions) - 1:
                st.session_state.quiz_state['current_question_index'] += 1
                st.rerun()
            else:
                # Calculate final score
                total_questions = len(questions)
                correct = st.session_state.quiz_state['correct_answers']
                wrong = st.session_state.quiz_state['wrong_answers']
                score = (correct / total_questions) * 100
                
                # Submit final score
                try:
                    score_response = requests.post(
                        f"http://localhost:8000/quizzes/{st.session_state.quiz_state['quiz_id']}/submit",
                        json={
                            "user_id": st.session_state.user["id"],
                            "score": score
                        }
                    )
                    if score_response.status_code == 200:
                        # Show detailed results
                        st.success("Quiz completed!")
                        st.subheader("Your Results:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Questions", total_questions)
                        with col2:
                            st.metric("Correct Answers", correct)
                        with col3:
                            st.metric("Wrong Answers", wrong)
                        
                        st.subheader(f"Final Score: {score:.1f}%")
                        
                        # Show leaderboard
                        try:
                            leaderboard_response = requests.get(
                                f"http://localhost:8000/quizzes/{st.session_state.quiz_state['quiz_id']}/leaderboard"
                            )
                            if leaderboard_response.status_code == 200:
                                leaderboard = leaderboard_response.json()
                                if leaderboard:
                                    st.subheader("Leaderboard")
                                    for i, entry in enumerate(leaderboard[:5], 1):
                                        st.write(f"{i}. {entry['username']} - {entry['score']}%")
                        except:
                            st.info("Could not load leaderboard")
                    else:
                        st.error("Could not submit score")
                except:
                    st.error("Could not connect to the server")
                
        
        # Add a button to restart the quiz
        if st.button("Restart Quiz"):
            st.session_state.quiz_state = {
                'quiz_id': None,
                'questions': None,
                'current_question_index': 0,
                'score': 0,
                'answers': [],
                'correct_answers': 0,
                'wrong_answers': 0
            }
            st.rerun() 