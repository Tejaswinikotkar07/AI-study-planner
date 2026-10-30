"""Core study-plan generation logic for AI Study Planner.

The recommendations are rule-based (no external AI API is required).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, List, Sequence


def parse_start_time(value: str) -> time:
    """Convert a 12-hour time such as '4:00 PM' into a time object."""
    try:
        return datetime.strptime(value.strip(), "%I:%M %p").time()
    except (ValueError, AttributeError) as exc:
        raise ValueError("Choose a valid study start time.") from exc


def format_duration(minutes: int) -> str:
    minutes = max(0, int(minutes))
    hours, remaining = divmod(minutes, 60)
    if hours and remaining:
        return f"{hours} hr {remaining} min"
    if hours:
        return f"{hours} hr"
    return f"{remaining} min"


def validate_inputs(
    subjects: Sequence[str],
    hours: float,
    exam_date: str | date,
    difficulty: Dict[str, int],
    break_minutes: int,
    start_time: str,
) -> tuple[list[str], date]:
    cleaned = [str(subject).strip() for subject in subjects if str(subject).strip()]
    if not cleaned:
        raise ValueError("Enter at least one subject.")
    if len({s.casefold() for s in cleaned}) != len(cleaned):
        raise ValueError("Subject names must be unique.")
    if not isinstance(hours, (int, float)) or hours <= 0 or hours > 24:
        raise ValueError("Study hours must be greater than 0 and no more than 24.")
    if not isinstance(break_minutes, int) or not 0 <= break_minutes <= 180:
        raise ValueError("Break time must be between 0 and 180 minutes.")
    for subject in cleaned:
        rating = difficulty.get(subject)
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError(f"Enter a difficulty rating from 1 to 5 for {subject}.")
    if isinstance(exam_date, date):
        exam = exam_date
    else:
        try:
            exam = datetime.strptime(str(exam_date).strip(), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Exam date must use YYYY-MM-DD format.") from exc
    if exam < date.today():
        raise ValueError("Exam date cannot be in the past.")
    parse_start_time(start_time)
    return cleaned, exam


def ai_recommendations(difficulty: Dict[str, int], days_left: int) -> list[str]:
    """Return transparent, rule-based study suggestions."""
    tips: list[str] = []
    if difficulty:
        hardest = max(difficulty, key=difficulty.get)
        tips.append(f"Give extra attention to {hardest} (difficulty {difficulty[hardest]}/5).")
    if days_left <= 3:
        tips.append("Prioritise revision and practice questions; avoid starting large new topics.")
    elif days_left <= 7:
        tips.append("Use the remaining days for focused practice and active recall.")
    else:
        tips.append("Revise difficult subjects regularly instead of leaving them until the end.")
    tips.append("Take short breaks between focused study sessions.")
    tips.append("Finish each session by recalling key points without looking at your notes.")
    return tips


def create_plan(
    subjects: Sequence[str],
    hours: float,
    exam_date: str | date,
    difficulty: Dict[str, int],
    start_time: str = "8:00 AM",
    break_minutes: int = 10,
    days_left: int | None = None,
) -> list[dict]:
    """Create a date-wise plan containing individual, trackable study sessions."""
    cleaned, exam = validate_inputs(subjects, hours, exam_date, difficulty, break_minutes, start_time)
    today = date.today()
    study_days = (exam - today).days

    if study_days == 0:
        return [{
            "date": today.isoformat(),
            "title": "Exam day",
            "sessions": [{
                "subject": "Final quick review",
                "duration_minutes": min(60, int(hours * 60)),
                "start": start_time,
                "end": "",
                "task": "Review key formulas, definitions and prepared notes.",
                "is_revision": True,
            }],
        }]

    start = parse_start_time(start_time)
    total_minutes = int(round(hours * 60))
    # A minimum of 15 minutes per subject keeps small schedules practical.
    session_count = min(3, len(cleaned))
    selected = sorted(cleaned, key=lambda s: difficulty[s], reverse=True)
    days: list[dict] = []

    for day_index in range(study_days):
        current = today + timedelta(days=day_index)
        is_final_revision = day_index == study_days - 1
        if is_final_revision:
            revision_subjects = selected
            durations = _allocate_minutes(total_minutes, revision_subjects, difficulty)
            sessions = []
            cursor = datetime.combine(current, start)
            for subject, duration in zip(revision_subjects, durations):
                end = cursor + timedelta(minutes=duration)
                sessions.append({
                    "subject": subject,
                    "duration_minutes": duration,
                    "start": cursor.strftime("%I:%M %p"),
                    "end": end.strftime("%I:%M %p"),
                    "task": "Final revision: recall key concepts and solve important questions.",
                    "is_revision": True,
                })
                cursor = end + timedelta(minutes=break_minutes)
            days.append({
                "date": current.isoformat(),
                "title": "Final revision day",
                "sessions": sessions,
            })
            continue

        # Rotate through all subjects; up to three are scheduled each day.
        offset = (day_index * session_count) % len(selected)
        daily_subjects = [selected[(offset + i) % len(selected)] for i in range(session_count)]
        durations = _allocate_minutes(total_minutes, daily_subjects, difficulty)
        sessions = []
        cursor = datetime.combine(current, start)
        for subject, duration in zip(daily_subjects, durations):
            end = cursor + timedelta(minutes=duration)
            sessions.append({
                "subject": subject,
                "duration_minutes": duration,
                "start": cursor.strftime("%I:%M %p"),
                "end": end.strftime("%I:%M %p"),
                "task": _task_for_rating(difficulty[subject]),
                "is_revision": False,
            })
            cursor = end + timedelta(minutes=break_minutes)
        days.append({
            "date": current.isoformat(),
            "title": "Study day",
            "sessions": sessions,
        })
    return days


def _allocate_minutes(total: int, subjects: Sequence[str], difficulty: Dict[str, int]) -> list[int]:
    if not subjects:
        return []
    weights = [max(1, difficulty[s]) for s in subjects]
    weight_total = sum(weights)
    raw = [total * weight / weight_total for weight in weights]
    allocated = [int(value) for value in raw]
    remainder = total - sum(allocated)
    for index in range(remainder):
        allocated[index % len(allocated)] += 1
    # If there are enough minutes, avoid zero-minute sessions.
    if total >= 15 * len(subjects):
        for i, value in enumerate(allocated):
            if value < 15:
                deficit = 15 - value
                donor = max(range(len(allocated)), key=lambda j: allocated[j])
                if allocated[donor] - deficit >= 15:
                    allocated[donor] -= deficit
                    allocated[i] += deficit
    return allocated


def _task_for_rating(rating: int) -> str:
    if rating >= 4:
        return "Study a difficult topic, make concise notes and solve practice questions."
    if rating == 3:
        return "Understand the main concepts and practise representative questions."
    return "Review fundamentals and complete a short practice set."


def flatten_sessions(plan: Iterable[dict]) -> list[dict]:
    """Return all sessions in display order."""
    return [session for day in plan for session in day.get("sessions", [])]
