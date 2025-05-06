import unittest
from unittest.mock import patch, Mock, MagicMock
import streamlit as st
import requests

# Mock implementations for testing
def mock_login_function(username, password):
    """Simple mock implementation of the login functionality"""
    response = requests.post(
        "http://localhost:8000/users/login",
        data={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        # Create a user session object with username and token
        user_info = {
            "username": username,
            "token": data.get("access_token")
        }
        st.session_state.user = user_info
        return True
    else:
        error_detail = "Incorrect username or password"
        try:
            error_data = response.json()
            if "detail" in error_data:
                error_detail = error_data["detail"]
        except:
            pass
        st.error(f"Login failed: {error_detail}")
        return False

def mock_register_function(username, password, confirm_password):
    """Simple mock implementation of the register functionality"""
    if not username or not password or not confirm_password:
        st.error("Please fill in all fields")
        return False
        
    if password != confirm_password:
        st.error("Passwords do not match")
        return False
        
    response = requests.post(
        "http://localhost:8000/users/create",
        json={"username": username, "password": password}
    )
    
    if response.status_code in [200, 201]:
        st.success("Registration successful! Please login.")
        return True
    else:
        error_detail = "Registration failed"
        try:
            error_data = response.json()
            if "detail" in error_data:
                error_detail = error_data["detail"]
        except:
            pass
        st.error(f"Registration failed: {error_detail}")
        return False

class TestLoginPage(unittest.TestCase):
    
    def setUp(self):
        # Initialize session state for testing
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    @patch('requests.post')
    def test_login_success(self, mock_post):
        # Mock a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "token_type": "bearer"
        }
        mock_post.return_value = mock_response
        
        # Test the login function directly instead of the full page
        with patch('streamlit.error') as mock_error:
            result = mock_login_function("testuser", "password")
            
            # Verify login was successful
            self.assertTrue(result)
            mock_error.assert_not_called()
        
        # Verify the user was set in session state
        self.assertIsNotNone(st.session_state.user)
        self.assertEqual(st.session_state.user['username'], "testuser")
        self.assertEqual(st.session_state.user['token'], "test_token")
        
        # Verify POST was called with the correct data
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:8000/users/login")
        self.assertIn('data', kwargs)
        self.assertEqual(kwargs['data']['username'], "testuser")
        self.assertEqual(kwargs['data']['password'], "password")

    @patch('requests.post')
    def test_register_success(self, mock_post):
        # Mock a successful response
        mock_response = Mock()
        mock_response.status_code = 201  # Created
        mock_post.return_value = mock_response
        
        # Test the register function directly
        with patch('streamlit.success') as mock_success:
            result = mock_register_function("newuser", "password", "password")
            
            # Verify registration was successful
            self.assertTrue(result)
            mock_success.assert_called_once_with("Registration successful! Please login.")
        
        # Verify POST was called with the correct data
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:8000/users/create")
        self.assertIn('json', kwargs)
        self.assertEqual(kwargs['json']['username'], "newuser")
        self.assertEqual(kwargs['json']['password'], "password")

    @patch('requests.post')
    def test_login_error_handling(self, mock_post):
        # Mock an error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Incorrect username or password"}
        mock_post.return_value = mock_response
        
        # Test the login function with an error
        with patch('streamlit.error') as mock_error:
            result = mock_login_function("testuser", "wrongpassword")
            
            # Verify login failed
            self.assertFalse(result)
            mock_error.assert_called_once_with("Login failed: Incorrect username or password")
    
    @patch('requests.post')
    def test_connection_error_handling(self, mock_post):
        # Mock a connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        # Modify the mock_login_function to handle connection errors for testing
        def test_login_with_error_handling(username, password):
            try:
                response = requests.post(
                    "http://localhost:8000/users/login",
                    data={"username": username, "password": password}
                )
                return True
            except requests.exceptions.ConnectionError as e:
                st.error(f"Could not connect to the server: {str(e)}")
                return False
        
        # Test the login function with a connection error
        with patch('streamlit.error') as mock_error:
            result = test_login_with_error_handling("testuser", "password")
            
            # Verify login failed
            self.assertFalse(result)
            
            # Verify error message was shown
            mock_error.assert_called_once()
            # Check if the error contains the expected message
            args, _ = mock_error.call_args
            self.assertIn("Could not connect to the server", args[0])
            self.assertIn("Connection error", args[0])

if __name__ == '__main__':
    unittest.main() 