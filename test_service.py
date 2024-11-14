import requests
import unittest
import logging

# Configure logging to output test results and errors to a file
logging.basicConfig(filename="test_service.log", level=logging.INFO)


class TestRecommendationService(unittest.TestCase):
    recommendations_url = "http://127.0.0.1:8000"
    events_store_url = "http://127.0.0.1:8020"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def log(self, test_name, message, level="info"):
        """Helper method to log messages with test name and log level."""
        if level == "error":
            logging.error(f"[{test_name}] {message}")
        else:
            logging.info(f"[{test_name}] {message}")

    def post_events(self, test_name, user_id, event_item_ids):
        """Post events to the event store for the given user_id and item_ids."""
        for event_item_id in event_item_ids:
            resp = requests.post(
                f"{self.events_store_url}/put",
                headers=self.headers,
                params={"user_id": user_id, "item_id": event_item_id}
            )
            if resp.status_code == 200:
                self.log(
                    test_name,
                    f"PUT event: user_id={user_id}, item_id={event_item_id}. Status code: {resp.status_code}, Response body: {resp.text}"
                )
            else:
                self.log(
                    test_name,
                    f"Failed PUT event: user_id={user_id}, item_id={event_item_id}. Status code: {resp.status_code}, Response body: {resp.text}",
                    level="error"
                )

    def get_recommendations(self, test_name, user_id, k=5):
        """Request recommendations and log the response."""
        params = {"user_id": user_id, "k": k}
        resp = requests.post(f"{self.recommendations_url}/recommendations", headers=self.headers, params=params)
        if resp.status_code == 200:
            recs = resp.json().get("recs", [])
            self.log(
                test_name,
                f"POST recommendations: user_id={user_id}. Status code: {resp.status_code}, Recommendations: {recs}, Response body: {resp.text}"
            )
        else:
            self.log(
                test_name,
                f"Failed POST recommendations: user_id={user_id}. Status code: {resp.status_code}, Response body: {resp.text}",
                level="error"
            )
        return resp

    def test_user_without_recommendations(self):
        """
        Test for a user without personal recommendations.
        No events or personal recommendation data exists for the user.
        """
        test_name = "test_user_without_recommendations"
        user_id = 1291250

        # Directly request recommendations without any history or personal recommendations
        self.get_recommendations(test_name, user_id)

    def test_user_with_recommendations_and_without_story(self):
        """
        Test for a user with personal recommendations but without any online history.
        No events are posted for the user before requesting recommendations.
        """
        test_name = "test_user_with_recommendations_and_without_story"
        user_id = 1291249

        # Directly request recommendations without posting any events
        self.get_recommendations(test_name, user_id)

    def test_user_with_recommendations_and_with_story(self):
        """
        Test for a user with both personal recommendations and an online history.
        Events are posted for the user before requesting recommendations.
        """
        test_name = "test_user_with_recommendations_and_with_story"
        user_id = 1291248
        event_item_ids = [41899, 102868, 5472, 5907]

        # Post events to simulate user history
        self.post_events(test_name, user_id, event_item_ids)
        # Request recommendations after posting events
        self.get_recommendations(test_name, user_id)


if __name__ == "__main__":
    unittest.main()
