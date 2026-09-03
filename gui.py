from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime,date,timedelta
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

from planner import create_plan, ai_recommendations

# ---------------- MAIN WINDOW ---------------- #

root = Tk()
root.title("AI Study Planner")
root.geometry("900x700")
root.configure(bg="#F4F6F9")
root.resizable(False, False)

progress_value = IntVar()
completed_var = IntVar()

# ---------------- PAGES ---------------- #

input_frame = Frame(root, bg="#F4F6F9")
result_frame = Frame(root, bg="#F4F6F9")

input_frame.pack(fill="both", expand=True)

def save_plan():
    content = output.get("1.0", END)

    with open("study_plan.txt", "w") as file:
        file.write(content)

    messagebox.showinfo("Success", "Study Plan saved successfully!")

def export_pdf():
    content = output.get("1.0", END)

    pdf = canvas.Canvas("AI_Study_Plan.pdf")
    y = 800

    for line in content.split("\n"):
        pdf.drawString(40, y, line)
        y -= 20

    pdf.save()

    messagebox.showinfo("Success", "PDF exported successfully!")

def back():
    result_frame.pack_forget()
    input_frame.pack(fill="both", expand=True)
    output.delete("1.0", END)

def show_chart():
    difficulty = {}

    difficulty_text = difficulty_entry.get().strip()

    for item in difficulty_text.split(","):
        subject, rating = item.split(":")
        difficulty[subject.strip()] = int(rating)

    labels = list(difficulty.keys())
    sizes = list(difficulty.values())

    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Difficulty Distribution")
    plt.axis("equal")
    plt.show()

def generate_plan():
    print("step 2")

    output.delete("1.0", END)
    output.insert(END, "📚 AI STUDY PLAN\n")
    output.insert(END, "=" * 50 + "\n\n")

    

    notes = notes_entry.get("1.0", END)
    subjects = subjects_entry.get().strip()
    hours_text = hours_entry.get().strip()
    exam_date = exam_entry.get().strip()

    difficulty_text = difficulty_entry.get().strip()

    study_start = start_time.get()
    break_minutes = int(break_entry.get())

    if completed_var.get():
        progress_value.set(100)
    else:
        progress_value.set(0)


    if not subjects or not hours or not difficulty_text:
        messagebox.showerror(
            "Error",
            "Please fill all fields."
        )
        return

    try:
        hours = float(hours)
    except ValueError:
        messagebox.showerror(
            "Error",
            "Study hours must be numeric."
        )
        return
    try:
        break_minutes = int(break_minutes)
    except ValueError:
        messagebox.showerror("Error", "Break time must be a number.")
        return
    try:
        exam = datetime.strptime(exam_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid exam date.")
        return
    

    days_left = (exam - datetime.today()).days

    if days_left < 0:
        messagebox.showerror(
            "Error",
            "Exam date has already passed."
        )
        return

    difficulty = {}

    for item in difficulty_text.split(","):

        subject,rating = item.split(":")
        difficulty[subject.strip()] = int(rating)

    subjects_list = [s.strip() for s in subjects.split(",")]
    print("step  3")

    plan = create_plan(
        subjects_list,
        hours,exam_date,
        difficulty,start_time,break_minutes,days_left
    )

    output.insert(
        END,
        "=========== AI STUDY PLANNER ===========\n\n"
    )

    output.insert(
        END,
        f"Exam Date : {exam_date}\n"
    )

    output.insert(
        END,
        f"Days Remaining : {days_left}\n\n"
    )

    output.insert(
        END,
        "AI RECOMMENDATIONS\n"
    )

    output.insert(
        END,
        "------------------------------\n"
    )

    tips = ai_recommendations(
        difficulty,
        days_left
    )

    for tip in tips:
        output.insert(
            END,
            "• "+tip+"\n"
        )

    output.insert(
        END,
        "\nDifficulty Ratings\n"
    )
    output.insert(
        END,
        "------------------------------\n"
    )

    for subject,rating in sorted(
        difficulty.items(),
        key=lambda x:x[1],
        reverse=True
    ):

        output.insert(
            END,
            f"{subject} {'⭐'*rating}\n"
        )

    output.insert(
        END,
        "\nStudy Plan\n"
    )

    output.insert(
        END,
        "------------------------------\n"
    )

    for item in plan:
        output.insert(
            END,
            item+"\n"
        )

    output.insert(
        END,
        "\nNotes\n"
    )

    output.insert(
        END,
        "------------------------------\n"
    )

    output.insert(
        END,
        notes
    )

    if completed_var.get():
        output.insert(
            END,
            "\nProgress : 100%\n"
        )
    else:
        output.insert(
            END,
            "\nProgress : Incomplete\n"
        )
        print("step 4")

    input_frame.pack_forget()

    result_frame.pack(
        fill="both",
        expand=True
    )
    print("step 5")

    # ===========================
# TITLE
# ===========================

title = Label(
    input_frame,
    text="AI STUDY PLANNER",
    font=("Arial", 22, "bold"),
    bg="#F4F6F9",
    fg="#003366"
)
title.pack(pady=15)

# ===========================
# INPUT SECTION
# ===========================

details_frame = LabelFrame(
    input_frame,
    text="Student Details",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=20,
    bg="white"
)

details_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)

# Subjects

Label(
    details_frame,
    text="Subjects",
    bg="white",
    font=("Arial",11)
).grid(row=0,column=0,sticky="w",pady=8)

subjects_entry = Entry(
    details_frame,
    width=45,
    font=("Arial",11)
)

subjects_entry.grid(
    row=0,
    column=1,
    padx=10
)

# Difficulty

Label(
    details_frame,
    text="Difficulty",
    bg="white",
    font=("Arial",11)
).grid(row=1,column=0,sticky="w",pady=8)

difficulty_entry = Entry(
    details_frame,
    width=45,
    font=("Arial",11)
)

difficulty_entry.grid(
    row=1,
    column=1,
    padx=10
)

# Hours

Label(
    details_frame,
    text="Study Hours",
    bg="white",
    font=("Arial",11)
).grid(row=2,column=0,sticky="w",pady=8)

hours_entry = Entry(
    details_frame,
    width=20,
    font=("Arial",11)
)

hours_entry.grid(
    row=2,
    column=1,
    sticky="w",
    padx=10
)

# Exam Date

Label(
    details_frame,
    text="Exam Date",
    bg="white",
    font=("Arial",11)
).grid(row=3,column=0,sticky="w",pady=8)

exam_entry = DateEntry(
    details_frame,
    width=18,
    date_pattern="yyyy-mm-dd",
    font=("Arial",11)
)

exam_entry.grid(
    row=3,
    column=1,
    sticky="w",
    padx=10
)
# Study Start Time

Label(
    details_frame,
    text="Study Start Time",
    bg="white",
    font=("Arial",11)
).grid(row=4, column=0, sticky="w", pady=8)

start_time = ttk.Combobox(
    details_frame,
    values=[
        "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM",
        "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM",
        "4:00 PM", "5:00 PM", "6:00 PM",
        "7:00 PM", "8:00 PM", "9:00 PM"
    ],
    width=18,
    state="readonly"
)

start_time.current(2)

start_time.grid(
    row=4,
    column=1,
    sticky="w",
    padx=10
)




# Break Time

Label(
    details_frame,
    text="Break (minutes)",
    bg="white",
    font=("Arial",11)
).grid(row=5, column=0, sticky="w", pady=8)

break_entry = Entry(
    details_frame,
    width=20,
    font=("Arial",11)
)

break_entry.insert(0, "10")

break_entry.grid(
    row=5,
    column=1,
    sticky="w",
    padx=10
)

# Notes

Label(
    details_frame,
    text="Notes",
    bg="white",
    font=("Arial",11)
).grid(row=6,column=0,sticky="nw",pady=10,padx=10)

notes_entry = Text(
    details_frame,
    width=40,
    height=3,
    font=("Arial",11)
)

notes_entry.grid(
    row=6,
    column=1,
    padx=10,
    pady=5
)

# Checkbox

Checkbutton(
    details_frame,
    text="Today's Study Completed",
    variable=completed_var,
    bg="white",
    font=("Arial",11)
).grid(
    row=7,
    column=1,
    sticky="w",
    pady=10
)

# Progress

progress = ttk.Progressbar(
    details_frame,
    orient="horizontal",
    length=300,
    mode="determinate",
    maximum=100,
    variable=progress_value
)

progress.grid(
    row=8,
    column=1,
    sticky="w",
    pady=10
)

# Generate Button

Button(
    input_frame,
    text="Generate Study Plan",
    command=generate_plan,
    font=("Arial",12,"bold"),
    bg="#28A745",
    fg="white",
    padx=20,
    pady=8
).pack(pady=20)

# ==========================================
# RESULT PAGE TITLE
# ==========================================

result_title = Label(
    result_frame,
    text="STUDY PLAN",
    font=("Arial", 22, "bold"),
    bg="#F4F6F9",
    fg="#003366"
)

result_title.pack(pady=15)

# ==========================================
# OUTPUT BOX
# ==========================================

output_frame = LabelFrame(
    result_frame,
    text="Generated Study Plan",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=10,
    pady=10
)

output_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

scrollbar = Scrollbar(output_frame)

scrollbar.pack(
    side=RIGHT,
    fill=Y
)

output = Text(
    output_frame,
    width=95,
    height=25,
    font=("Consolas",11),
    wrap=WORD,
    yscrollcommand=scrollbar.set
)

output.pack(
    side=LEFT,
    fill=BOTH,
    expand=True
)

scrollbar.config(command=output.yview)

# ==========================================
# BUTTONS
# ==========================================

button_frame = Frame(
    result_frame,
    bg="#F4F6F9"
)

button_frame.pack(pady=15)

Button(
    button_frame,
    text="💾 Save Plan",
    command=save_plan,
    bg="#007BFF",
    fg="white",
    width=15,
    font=("Arial",11,"bold")
).grid(row=0,column=0,padx=10)

Button(
    button_frame,
    text="📄 Export PDF",
    command=export_pdf,
    bg="#DC3545",
    fg="white",
    width=15,
    font=("Arial",11,"bold")
).grid(row=0,column=1,padx=10)

Button(
    button_frame,
    text="📊 Show Chart",
    command=show_chart,
    bg="#6F42C1",
    fg="white",
    width=15,
    font=("Arial",11,"bold")
).grid(row=0,column=2,padx=10)

Button(
    button_frame,
    text="⬅ Back",
    command=back,
    bg="#6C757D",
    fg="white",
    width=15,
    font=("Arial",11,"bold")
).grid(row=0,column=3,padx=10)

def back():
    result_frame.pack_forget()
    input_frame.pack(fill="both",expand=True)
    output.delete("1.0", END)
    
root.mainloop()