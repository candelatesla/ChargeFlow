import unittest

from src.rag.service import answer_query, build_rag_index
from src.recommender.service import build_recommendation_snapshot, recommend_stations


class Day5ServiceTests(unittest.TestCase):
    def test_recommendations_and_rag_work(self) -> None:
        recommendation_path = build_recommendation_snapshot()
        rag_outputs = build_rag_index()

        self.assertTrue(recommendation_path.exists())
        self.assertTrue(rag_outputs["index"].exists())

        recommendations = recommend_stations("CA", top_k=3)
        self.assertTrue(recommendations)
        self.assertLessEqual(len(recommendations), 3)

        rag_result = answer_query("How should I respond to a cooling alarm?", top_k=2, use_llm=False)
        self.assertIn("answer", rag_result)
        self.assertTrue(rag_result["sources"])


if __name__ == "__main__":
    unittest.main()
