import streamlit as st
from pathlib import Path
import requests
import time

# Set page config
st.set_page_config(
    page_title="InnoQuiz",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .quiz-list {
        margin: 1rem 0;
        padding: 0.5rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    /* Add loading spinner */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(0,0,0,.1);
        border-radius: 50%;
        border-top-color: #000;
        animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'quiz_id' not in st.session_state:
    st.session_state.quiz_id = None
if 'my_quizzes' not in st.session_state:
    st.session_state.my_quizzes = []
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = 0

# Cache user quizzes fetch
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_user_quizzes(user_id):
    try:
        response = requests.get(f"http://localhost:8000/users/{user_id}/quizzes")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# Navigation
st.sidebar.title("InnoQuiz")

# Show login status and user's quizzes
if st.session_state.user:
    st.sidebar.success(f"Logged in as: {st.session_state.user['username']}")
    
    # Fetch user's quizzes with caching
    current_time = time.time()
    if current_time - st.session_state.last_fetch > 60:  # Refresh every minute
        st.session_state.my_quizzes = fetch_user_quizzes(st.session_state.user['id'])
        st.session_state.last_fetch = current_time
    
    # Show user's quizzes
    if st.session_state.my_quizzes:
        st.sidebar.markdown("### Your Quizzes")
        for quiz in st.session_state.my_quizzes:
            col1, col2, col3 = st.sidebar.columns([2, 1, 1])
            with col1:
                st.write(f"📝 {quiz['title']}")
            with col2:
                if st.button("Select", key=f"select_quiz_{quiz['id']}"):
                    st.session_state.quiz_id = quiz['id']
                    st.query_params["page"] = "add_questions"
                    st.rerun()
            with col3:
                if st.button("ID", key=f"copy_id_{quiz['id']}"):
                    st.sidebar.code(quiz['id'], language="text")
    
    # Show current quiz info
    if st.session_state.quiz_id:
        current_quiz = next(
            (q for q in st.session_state.my_quizzes if q['id'] == st.session_state.quiz_id),
            None
        )
        if current_quiz:
            st.sidebar.markdown("### Current Quiz")
            st.sidebar.info(f"Working on: {current_quiz['title']}")
    
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.user = None
        st.session_state.quiz_id = None
        st.session_state.my_quizzes = []
        st.query_params.clear()
        st.rerun()
else:
    st.sidebar.warning("Not logged in")

# Navigation options based on login status
if st.session_state.user:
    pages = ["Create Quiz", "Add Questions", "Quiz Info", "Play Quiz"]
else:
    pages = ["Login", "Quiz Info"]

# Convert URL-friendly page names to display names
page_mapping = {
    "login": "Login",
    "create_quiz": "Create Quiz",
    "add_questions": "Add Questions",
    "quiz_info": "Quiz Info",
    "play_quiz": "Play Quiz"
}

# Convert display names to URL-friendly names
reverse_page_mapping = {v: k for k, v in page_mapping.items()}

# Get current page from URL or default to login
current_page = st.query_params.get("page", "login")
if current_page not in page_mapping:
    current_page = "login"

# Create navigation buttons
st.sidebar.markdown("### Navigation")
for page_name in pages:
    if st.sidebar.button(page_name, key=f"nav_{page_name.lower().replace(' ', '_')}"):
        if page_name == "Add Questions" and not st.session_state.quiz_id:
            st.sidebar.warning("Please select a quiz first")
            continue
            
        st.query_params.clear()
        st.query_params["page"] = reverse_page_mapping[page_name]
        st.rerun()

# Show current page
page = page_mapping.get(current_page, "Login")

# Import and show pages with loading indicator
with st.spinner("Loading..."):
    if page == "Login" and not st.session_state.user:
        from views.login import show_login_page
        show_login_page()
    elif page == "Create Quiz" and st.session_state.user:
        from views.create_quiz import show_create_quiz_page
        show_create_quiz_page()
    elif page == "Add Questions" and st.session_state.user:
        if not st.session_state.quiz_id:
            st.warning("Please select a quiz first")
        else:
            from views.add_questions import show_add_questions_page
            show_add_questions_page()
    elif page == "Quiz Info":
        from views.quiz_info import show_quiz_info_page
        show_quiz_info_page()
    elif page == "Play Quiz":
        if not st.session_state.user:
            st.warning("Please login first")
        else:
            from views.play_quiz import show_play_quiz_page
            show_play_quiz_page()
