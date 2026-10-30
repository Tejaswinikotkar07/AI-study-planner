
"""Tkinter desktop interface for AI Study Planner."""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from planner import create_plan, ai_recommendations, flatten_sessions
from utils import (
    parse_subjects_and_difficulty,
    parse_positive_hours,
    parse_break_minutes,
    validate_exam_date,
)

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "study_progress.json"
TEXT_FILE = APP_DIR / "study_plan.txt"
PDF_FILE = APP_DIR / "AI_Study_Plan.pdf"


class StudyPlannerApp:
    BG = "#F4F6F9"
    NAVY = "#17365D"
    BLUE = "#2463A6"
    GREEN = "#218838"
    WHITE = "#FFFFFF"
    TEXT = "#263445"
    MUTED = "#667085"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Study Planner")
        self.root.geometry("1000x820")
        self.root.minsize(850, 650)
        self.root.configure(bg=self.BG)

        self.plan: list[dict] = []
        self.difficulty: dict[str, int] = {}
        self.notes = ""
        self.exam_date = ""
        self.days_left = 0
        self.session_vars: list[tk.BooleanVar] = []
        self.session_records: list[dict] = []

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("TProgressbar", troughcolor="#E3E8EF", background=self.GREEN, thickness=16)
        self.style.configure("TCombobox", padding=5)

        self._build_input_page()
        self._build_result_page()
        self.show_input_page()

    def _header(self, parent: tk.Widget, title: str, subtitle: str) -> None:
        tk.Label(parent, text=title, font=("Arial", 24, "bold"), bg=self.BG,
                 fg=self.NAVY).pack(pady=(18, 4))
        tk.Label(parent, text=subtitle, font=("Arial", 11), bg=self.BG,
                 fg=self.MUTED).pack(pady=(0, 14))

    def _build_input_page(self) -> None:
        self.input_page = tk.Frame(self.root, bg=self.BG)
        self._header(self.input_page, "AI STUDY PLANNER", "Create a practical, date-wise study timetable")

        card = tk.LabelFrame(
            self.input_page, text=" Student Details ", font=("Arial", 11, "bold"),
            bg=self.WHITE, fg=self.NAVY, padx=22, pady=15, bd=1, relief="solid",
        )
        card.pack(fill="both", expand=True, padx=28, pady=(4, 12))
        card.columnconfigure(1, weight=1)

        self.subject_entry = self._entry_row(card, 0, "Subjects", "Mathematics, Science, English")
        self.difficulty_entry = self._entry_row(card, 1, "Difficulty (Subject:Rating)", "Mathematics:5, Science:4, English:2")
        self.hours_entry = self._entry_row(card, 2, "Study hours per day", "4")
        self.date_entry = self._entry_row(card, 3, "Exam date (YYYY-MM-DD)", datetime.today().date().isoformat())

        tk.Label(card, text="Study start time", bg=self.WHITE, fg=self.TEXT,
                 font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=(4, 18), pady=9)
        self.start_combo = ttk.Combobox(
            card, values=[f"{hour}:00 {period}" for period in ("AM", "PM") for hour in range(1, 13)],
            width=18, state="readonly",
        )
        self.start_combo.set("8:00 AM")
        self.start_combo.grid(row=4, column=1, sticky="w", pady=9)

        self.break_entry = self._entry_row(card, 5, "Break between sessions (minutes)", "10")

        tk.Label(card, text="Notes / topics to focus on", bg=self.WHITE, fg=self.TEXT,
                 font=("Arial", 10)).grid(row=6, column=0, sticky="nw", padx=(4, 18), pady=9)
        self.notes_text = tk.Text(card, height=3, width=55, font=("Arial", 10),
                                  relief="solid", bd=1, wrap="word")
        self.notes_text.grid(row=6, column=1, sticky="ew", pady=9)

        hint = ("Enter difficulty ratings from 1 (easy) to 5 (difficult). "
                "Use the same subject names in both fields.")
        tk.Label(card, text=hint, bg=self.WHITE, fg=self.MUTED,
                 font=("Arial", 9), wraplength=650, justify="left").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=4, pady=(8, 0)
        )

        # The action is outside the expanding card and always visible.
        action_bar = tk.Frame(self.input_page, bg=self.BG)
        action_bar.pack(fill="x", padx=28, pady=(0, 18))
        self.generate_button = tk.Button(
            action_bar, text="GENERATE STUDY PLAN", command=self.generate_plan,
            font=("Arial", 12, "bold"), bg=self.GREEN, fg=self.WHITE,
            activebackground="#176B2C", activeforeground=self.WHITE,
            relief="flat", padx=28, pady=12, cursor="hand2",
        )
        self.generate_button.pack()
        tk.Label(action_bar, text="You can mark sessions complete after generating your plan.",
                 bg=self.BG, fg=self.MUTED, font=("Arial", 9)).pack(pady=(6, 0))

    def _entry_row(self, parent: tk.Widget, row: int, label: str, default: str) -> tk.Entry:
        tk.Label(parent, text=label, bg=self.WHITE, fg=self.TEXT,
                 font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=(4, 18), pady=9)
        entry = tk.Entry(parent, font=("Arial", 10), relief="solid", bd=1)
        entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", pady=9, ipady=5)
        return entry

    def _build_result_page(self) -> None:
        self.result_page = tk.Frame(self.root, bg=self.BG)
        self._header(self.result_page, "YOUR STUDY PLAN", "Complete each session to update your daily progress")

        top = tk.Frame(self.result_page, bg=self.BG)
        top.pack(fill="x", padx=25, pady=(0, 8))
        self.summary_label = tk.Label(top, text="", bg=self.BG, fg=self.TEXT,
                                      font=("Arial", 10, "bold"), justify="left")
        self.summary_label.pack(anchor="w")

        progress_box = tk.Frame(self.result_page, bg=self.WHITE, padx=15, pady=10,
                                highlightbackground="#D8DEE8", highlightthickness=1)
        progress_box.pack(fill="x", padx=25, pady=(0, 10))
        self.progress_label = tk.Label(progress_box, text="Overall progress: 0%",
                                       bg=self.WHITE, fg=self.NAVY, font=("Arial", 10, "bold"))
        self.progress_label.pack(anchor="w")
        self.progress = ttk.Progressbar(progress_box, maximum=100, mode="determinate")
        self.progress.pack(fill="x", pady=(6, 0))

        content = tk.Frame(self.result_page, bg=self.BG)
        content.pack(fill="both", expand=True, padx=25, pady=4)
        self.session_canvas = tk.Canvas(content, bg=self.WHITE, highlightthickness=1,
                                        highlightbackground="#D8DEE8")
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.session_canvas.yview)
        self.session_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.session_canvas.pack(side="left", fill="both", expand=True)
        self.session_inner = tk.Frame(self.session_canvas, bg=self.WHITE)
        self.canvas_window = self.session_canvas.create_window((0, 0), window=self.session_inner, anchor="nw")
        self.session_inner.bind("<Configure>", self._update_scroll_region)
        self.session_canvas.bind("<Configure>", self._resize_inner)

        self.recommendation_label = tk.Label(self.result_page, text="", bg=self.BG,
                                             fg=self.MUTED, justify="left",
                                             font=("Arial", 9), wraplength=900)
        self.recommendation_label.pack(fill="x", padx=28, pady=(6, 4))

        buttons = tk.Frame(self.result_page, bg=self.BG)
        buttons.pack(pady=(4, 14))
        self._button(buttons, "Save TXT", self.save_txt, self.BLUE).grid(row=0, column=0, padx=5)
        self._button(buttons, "Export PDF", self.export_pdf, "#B42318").grid(row=0, column=1, padx=5)
        self._button(buttons, "Show Chart", self.show_chart, "#6941C6").grid(row=0, column=2, padx=5)
        self._button(buttons, "Back", self.show_input_page, "#667085").grid(row=0, column=3, padx=5)

    def _button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg=self.WHITE,
                         activeforeground=self.WHITE, relief="flat", padx=14, pady=8,
                         font=("Arial", 9, "bold"), cursor="hand2")

    def _update_scroll_region(self, _event=None):
        self.session_canvas.configure(scrollregion=self.session_canvas.bbox("all"))

    def _resize_inner(self, event):
        self.session_canvas.itemconfigure(self.canvas_window, width=event.width)

    def show_input_page(self):
        self.result_page.pack_forget()
        self.input_page.pack(fill="both", expand=True)

    def show_result_page(self):
        self.input_page.pack_forget()
        self.result_page.pack(fill="both", expand=True)

    def generate_plan(self):
        try:
            subjects, difficulty = parse_subjects_and_difficulty(
                self.subject_entry.get(), self.difficulty_entry.get()
            )
            hours = parse_positive_hours(self.hours_entry.get())
            break_minutes = parse_break_minutes(self.break_entry.get())
            exam_date = validate_exam_date(self.date_entry.get())
            start_time = self.start_combo.get()
            notes = self.notes_text.get("1.0", "end").strip()

            self.plan = create_plan(
                subjects=subjects,
                hours=hours,
                exam_date=exam_date,
                difficulty=difficulty,
                start_time=start_time,
                break_minutes=break_minutes,
            )
        except ValueError as exc:
            messagebox.showerror("Check your details", str(exc), parent=self.root)
            return
        except Exception as exc:
            messagebox.showerror("Unable to generate plan", f"Unexpected error: {exc}", parent=self.root)
            return

        self.difficulty = difficulty
        self.notes = notes
        self.exam_date = exam_date
        self.days_left = (datetime.strptime(exam_date, "%Y-%m-%d").date() - datetime.today().date()).days
        self._render_sessions()
        self.summary_label.config(
            text=f"Exam date: {exam_date}    |    Days remaining: {self.days_left}    |    "
                 f"Study time per day: {hours:g} hours"
        )
        tips = ai_recommendations(difficulty, self.days_left)
        self.recommendation_label.config(text="STUDY TIPS  •  " + "   •   ".join(tips))
        self.show_result_page()

    def _render_sessions(self):
        for child in self.session_inner.winfo_children():
            child.destroy()
        self.session_vars = []
        self.session_records = []

        for day in self.plan:
            heading = tk.Frame(self.session_inner, bg="#EAF0F7", padx=12, pady=8)
            heading.pack(fill="x", padx=10, pady=(10, 3))
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            tk.Label(heading, text=f"{date_obj.strftime('%A, %d %B %Y')}  —  {day['title']}",
                     bg="#EAF0F7", fg=self.NAVY, font=("Arial", 10, "bold")).pack(anchor="w")

            for session in day["sessions"]:
                var = tk.BooleanVar(value=False)
                self.session_vars.append(var)
                self.session_records.append(session)
                row = tk.Frame(self.session_inner, bg=self.WHITE, padx=14, pady=8)
                row.pack(fill="x", padx=10, pady=2)
                time_text = f"{session['start']} – {session['end']}  |  " if session["end"] else ""
                duration = session["duration_minutes"]
                label = (f"{time_text}{session['subject']}  |  {duration} min\n"
                         f"{session['task']}")
                check = tk.Checkbutton(
                    row, text=label, variable=var, command=self.update_progress,
                    bg=self.WHITE, fg=self.TEXT, activebackground=self.WHITE,
                    selectcolor="#E8F5E9", font=("Arial", 9), justify="left",
                    anchor="w", wraplength=820,
                )
                check.pack(fill="x", anchor="w")

        self.update_progress()

    def update_progress(self):
        total = len(self.session_vars)
        completed = sum(var.get() for var in self.session_vars)
        percent = round((completed / total) * 100) if total else 0
        self.progress["value"] = percent
        self.progress_label.config(text=f"Overall progress: {percent}%  ({completed}/{total} sessions completed)")
        self._save_progress_silently()

    def _save_progress_silently(self):
        if not self.session_vars:
            return
        data = {
            "exam_date": self.exam_date,
            "completed": [bool(var.get()) for var in self.session_vars],
        }
        try:
            DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _report_text(self) -> str:
        lines = [
            "AI STUDY PLANNER",
            "=" * 60,
            f"Exam date: {self.exam_date}",
            f"Days remaining: {self.days_left}",
            "",
            "STUDY RECOMMENDATIONS",
        ]
        lines.extend(f"- {tip}" for tip in ai_recommendations(self.difficulty, self.days_left))
        lines += ["", "DATE-WISE STUDY PLAN"]
        index = 0
        for day in self.plan:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            lines += ["", f"{date_obj.strftime('%A, %d %B %Y')} — {day['title']}"]
            for session in day["sessions"]:
                done = self.session_vars[index].get() if index < len(self.session_vars) else False
                status = "COMPLETED" if done else "NOT COMPLETED"
                lines.append(
                    f"[{status}] {session['start']}–{session['end']} | "
                    f"{session['subject']} | {session['duration_minutes']} min"
                )
                lines.append(f"  Task: {session['task']}")
                index += 1
        if self.notes:
            lines += ["", "NOTES / TOPICS", self.notes]
        return "\n".join(lines) + "\n"

    def save_txt(self):
        try:
            TEXT_FILE.write_text(self._report_text(), encoding="utf-8")
            messagebox.showinfo("Saved", f"Study plan saved to:\n{TEXT_FILE}", parent=self.root)
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc), parent=self.root)

    def export_pdf(self):
        try:
            path = filedialog.asksaveasfilename(
                parent=self.root, defaultextension=".pdf",
                initialfile="AI_Study_Plan.pdf",
                filetypes=[("PDF files", "*.pdf")],
            )
            if not path:
                return
            pdf = canvas.Canvas(path, pagesize=A4)
            width, height = A4
            y = height - 48
            for line in self._report_text().splitlines():
                if y < 48:
                    pdf.showPage()
                    y = height - 48
                # Basic PDF fonts do not support all emoji; replace unsupported glyphs safely.
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.setFont("Helvetica", 9)
                pdf.drawString(42, y, safe_line[:115])
                y -= 14
            pdf.save()
            messagebox.showinfo("Exported", f"PDF exported to:\n{path}", parent=self.root)
        except Exception as exc:
            messagebox.showerror("PDF export failed", str(exc), parent=self.root)

    def show_chart(self):
        if not self.difficulty:
            messagebox.showwarning("No data", "Generate a study plan first.", parent=self.root)
            return
        window = tk.Toplevel(self.root)
        window.title("Subject Difficulty")
        window.geometry("620x500")
        figure = Figure(figsize=(6, 4.5), dpi=100)
        axis = figure.add_subplot(111)
        subjects = list(self.difficulty)
        ratings = [self.difficulty[name] for name in subjects]
        axis.bar(subjects, ratings)
        axis.set_title("Subject Difficulty Ratings")
        axis.set_ylabel("Difficulty (1–5)")
        axis.set_ylim(0, 5.5)
        axis.tick_params(axis="x", rotation=20)
        figure.tight_layout()
        chart = FigureCanvasTkAgg(figure, master=window)
        chart.draw()
        chart.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


def main():
    root = tk.Tk()
    StudyPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
