subjects = input("Enter subjects separated by commas: ")
subject_list = subjects.split(",")
difficulty = {}

for subject in subject_list:
    level = int(input(f"Enter difficulty for {subject.strip()} (1-5): "))
    difficulty[subject.strip()] = level
    print("\nSUBJECT DIFFICULTIES")

for subject, level in difficulty.items():
    print(subject, ":", level)

hours = int(input("Enter study hours per day: "))

#print(subject_list)
#print(hours)

from planner import create_plan
#subjects = input("Enter subjects separated by commas: ")
#subject_list = subjects.split(",")
#hours = int(input("Enter study hours per day: "))

plan = create_plan(subject_list, hours,difficulty)

print("\nTODAY'S STUDY PLAN")
for item in plan:
    print(item)

    #subjects = input("Enter subjects separated by commas: ")

#subject_list = subjects.split(",")

#for s in subject_list:
    #print("-", s.strip())
    #print("\nTotal hours:", hours)

    #n = len(subject_list)
#hours_per_subject = hours // n

#print("\nDAILY STUDY PLAN")
#for s in subject_list:
    #print(f"{s} - {hours_per_subject} hrs")
#if hours < len(subject_list):
   # print("study hour are less than the number of subjects.")
#else:
    #hours_per_subject = hours // len(subject_list)

from datetime import datetime

exam_date = input("Enter exam date (YYYY-MM-DD): ")

exam = datetime.strptime(exam_date, "%Y-%m-%d")
today = datetime.today()

days_left = (exam - today).days

print("Days left until exam:", days_left)
print("\nSTUDY SCHEDULE")

for day in range(1, days_left + 1):
    if day == days_left:
       print(f"\nDay {day}")
       print("REVISION DAY")
    else:
        print(f"\nDay {day}")

        for subject in subject_list:
            print("-", subject.strip())

with open("study_plan.txt", "w") as file:
    file.write("TODAY'S STUDY PLAN\n\n")
    for item in plan:
        file.write(item + "\n")
        print("Study plan saved to study_plan.txt")