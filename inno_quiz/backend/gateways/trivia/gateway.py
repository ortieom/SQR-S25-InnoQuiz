import requests
from typing import List, Dict, Any, Optional

from .models import TriviaQuestion


class TriviaGateway:
    BASE_URL = "https://opentdb.com/api.php"

    def get_questions(
        self,
        amount: int = 10,
        category: Optional[int] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None
    ) -> List[TriviaQuestion]:
        """
        Fetch trivia questions from the Open Trivia Database API

        Parameters:
        - amount: Number of questions (1-50)
        - category: ID of the category (optional)
        - difficulty: easy, medium, hard (optional)
        - question_type: multiple, boolean (optional)

        Returns:
        - List of TriviaQuestion objects
        """
        params: Dict[str, Any] = {"amount": amount}

        if category is not None:
            params["category"] = category

        if difficulty is not None:
            params["difficulty"] = difficulty

        if question_type is not None:
            params["type"] = question_type

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            if data["response_code"] != 0:
                # Handle API errors based on response codes
                if data["response_code"] == 1:
                    raise ValueError("Not enough questions available")
                elif data["response_code"] == 2:
                    raise ValueError("Invalid parameter")
                else:
                    raise ValueError(f"API Error: Response code {data['response_code']}")

            return [TriviaQuestion(**q) for q in data["results"]]

        except requests.HTTPError as e:
            # Handle HTTP errors
            raise ValueError(f"HTTP error from Trivia API: {str(e)}")
        except requests.RequestException as e:
            # Handle other connection errors
            raise ConnectionError(f"Error connecting to Trivia API: {str(e)}")


# Create a singleton instance
trivia_gateway = TriviaGateway() 