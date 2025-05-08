import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import ConnectionError
import streamlit as st
from frontend.app.utils.api import create_quiz, get_user_quizzes


class TestConnectionHandling(unittest.TestCase):

    def setUp(self):
        # Initialize session state for testing
        if 'user' not in st.session_state:
            st.session_state.user = {
                "username": "testuser",
                "token": "test_token_value"
            }

    @patch('frontend.app.utils.api.execute_request')
    def test_connection_refused_error(self, mock_execute):
        """Test that connection errors are handled gracefully with retries"""
        # Mock the execute_request function to return None (simulating failure)
        mock_execute.return_value = None

        # Call the API function that would trigger the request
        result = create_quiz(title="Test Quiz", category="Test")

        # Verify execute_request was called with expected arguments
        mock_execute.assert_called_once()
        args = mock_execute.call_args[0]
        self.assertEqual(args[0], 'POST')
        self.assertIn('/quiz/', args[1])

        # Check that it returns None on error
        self.assertIsNone(result)

    @patch('frontend.app.utils.api.is_backend_available',
           return_value=False)  # Simulate backend not available
    def test_backend_unavailable_handling(self, mock_available):
        """Test that backend unavailability is handled properly"""
        # Set up mock error tracking
        with patch('streamlit.error') as mock_error:
            # Call API function
            result = get_user_quizzes("testuser")

            # Check the error is displayed to the user
            mock_error.assert_called()
            # Check if the error contains expected text
            error_args = mock_error.call_args[0][0]
            self.assertIn("Backend server is not running", error_args)

        # Function should return None on error
        self.assertIsNone(result)

    @patch('socket.socket')
    def test_backend_checks_connection(self, mock_socket):
        """Test that is_backend_available tries to connect to the backend"""
        # Mock socket behavior
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 0  # Simulate successful connection

        from frontend.app.utils.api import is_backend_available

        # Call the function
        result = is_backend_available()

        # Check socket was used correctly
        mock_socket_instance.connect_ex.assert_called_once_with(('localhost', 8000))
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
