import requests
import streamlit as st
from typing import Dict, List, Any, Optional
import time
import socket
import uuid

# Base URL for the backend API
BASE_URL = "http://localhost:8000"

# Configuration for connection handling
MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds

def is_backend_available():
    """Check if the backend server is running"""
    try:
        # Try to connect to the backend server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        return result == 0
    except:
        return False

def handle_response(response):
    """Handle common API response scenarios"""
    if response.status_code == 401:
        # Clear user session if unauthorized (token expired or invalid)
        if 'user' in st.session_state:
            st.session_state['user'] = None
        st.error("Session expired. Please login again.")
        # Return None to indicate authentication failure
        return None
        
    # For other error codes
    if response.status_code >= 400:
        try:
            error_data = response.json()
            error_message = error_data.get("detail", f"Error: HTTP {response.status_code}")
            st.error(error_message)
        except ValueError:
            st.error(f"Error: HTTP {response.status_code}")
        return None
        
    # Return JSON data for successful responses
    try:
        return response.json()
    except ValueError:
        st.error("Invalid response from server")
        return None

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers if user is logged in"""
    headers = {"Content-Type": "application/json"}
    
    if st.session_state.user and "token" in st.session_state.user:
        token = st.session_state.user["token"]
        headers["Authorization"] = f"Bearer {token}"
        
    return headers

def get_auth_cookies() -> Dict[str, str]:
    """Get authentication cookies if user is logged in"""
    cookies = {}
    
    if st.session_state.user and "token" in st.session_state.user:
        token = st.session_state.user["token"]
        cookies["access_token"] = f"Bearer {token}"
        
    return cookies

def execute_request(method, url, **kwargs):
    """Execute a request with retry logic for connection errors"""
    headers = kwargs.pop('headers', {})
    cookies = kwargs.pop('cookies', {})
    
    # Check if backend is available before making requests
    if not is_backend_available():
        st.error("Backend server is not running. Please start the backend server and try again.")
        # Display helpful instructions
        with st.expander("How to start the backend server"):
            st.code("""
cd inno_quiz
SECRET_KEY=your_secret_key_here poetry run uvicorn backend.main:app --reload
            """)
        return None
    
    # Retry logic for connection errors
    for attempt in range(MAX_RETRIES + 1):
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, cookies=cookies, **kwargs)
            elif method == 'POST':
                response = requests.post(url, headers=headers, cookies=cookies, **kwargs)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, cookies=cookies, **kwargs)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, cookies=cookies, **kwargs)
            else:
                st.error(f"Unsupported HTTP method: {method}")
                return None
                
            return handle_response(response)
        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES:
                # Show retry message
                st.warning(f"Connection failed. Retrying in {RETRY_DELAY} seconds... ({attempt+1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                # Final attempt failed
                st.error("Could not connect to the backend server. Please check if the server is running.")
                # Display helpful instructions
                with st.expander("How to start the backend server"):
                    st.code("""
cd inno_quiz
SECRET_KEY=your_secret_key_here poetry run uvicorn backend.main:app --reload
                    """)
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None

def get_user_quizzes(username: str) -> Optional[List[Dict[str, Any]]]:
    """Get quizzes for a specific user"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    return execute_request('GET', f"{BASE_URL}/v1/users/{username}/quizzes", headers=headers, cookies=cookies)

def create_quiz(title: str, category: str) -> Optional[Dict[str, Any]]:
    """Create a new quiz"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Convert category to integer if it's a string
    try:
        category_id = int(category)
    except ValueError:
        # Default to general knowledge if category is not a valid number
        category_id = 9
    
    return execute_request('POST', f"{BASE_URL}/v1/quiz/", 
                           json={"name": title, "category": category_id, "is_submitted": False}, 
                           headers=headers, cookies=cookies)

def get_quiz_info(quiz_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific quiz"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    return execute_request('GET', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}", headers=headers, cookies=cookies)

def add_question(quiz_id: str, question_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Add a question to a quiz"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    # Ensure question data matches the expected backend format
    # Backend expects: text, options, correct_options (as indexes)
    if "question_text" in question_data and "text" not in question_data:
        question_data["text"] = question_data.pop("question_text")
    
    return execute_request('POST', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}/questions", 
                           json=question_data, headers=headers, cookies=cookies)

def load_external_questions(quiz_id: str, count: int, category: str) -> Optional[Dict[str, Any]]:
    """Load questions from external API"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    return execute_request('GET', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}/load_questions?count={count}&category={category}", 
                           headers=headers, cookies=cookies)

def get_quiz_questions(quiz_id: str) -> Optional[Dict[str, Any]]:
    """Get all questions for a quiz"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    return execute_request('GET', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}/questions", 
                           headers=headers, cookies=cookies)

def ensure_uuid_format(id_value: str) -> str:
    """
    Ensures the ID is in proper UUID format
    Returns the string representation of the UUID
    """
    try:
        # Convert to UUID object and then back to string to ensure proper format
        return str(uuid.UUID(str(id_value)))
    except ValueError:
        # If not a valid UUID, return as is and let the backend handle the error
        return str(id_value)

def submit_quiz(quiz_id: str) -> Optional[Dict[str, Any]]:
    """Submit a quiz as ready for participants"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    return execute_request('PUT', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}/submit", 
                          headers=headers, cookies=cookies)

def submit_quiz_answers(quiz_id: str, answers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Submit answers for a quiz"""
    headers = get_auth_headers()
    cookies = get_auth_cookies()
    
    # Ensure proper UUID format
    formatted_quiz_id = ensure_uuid_format(quiz_id)
    
    # Make sure quiz_id is in the answers with proper format
    answers["quiz_id"] = formatted_quiz_id
    
    return execute_request('POST', f"{BASE_URL}/v1/quiz/{formatted_quiz_id}/answers", 
                           json=answers, headers=headers, cookies=cookies)

def register_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Register a new user"""
    return execute_request('POST', f"{BASE_URL}/v1/users/create", 
                         json={"username": username, "password": password})

def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Login a user"""
    return execute_request('POST', f"{BASE_URL}/v1/users/login",
                         data={"username": username, "password": password})
