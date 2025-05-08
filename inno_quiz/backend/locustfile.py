import json
import random
import uuid
from typing import Dict, List, Optional

from locust import HttpUser, between, task


class QuizUser(HttpUser):
    """
    Simulates a user interacting with the InnoQuiz application.
    Tests the main scenarios:
    - User registration and login
    - Viewing quizzes
    - Taking quizzes
    - Viewing leaderboard
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.username = f"locust_user_{uuid.uuid4().hex[:8]}"
        self.password = "testpassword123"
        self.current_quiz_id = None
        self.questions = []
        self.has_loaded_external_questions = False  # Flag to track if we've already loaded external questions

    def on_start(self):
        """
        Register and log in when simulation starts
        """
        # Register a new user
        self.register()
        # Log in
        self.login()

    def register(self):
        """
        Register a new user to the application
        """
        with self.client.post(
            "/v1/users/create",
            json={"username": self.username, "password": self.password},
            name="Register User",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                print(f"Successfully registered user: {self.username}")
            elif response.status_code == 400 and "Username already registered" in response.text:
                # Try with a different username if this one is taken
                self.username = f"locust_user_{uuid.uuid4().hex[:8]}"
                self.register()
            else:
                response.failure(f"Registration failed: {response.text}")

    def login(self):
        """
        Login to the application
        """
        with self.client.post(
            "/v1/users/login",
            data={"username": self.username, "password": self.password},
            name="Login",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                resp_data = response.json()
                self.token = resp_data.get("access_token")
                print(f"Successfully logged in: {self.username}")
                # We don't need to set the Authorization header since the backend
                # uses cookie-based auth set by the login endpoint
            else:
                response.failure(f"Login failed: {response.text}")

    @task(5)
    def get_user_info(self):
        """
        Get the current user information
        """
        with self.client.get(
            "/v1/users/me",
            name="User Info",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get user info: {response.text}")

    @task(10)
    def get_user_quizzes(self):
        """
        Get quizzes created by the current user
        """
        with self.client.get(
            f"/v1/users/{self.username}/quizzes",
            name="User Quizzes",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get user quizzes: {response.text}")

    @task(5)
    def create_quiz(self):
        """
        Create a new quiz
        """
        # Use the correct field names and data types as per QuizBase model
        quiz_data = {
            "name": f"Locust Test Quiz {random.randint(1, 1000)}",
            "category": 9,  # General Knowledge category (from the Category enum)
            "is_submitted": False
        }

        with self.client.post(
            "/v1/quiz/",
            json=quiz_data,
            name="Create Quiz",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.current_quiz_id = data.get("id")
                print(f"Successfully created quiz with ID: {self.current_quiz_id}")
            else:
                response.failure(f"Failed to create quiz: {response.text}")

    @task(8)
    def view_quiz_info(self):
        """
        View quiz information
        """
        if not self.current_quiz_id:
            return

        with self.client.get(
            f"/v1/quiz/{self.current_quiz_id}",
            name="Quiz Info",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get quiz info: {response.text}")

    @task(8)
    def view_quiz_questions(self):
        """
        View questions for a quiz
        """
        if not self.current_quiz_id:
            return

        with self.client.get(
            f"/v1/quiz/{self.current_quiz_id}/questions",
            name="Quiz Questions",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.questions = data.get("questions", [])
                print(f"Loaded {len(self.questions)} questions for quiz {self.current_quiz_id}")
            else:
                response.failure(f"Failed to get quiz questions: {response.text}")

    @task(3)
    def add_question_to_quiz(self):
        """
        Add a question to a quiz
        """
        if not self.current_quiz_id:
            return

        # Match the QuestionRequest model structure
        # The correct format is:
        # - text: str
        # - options: List[str]
        # - correct_options: List[int]
        question_data = {
            "text": f"Test question {random.randint(1, 100)}?",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_options": [0]  # Index 0 is the correct answer (Option 1)
        }

        with self.client.post(
            f"/v1/quiz/{self.current_quiz_id}/questions",
            json=question_data,
            name="Add Question",
            catch_response=True
        ) as response:
            if response.status_code not in [200, 201]:
                response.failure(f"Failed to add question: {response.text}")
            else:
                print(f"Successfully added question to quiz {self.current_quiz_id}")

    @task(1)
    def load_external_questions(self):
        """
        Load questions from external API - Runs only ONCE per user session to avoid API abuse
        """
        # Skip if we've already loaded external questions or have no quiz ID
        if not self.current_quiz_id or self.has_loaded_external_questions:
            return

        with self.client.get(
            # Use category id instead of name
            f"/v1/quiz/{self.current_quiz_id}/load_questions?count=5&category=9",
            name="Load External Questions",
            catch_response=True
        ) as response:
            # Mark as completed regardless of outcome to prevent retries
            self.has_loaded_external_questions = True

            if response.status_code == 200:
                print(f"Successfully loaded external questions for quiz {self.current_quiz_id}")
            else:
                response.failure(f"Failed to load external questions: {response.text}")

    @task(5)
    def submit_quiz_answers(self):
        """
        Submit answers for a quiz
        """
        if not self.current_quiz_id or not self.questions:
            return

        # Prepare random answers
        answers = []
        for question in self.questions:
            question_id = question.get("id")
            options = question.get("options", [])

            if options:
                # Choose a random option
                chosen_option = random.choice(options)
                answers.append({
                    "question_id": question_id,
                    "answer_id": chosen_option.get("id")
                })

        submission_data = {
            "quiz_id": self.current_quiz_id,
            "user_id": self.username,  # This will be overridden by the backend
            "answers": answers
        }

        with self.client.post(
            f"/v1/quiz/{self.current_quiz_id}/answers",
            json=submission_data,
            name="Submit Quiz",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to submit quiz answers: {response.text}")

    @task(10)
    def view_leaderboard(self):
        """
        View quiz leaderboard
        """
        if not self.current_quiz_id:
            return

        with self.client.get(
            f"/v1/quiz/{self.current_quiz_id}/leaderboard",
            name="Leaderboard",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to view leaderboard: {response.text}")
