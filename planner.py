
def ai_recommendations(difficulty, days_left):

    tips = []

    if difficulty:
        hardest = max(difficulty, key=difficulty.get)

        tips.append(
            f"Focus more on {hardest} "
            f"(Difficulty: {difficulty[hardest]})"
        )

    if days_left <= 3:
        tips.append(
            "Revise only. Avoid starting new topics."
        )
    else:
        tips.append(
            "Revise difficult subjects every alternate day."
        )

    tips.append(
        "Take a 10-minute break after every 50 minutes of study."
    )

    tips.append(
        "Practice difficult subjects before easy ones."
    )

    return tips


def create_plan(
    subjects,
    hours,
    exam_date,
    difficulty,
    start_time,
    break_minutes,
    days_left
):

    plan = []

    # Convert exam date into a date object
    exam = datetime.strptime(
        exam_date,
        "%Y-%m-%d"
    ).date()

    today = date.today()

    # Do not create a plan for exam day itself
    study_days = (exam - today).days

    if study_days <= 0:
        return [
            "🎓 EXAM DAY",
            "Revise important topics only."
        ]

    # Sort subjects from difficult to easy
    sorted_subjects = sorted(
        subjects,
        key=lambda subject: difficulty.get(
            subject.strip(),
            0
        ),
        reverse=True
    )

    # Start rotating subjects
    rotation = 0

    for day_number in range(study_days):

        current_date = today + timedelta(
            days=day_number
        )

        # Last day before exam = revision day
        if day_number == study_days - 1:

            plan.append(
                f"\n📅 {current_date.strftime('%A, %d %B %Y')}"
            )

            plan.append(
                "🔄 FINAL REVISION DAY"
            )

            plan.append(
                "• Revise difficult subjects"
            )

            plan.append(
                "• Practice important questions"
            )

            plan.append(
                "• Review notes and formulas"
            )

            continue

        # Select 3 rotating subjects
        selected_subjects = []

        for i in range(
            min(3, len(sorted_subjects))
        ):

            subject_index = (
                rotation + i
            ) % len(sorted_subjects)

            selected_subjects.append(
                sorted_subjects[
                    subject_index
                ]
            )

        rotation += 1

        # Calculate total difficulty
        total_difficulty = sum(
            difficulty.get(
                subject.strip(),
                1
            )
            for subject in selected_subjects
        )

        # Date heading
        plan.append(
            f"\n📅 {current_date.strftime('%A, %d %B %Y')}"
        )

        plan.append(
            "-" * 45
        )

        # Give more time to difficult subjects
        for subject in selected_subjects:

            rating = difficulty.get(
                subject.strip(),
                1
            )

            subject_hours = (
                hours *
                rating /
                total_difficulty
            )

            total_minutes = round(
                subject_hours * 60
            )

            subject_hours_part = (
                total_minutes // 60
            )

            subject_minutes_part = (
                total_minutes % 60
            )

            if subject_hours_part > 0:

                time_text = (
                    f"{subject_hours_part} hr "
                )

                if subject_minutes_part > 0:

                    time_text += (
                        f"{subject_minutes_part} min"
                    )

            else:

                time_text = (
                    f"{subject_minutes_part} min"
                )

            if rating >= 4:

                level = "DIFFICULT"

            elif rating >= 3:

                level = "MEDIUM"

            else:

                level = "EASY"

            plan.append(
                f"📘 {subject} "
                f"({level} - Difficulty {rating}) "
                f"→ {time_text}"
            )

    return plan