import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import csv

# Define the Student class
class Student:
    # init to allow the student to have all needed information
    def __init__(self, name, frees, grade, free_number):
        self.name = name
        self.frees = frees
        self.grade = grade
        self.free_number = free_number

    # allows the student object to print
    def __repr__(self):
        return f"{self.name} (Grade: {self.grade}, Free Periods: {self.frees})"

# Define the Workjob class
class Workjob:
    # init to allow the workjob to store all relevant information and calls the classify function
    def __init__(self, name, w_type, min_students, max_students, priority, periods):
        self.name = name
        self.type = w_type
        self.min = min_students
        self.max = max_students
        self.priority = priority
        self.periods = periods
        self.min_period = None
        self.max_period = None
        self.min_total = None
        self.max_total = None
        self.assigned_students = {period: [] for period in periods}  # Keep track of assigned students per period
        self.classify_workjob()

    # function to classify the workjob as type T or E and assign it with proper min and max limits
    def classify_workjob(self):
        if self.type == "T":
            self.min_period = 1
            self.max_period = 1
            self.max_total = self.max
            self.min_total = self.min
        elif self.type == "E":
            self.min_period = self.min  # Min students per period for type E
            self.max_period = self.max  # Max students per period for type E
            self.min_total = len(self.periods) * self.min
            self.max_total = len(self.periods) * self.max
    
    # function to decide whether a student can be assigned to a period; checks period max/min and total max/min
    def can_assign_student_to_period(self, period):
        if len(self.assigned_students[period]) >= self.max_period:
            return False
        total_assigned = sum(len(students) for students in self.assigned_students.values())
        if total_assigned >= self.max_total:
            return False
        return True

    # allows workjob object to print
    def __repr__(self):
        return (f"Workjob: {self.name}, Type: {self.type}, Periods: {self.periods}, Priority: {self.priority}, "
                f"Min Period Requirements: {self.min_period}, Max Period Requirement: {self.max_period}, "
                f"Min Student Total: {self.min_total}, Max Student Total: {self.max_total}")

# Define the period mapping
period_mapping = {
    '1': ['D1B1', 'D2B2', 'D3B3', 'D4B4', 'D5B5', 'D6B6', 'D7B7'],
    '2': ['D1B2', 'D2B3', 'D3B4', 'D4B5', 'D5B6', 'D6B7', 'D7B1'],
    '3': ['D1B3', 'D2B4', 'D3B5', 'D4B6', 'D5B7', 'D6B1', 'D7B2'],
    '4': ['D1B4', 'D2B5', 'D3B6', 'D4B7', 'D5B1', 'D6B2', 'D7B3'],
    'B3': ['D1B3', 'D2B3', 'D3B3', 'D7B3'],
    'B2': ['D1B2', 'D2B2', 'D6B2', 'D7B2'],
    'B4': ['D1B4', 'D2B4', 'D3B4', 'D7B4'],
    'B6': ['D3B6', 'D4B6', 'D5B6', 'D6B6'],
}

# Read student information from CSV and keep all relevant free periods information
def read_student_file(filename):
    students = []
    with open(filename, 'r') as file:
        reader_dict = csv.DictReader(file)
        for row in reader_dict:
            name = row["Full Name"]
            grade = row["Grade"]
            frees = {}
            for block in row.keys():
                if block not in ["Person ID", "Full Name", "Grade"]:
                    frees[block] = int(row[block]) if row[block] != '' else 0
            free_list = [period for period, value in frees.items() if value == 1]
            free_number = len(free_list)
            students.append(Student(name, free_list, grade, free_number))
    return students

# Read workjob information from CSV and keep all relevant information about it
def read_workjob_file(filename):
    workjobs = []
    with open(filename, 'r', encoding='utf-8-sig') as file:
        reader_dict = csv.DictReader(file)
        for row in reader_dict:
            name = row["name"]
            w_type = row["type"]
            min_students = int(row["min"])
            max_students = int(row["max"])
            priority = int(row["priority"])
            periods = []
            elements = [element.strip() for element in row["periods"].split(',')]
            for element in elements:
                if element in period_mapping:
                    periods.extend(period_mapping[element])
                else:
                    periods.append(element)
            workjobs.append(Workjob(name, w_type, min_students, max_students, priority, periods))
    return workjobs

# Assigns students to workjobs based on their free periods and job requirements
def assign_students_to_workjobs(students, workjobs):
    # Initialize variables
    unassigned_students = []
    assignments = []

    # Sort workjobs and students by free periods and priority
    sorted_students = sorted(students, key=lambda x: int(x.free_number))
    workjobs.sort(key=lambda job: job.priority)

    # Attempt to fill all the workjobs up to their minimum totals
    for student in sorted_students:
        assigned = False
        for workjob in workjobs:
            total_assigned = sum(len(students) for students in workjob.assigned_students.values())
            if total_assigned >= workjob.min_total:
                continue
            for period in student.frees:
                if period in workjob.periods and workjob.can_assign_student_to_period(period):
                    workjob.assigned_students[period].append(student.name)
                    assignments.append([workjob.name, period, student.name])
                    assigned = True
                    break
            if assigned:
                break
        if not assigned:
            unassigned_students.append(student)
    
    # Fill remaining periods to meet the minimum number of students
    for workjob in workjobs:
        for period, assigned_students in workjob.assigned_students.items():
            if len(assigned_students) < workjob.min_period:
                for student in unassigned_students:
                    if period in student.frees and workjob.can_assign_student_to_period(period):
                        workjob.assigned_students[period].append(student.name)
                        assignments.append([workjob.name, period, student.name])
                        unassigned_students.remove(student)
                        if len(workjob.assigned_students[period]) >= workjob.min_period:
                            break  
    
    # After minimums are full, start filling up to the max
    remaining_unassigned_students = unassigned_students.copy()
    unassigned_students.clear()  # Clear list before reassigning students
    for student in remaining_unassigned_students:
        assigned = False
        for workjob in workjobs:
            for period in student.frees:
                if period in workjob.periods and workjob.can_assign_student_to_period(period):
                    workjob.assigned_students[period].append(student.name)
                    assignments.append([workjob.name, period, student.name])
                    assigned = True
                    break
            if assigned:
                break
        if not assigned:
            unassigned_students.append(student.name)

    return assignments, unassigned_students

# Display error window for not enough students to fill the minimum workjobs
def show_min_error_window(message):
    messagebox.showerror("Not enough students to fill min workjobs", message)

# Display error window for too many students, exceeding the max workjob limits
def show_max_error_window(message):
    messagebox.showerror("Too many students, over max workjobs", message)

# Check if the number of students meets the min/max workjob requirements
def check_minmax(students, workjobs):
    min_total = sum(workjob.min_total for workjob in workjobs)
    max_total = sum(workjob.max_total for workjob in workjobs)

    if len(students) < min_total:
        show_min_error_window(f"Not enough students: {len(students)}. Minimum required is {min_total}.")
    elif len(students) > max_total:
        show_max_error_window(f"Too many students: {len(students)}. Maximum allowed is {max_total}.")

# initialize global variables to hold the student and workjob data
students = []
workjobs = []

# intialize tkinter
root = tk.Tk()
root.title("Workjob Assignment")
frame = tk.Frame(root)
frame.pack(pady=20)

# function to upload the student CSV
def upload_students():
    global students
    file_path = filedialog.askopenfilename()
    if file_path:
        students = read_student_file(file_path)
        student_button.config(bg="green")  

# function to upload the workjob CSV
def upload_workjobs():
    global workjobs
    file_path = filedialog.askopenfilename()
    if file_path:
        workjobs = read_workjob_file(file_path)
        workjob_button.config(bg="green")  

# function to assign and export workjobs
def assign_and_export():
    check_minmax(students, workjobs)
    if not students or not workjobs:
        messagebox.showerror("Error", "Please upload both student and workjob files before assigning.")
        return
    assignments, unassigned_students = assign_students_to_workjobs(students, workjobs)
    
    # export assignments to CSV
    save_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")], title="Save assignments CSV")
    with open(save_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Workjob", "Period", "Assigned Students"])
        grouped_students = defaultdict(list)
        for job, period, student in assignments:
            grouped_students[(job, period)].append(student)

        workjobs_by_priority = sorted(workjobs, key=lambda w: w.priority)
        for workjob in workjobs_by_priority:
            for period in workjob.periods:
                key = (workjob.name, period)
                if key in grouped_students:
                    grouped_students[key].sort()
                    writer.writerow([workjob.name, period, ', '.join(grouped_students[key])])
                else:
                    writer.writerow([workjob.name, period, "[Empty]"])

    # export unassigned students to a separate CSV 
    if unassigned_students:
        unassigned_save_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")], title="Save unassigned students CSV")
        if unassigned_save_path:
            with open(unassigned_save_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Unassigned Students"])
                for student in unassigned_students:
                    writer.writerow([student])
        else:
            print("\nUnassigned Students:")
            for student in unassigned_students:
                print(f"Student: {student}")
    else:
        print("\nAll students have been assigned.")

#buttons for UI
assign_button = tk.Button(frame, text="Assign Students and Export to CSV", command=assign_and_export)
assign_button.grid(row=1, column=0, columnspan=2, pady=10)

student_button = tk.Button(frame, text="Upload Students CSV", command=upload_students)
student_button.grid(row=0, column=0, padx=10)

workjob_button = tk.Button(frame, text="Upload Workjobs CSV", command=upload_workjobs)
workjob_button.grid(row=0, column=1, padx=10)

# start the Tkinter event loop
root.mainloop()
