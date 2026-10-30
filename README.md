# AI Study Planner

A desktop study-planning application built with Python and Tkinter.

## Features

- Date-wise study timetable based on the exam date.
- Subject difficulty ratings from 1 (easy) to 5 (difficult).
- Study-hour allocation weighted toward harder subjects.
- Custom start time and break duration.
- Up to three rotating subject sessions per study day.
- Final revision day before the exam.
- Individual session checkboxes and automatic progress percentage.
- Save the plan as a text file and export it as a PDF.
- Subject difficulty chart.
- Input validation with clear error messages.
- Light-themed Tkinter interface.

**Note:** The recommendations are rule-based. The app does not call an external AI service or require an API key.

## Requirements

- Python 3.10 or newer
- Tkinter (included with most Windows Python installations)
- Packages in `requirements.txt`

## Setup on Windows

1. Extract the ZIP file.
2. Open the extracted `AI_Study_Planner_Final` folder in VS Code.
3. Open Terminal in VS Code.
4. Run:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python gui.py
   ```

   Or run `python main.py`.

## Entering details

- **Subjects:** `Mathematics, Science, English`
- **Difficulty:** `Mathematics:5, Science:4, English:2`
- **Study hours:** for example `4` or `2.5`
- **Exam date:** `YYYY-MM-DD`
- **Study start time:** choose from the drop-down.
- **Break:** whole number of minutes.

The subject names in the Subjects and Difficulty fields must match (capitalisation does not matter).

## Progress tracking

The Generate button is visible at the bottom of the input page. Generate the timetable first. On the results page, tick a session only after completing it. Progress is calculated from completed sessions, not from a pre-study checkbox.

## Files created by the app

- `study_plan.txt` — saved text report.
- `AI_Study_Plan.pdf` — PDF export (choose the destination in the save dialog).
- `study_progress.json` — session completion state for the current generated plan.

## Project structure

```text
AI_Study_Planner_Final/
├── gui.py
├── main.py
├── planner.py
├── utils.py
├── requirements.txt
└── README.md
```
