import streamlit as st
from frontend.app.utils.api import get_quiz_info, get_quiz_questions, submit_quiz_answers, ensure_uuid_format
import time

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
            'wrong_answers': 0,
            'start_time': None
        }
    
    # If no quiz is loaded, show input form
    if not st.session_state.quiz_state['quiz_id']:
        quiz_id = st.text_input("Enter Quiz ID to Play")
        start_button = st.button("Start Quiz")
        
        if start_button and quiz_id:
            # Format quiz_id properly
            formatted_quiz_id = ensure_uuid_format(quiz_id)
            
            # Use our API utility to get quiz info and questions
            quiz = get_quiz_info(formatted_quiz_id)
            questions_data = get_quiz_questions(formatted_quiz_id)
            
            if quiz and questions_data and "questions" in questions_data:
                questions = questions_data["questions"]
                
                if not questions:
                    st.warning("This quiz has no questions yet")
                    return
                
                # Initialize quiz state
                st.session_state.quiz_state = {
                    'quiz_id': formatted_quiz_id,
                    'questions': questions,
                    'current_question_index': 0,
                    'score': 0,
                    'answers': [],
                    'correct_answers': 0,
                    'wrong_answers': 0,
                    'start_time': time.time(),
                    'user_answers': {}
                }
                st.rerun()
            else:
                st.error("Quiz not found or has no questions")
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
        
        # Handle both field names (text and question_text)
        question_text = current_question.get("text", current_question.get("question_text", ""))
        st.write(question_text)
        
        # Show options
        options = current_question.get("options", [])
        selected_option_index = st.radio(
            "Select your answer:",
            range(len(options)),
            format_func=lambda i: options[i],
            key=f"question_{current_index}"
        )
        
        # Store user's selection
        if "user_answers" not in st.session_state.quiz_state:
            st.session_state.quiz_state["user_answers"] = {}
        
        # Submit answer button
        if st.button("Submit Answer"):
            # Store this answer with the correct format
            question_id = current_question.get("id", f"q{current_index}")
            
            # Add this answer to the list
            st.session_state.quiz_state["answers"].append({
                "question_id": question_id,
                "selected_options": [selected_option_index]  # Backend expects a list
            })
            
            # Check if answer is correct - compare indexes
            correct_options = current_question.get("correct_options", [])
            if selected_option_index in correct_options:
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
                
                # Calculate completion time
                completion_time = time.time() - st.session_state.quiz_state.get('start_time', time.time())
                
                # Prepare submission data
                submission_data = {
                    "quiz_id": st.session_state.quiz_state['quiz_id'],
                    "user_id": st.session_state.user["username"],
                    "answers": st.session_state.quiz_state["answers"],
                    "completion_time": completion_time
                }
                
                # Submit final score using our API utility
                result = submit_quiz_answers(
                    st.session_state.quiz_state['quiz_id'],
                    submission_data
                )
                
                if result:
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
                    
                    # Show score from API result if available
                    if "score" in result:
                        st.info(f"Your official score: {result['score']}/{result.get('total', total_questions)}")
                    
                    # Show leaderboard if available in quiz info
                    quiz = get_quiz_info(st.session_state.quiz_state['quiz_id'])
                    if quiz and "leaderboard" in quiz:
                        leaderboard = quiz["leaderboard"]
                        if leaderboard:
                            st.subheader("Leaderboard")
                            for i, entry in enumerate(leaderboard[:5], 1):
                                st.write(f"{i}. {entry.get('username', 'User')} - {entry.get('score', 0)}%")
                else:
                    st.error("Could not submit score")
        
        # Add a button to restart the quiz
        if st.button("Restart Quiz"):
            st.session_state.quiz_state = {
                'quiz_id': None,
                'questions': None,
                'current_question_index': 0,
                'score': 0,
                'answers': [],
                'correct_answers': 0,
                'wrong_answers': 0,
                'user_answers': {}
            }
            st.rerun() 