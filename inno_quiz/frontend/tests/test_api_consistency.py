import unittest
from unittest.mock import patch, MagicMock
import inspect
import streamlit as st
from frontend.app.views import login, create_quiz, add_questions, quiz_info, play_quiz

class TestAPIConsistency(unittest.TestCase):
    
    def setUp(self):
        # Initialize session state for testing
        if 'user' not in st.session_state:
            st.session_state.user = {
                "username": "testuser",
                "token": "test_token_value"
            }
        if 'quiz_id' not in st.session_state:
            st.session_state.quiz_id = "test_quiz_id"
            
    @patch('frontend.app.utils.api.requests.get')
    @patch('frontend.app.utils.api.requests.post')
    def test_no_direct_requests_in_views(self, mock_post, mock_get):
        """Test that views don't use requests directly but use the API utility"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_get.return_value = MagicMock(status_code=200)
        
        # Create a separate patch to detect direct requests usage
        with patch('requests.get') as direct_get, \
             patch('requests.post') as direct_post:
                
            # Set up mocks to detect any direct usage
            direct_get.side_effect = Exception("Direct request.get detected!")
            direct_post.side_effect = Exception("Direct request.post detected!")
            
            # These calls should use the API utility, not direct requests
            try:
                # Test create_quiz view
                with patch('streamlit.text_input', return_value="Test Quiz"), \
                     patch('streamlit.form_submit_button', return_value=True):
                    create_quiz.show_create_quiz_page()
                    
                # Direct requests should not be called
                direct_get.assert_not_called()
                direct_post.assert_not_called()
                
            except Exception as e:
                self.fail(f"Direct request detected: {str(e)}")
                
    def test_api_utility_imported_in_all_views(self):
        """Test that all views import the API utility module"""
        view_modules = [
            login,
            create_quiz,
            add_questions,
            quiz_info,
            play_quiz
        ]
        
        for module in view_modules:
            # Check imports in the module
            module_src = inspect.getsource(module)
            
            # Skip login since it still needs to use direct requests for auth
            if module.__name__ == 'frontend.app.views.login':
                continue
                
            # Allow both app.utils.api and utils.api imports
            import_found = ('from frontend.app.utils.api import' in module_src or 
                           'from frontend.app.utils.api import' in module_src)
            
            self.assertTrue(import_found, 
                         f"Module {module.__name__} does not import API utility")

if __name__ == '__main__':
    unittest.main() 