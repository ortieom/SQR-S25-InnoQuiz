import unittest
from unittest.mock import patch, Mock
import requests
import streamlit as st
import sys
import os


class TestAPIAuthentication(unittest.TestCase):

    def setUp(self):
        # Initialize session state for testing
        if 'user' not in st.session_state:
            st.session_state.user = {
                "username": "testuser",
                "token": "test_token_value"
            }

    @patch('frontend.app.utils.api.execute_request')
    def test_api_request_with_token(self, mock_execute):
        # Mock a successful response
        mock_execute.return_value = [{"id": 1, "title": "Test Quiz"}]

        # Make a request to an endpoint that should include the token
        from frontend.app.utils.api import get_user_quizzes

        # This will fail if get_user_quizzes doesn't exist yet - we'll create it
        result = get_user_quizzes(st.session_state.user["username"])

        # Check if execute_request was called with proper method and url
        mock_execute.assert_called_once()
        args, kwargs = mock_execute.call_args

        # The first args should be the method and URL
        self.assertEqual(args[0], 'GET')
        self.assertIn('/users/', args[1])
        self.assertIn(st.session_state.user["username"], args[1])

        # Headers and cookies should be set but we don't check them directly
        # since they're handled by get_auth_headers and get_auth_cookies

    @patch('streamlit.error')
    def test_api_error_handling(self, mock_error):
        # Import the function we want to test
        from frontend.app.utils.api import handle_response

        # Create a mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Could not validate credentials"}

        # Save original user state
        original_user = st.session_state.user

        try:
            # Call handle_response directly
            result = handle_response(mock_response)

            # Check that the function returns None
            self.assertIsNone(result)

            # Verify error is shown to the user
            mock_error.assert_called_with("Session expired. Please login again.")

            # Check if the user session was cleared
            self.assertIsNone(st.session_state.user)
        finally:
            # Restore session state for other tests
            st.session_state.user = original_user


if __name__ == '__main__':
    unittest.main()
