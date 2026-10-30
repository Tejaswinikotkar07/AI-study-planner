"""Validation and small helper functions used by the GUI."""
from __future__ import annotations

from datetime import datetime


def parse_subjects_and_difficulty(subject_text: str, difficulty_text: str) -> tuple[list[str], dict[str, int]]:
    subjects = [item.strip() for item in subject_text.split(",") if item.strip()]
    if not subjects:
        raise ValueError("Enter subjects separated by commas.")
    if len({item.casefold() for item in subjects}) != len(subjects):
        raise ValueError("Please remove duplicate subject names.")

    ratings: dict[str, int] = {}
    if not difficulty_text.strip():
        raise ValueError("Enter difficulty as Subject:Rating, for example Mathematics:5.")

    for item in difficulty_text.split(","):
        if ":" not in item:
            raise ValueError(f"Invalid difficulty entry '{item.strip()}'. Use Subject:Rating.")
        subject, rating_text = item.rsplit(":", 1)
        subject = subject.strip()
        if not subject:
            raise ValueError("A difficulty entry has an empty subject name.")
        try:
            rating = int(rating_text.strip())
        except ValueError as exc:
            raise ValueError(f"Difficulty for {subject} must be a whole number from 1 to 5.") from exc
        if not 1 <= rating <= 5:
            raise ValueError(f"Difficulty for {subject} must be between 1 and 5.")
        if subject.casefold() in {key.casefold() for key in ratings}:
            raise ValueError(f"Difficulty for {subject} was entered more than once.")
        ratings[subject] = rating

    missing = [subject for subject in subjects if subject.casefold() not in {key.casefold() for key in ratings}]
    extra = [name for name in ratings if name.casefold() not in {subject.casefold() for subject in subjects}]
    if missing:
        raise ValueError("Missing difficulty rating for: " + ", ".join(missing))
    if extra:
        raise ValueError("Difficulty contains subjects not listed above: " + ", ".join(extra))

    # Normalise rating keys to match the exact subject spelling in the subjects field.
    normalised = {}
    for subject in subjects:
        matched = next(key for key in ratings if key.casefold() == subject.casefold())
        normalised[subject] = ratings[matched]
    return subjects, normalised


def parse_positive_hours(value: str) -> float:
    try:
        hours = float(value.strip())
    except (ValueError, AttributeError) as exc:
        raise ValueError("Study hours must be a number, such as 4 or 2.5.") from exc
    if not 0 < hours <= 24:
        raise ValueError("Study hours must be greater than 0 and no more than 24.")
    return hours


def parse_break_minutes(value: str) -> int:
    try:
        minutes = int(value.strip())
    except (ValueError, AttributeError) as exc:
        raise ValueError("Break time must be a whole number.") from exc
    if not 0 <= minutes <= 180:
        raise ValueError("Break time must be between 0 and 180 minutes.")
    return minutes


def validate_exam_date(value: str) -> str:
    try:
        parsed = datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError) as exc:
        raise ValueError("Choose a valid exam date.") from exc
    if parsed < datetime.today().date():
        raise ValueError("Exam date cannot be in the past.")
    return parsed.isoformat()
