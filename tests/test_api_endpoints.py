import unittest

from fastapi.testclient import TestClient

from api.main import app


class APIEndpointTests(unittest.TestCase):
    def test_health_recommendations_and_rag_endpoints(self) -> None:
        client = TestClient(app)

        health_response = client.get("/health")
        self.assertEqual(health_response.status_code, 200)
        self.assertEqual(health_response.json()["status"], "ok")

        overview_response = client.get("/overview")
        self.assertEqual(overview_response.status_code, 200)
        self.assertIn("summary", overview_response.json())

        recommendation_response = client.post(
            "/recommendations",
            json={"state": "CA", "top_k": 3, "max_predicted_failure_probability": 0.5},
        )
        self.assertEqual(recommendation_response.status_code, 200)
        self.assertTrue(recommendation_response.json()["results"])

        rag_response = client.post(
            "/rag/query",
            json={"query": "How do I handle a thermal alarm?", "top_k": 2, "use_llm": False},
        )
        self.assertEqual(rag_response.status_code, 200)
        self.assertIn("answer", rag_response.json())


if __name__ == "__main__":
    unittest.main()
