import requests
import unittest
import logging

logging.basicConfig(filename="test_service.log", level=logging.INFO)


class TestRecommendationService(unittest.TestCase):
    base_url = "http://127.0.0.1:8000/recommendations"

    def test_no_recommendations(self):
        response = requests.post(self.base_url, json={"user_id": "unknown_user"})
        self.assertEqual(response.status_code, 404)
        logging.info("Test no recommendations: Passed")

    def test_offline_recommendations_only(self):
        response = requests.post(self.base_url, json={"user_id": "user_2"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.json())
        logging.info("Test offline recommendations only: Passed")

    def test_offline_and_online_recommendations(self):
        response = requests.post(self.base_url, json={"user_id": "user_1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.json())
        logging.info("Test offline and online recommendations: Passed")


if __name__ == "__main__":
    unittest.main()
