"""Small automated tests for the planning and validation logic."""
import unittest
from datetime import date, timedelta

from planner import create_plan, format_duration, ai_recommendations
from utils import parse_subjects_and_difficulty, parse_positive_hours, parse_break_minutes


class PlannerTests(unittest.TestCase):
    def test_parse_subjects(self):
        subjects, ratings = parse_subjects_and_difficulty(
            "Mathematics, Science, English",
            "Mathematics:5, Science:4, English:2",
        )
        self.assertEqual(subjects, ["Mathematics", "Science", "English"])
        self.assertEqual(ratings["Mathematics"], 5)

    def test_case_insensitive_matching(self):
        subjects, ratings = parse_subjects_and_difficulty("math, SCIENCE", "MATH:5, science:3")
        self.assertEqual(ratings, {"math": 5, "SCIENCE": 3})

    def test_missing_rating_rejected(self):
        with self.assertRaises(ValueError):
            parse_subjects_and_difficulty("Math, Science", "Math:5")

    def test_invalid_hours_rejected(self):
        with self.assertRaises(ValueError):
            parse_positive_hours("0")

    def test_invalid_break_rejected(self):
        with self.assertRaises(ValueError):
            parse_break_minutes("-2")

    def test_plan_sessions_and_allocation(self):
        exam = (date.today() + timedelta(days=3)).isoformat()
        plan = create_plan(
            ["Math", "Science", "English"], 4, exam,
            {"Math": 5, "Science": 4, "English": 2},
            "8:00 AM", 10,
        )
        self.assertEqual(len(plan), 3)
        self.assertTrue(all(day["sessions"] for day in plan))
        first_day_minutes = sum(s["duration_minutes"] for s in plan[0]["sessions"])
        self.assertEqual(first_day_minutes, 240)
        self.assertEqual(plan[-1]["title"], "Final revision day")

    def test_exam_day_plan(self):
        plan = create_plan(["Math"], 2, date.today(), {"Math": 5}, "8:00 AM", 5)
        self.assertEqual(plan[0]["title"], "Exam day")

    def test_recommendations(self):
        tips = ai_recommendations({"Math": 5}, 2)
        self.assertTrue(any("revision" in tip.lower() for tip in tips))

    def test_duration(self):
        self.assertEqual(format_duration(90), "1 hr 30 min")


if __name__ == "__main__":
    unittest.main()
