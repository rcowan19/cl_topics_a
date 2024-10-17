#import statements
import customtkinter as ctk
from tkinter import filedialog, messagebox
from collections import defaultdict
import csv

# define the Student class
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

# define the Workjob class
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
            self.min_period = self.min  
            self.max_period = self.max  
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

# define the period mapping
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

# read student information from CSV and keep all relevant free periods information
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

# read workjob information from CSV and keep all relevant information about it
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

# assigns students to workjobs based on their free periods and job requirements
def assign_students_to_workjobs(students, workjobs):
    # initialize variables
    unassigned_students = []
    assignments = []

    # sort workjobs and students by free periods and priority
    sorted_students = sorted(students, key=lambda x: int(x.free_number))
    workjobs.sort(key=lambda job: job.priority)

    # attempt to fill all the workjobs up to their minimum totals
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
    
    # fill remaining periods to meet the minimum number of students
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
    
    # after minimums are full, start filling up to the max
    remaining_unassigned_students = unassigned_students.copy()
    unassigned_students.clear() 
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

#class used for application GUI
class WorkjobDisplay(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Workjob Assignment System")
        self.geometry("1000x700")

        # initialize variables
        self.students = []
        self.workjobs = []
        
        # create main layout
        self.create_gui()

    #function to create the main gui
    def create_gui(self):
        # create main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create top frame 
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.top_frame.grid_columnconfigure((0,1,2), weight=1)

        #create upload students button
        self.student_button = ctk.CTkButton(
            self.top_frame, 
            text="Upload Students CSV",
            command=self.upload_students
        )
        self.student_button.grid(row=0, column=0, padx=10, pady=10)

        #create upload workjob button
        self.workjob_button = ctk.CTkButton(
            self.top_frame, 
            text="Upload Workjobs CSV",
            command=self.upload_workjobs
        )
        self.workjob_button.grid(row=0, column=1, padx=10, pady=10)

        # create export button
        self.assign_button = ctk.CTkButton(
            self.top_frame,
            text="Assign & Display Results",
            command=self.assign_and_display,
            state="disabled"
        )
        self.assign_button.grid(row=0, column=2, padx=10, pady=10)

        # create and add tabview for results
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.tabview.add("Assignments")
        self.tabview.add("Unassigned Students")
     
        # call functions that assign tabs to frames
        self.setup_assignments_tab()
        self.setup_unassigned_tab()

    # function to create frame and assign tab for assignments
    def setup_assignments_tab(self):
        self.assignments_frame = ctk.CTkScrollableFrame(self.tabview.tab("Assignments"))
        self.assignments_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # function to create frame and assign tab for unassigned
    def setup_unassigned_tab(self):
        self.unassigned_frame = ctk.CTkScrollableFrame(self.tabview.tab("Unassigned Students"))
        self.unassigned_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # function to upload the student CSV and change button color
    def upload_students(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.students = read_student_file(file_path)
            self.student_button.configure(fg_color="green")
            self.check_enable_assign()

    # function to upload the workjob CSV and change button color
    def upload_workjobs(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.workjobs = read_workjob_file(file_path)
            self.workjob_button.configure(fg_color="green")
            self.check_enable_assign()

    #function to check if both files are uploaded and activate the assign button
    def check_enable_assign(self):
        if self.students and self.workjobs:
            self.assign_button.configure(state="normal")

    #function to clear the results frames
    def clear_results(self):
        for widget in self.assignments_frame.winfo_children():
            widget.destroy()
        for widget in self.unassigned_frame.winfo_children():
            widget.destroy()
            widget.destroy()

    #function to call mix/max checker, add an export button, and display the results in the correct tab
    def assign_and_display(self):
        self.clear_results()
        
        #check min/max requirements by calculating workjob and students and comparing
        min_total = sum(workjob.min_total for workjob in self.workjobs)
        max_total = sum(workjob.max_total for workjob in self.workjobs)
        if len(self.students) < min_total:
            messagebox.showerror(
                "Error",
                f"Not enough students: {len(self.students)}. Minimum required is {min_total}."
            )
            return
        elif len(self.students) > max_total:
            messagebox.showerror(
                "Error",
                f"Too many students: {len(self.students)}. Maximum allowed is {max_total}."
            )
            return

        # call assign fucntion and place relavant information into their tabs
        assignments, unassigned_students = assign_students_to_workjobs(self.students, self.workjobs)
        self.display_assignments(assignments)
        self.display_unassigned(unassigned_students)
    
        #add export button after results are displayed
        export_button = ctk.CTkButton(
            self.top_frame,
            text="Export Results to CSV",
            command=lambda: self.export_results(assignments, unassigned_students)
        )
        export_button.grid(row=1, column=1, padx=10, pady=10)

    #function to display the assigned students 
    def display_assignments(self, assignments):
        #groups assignment by workjob and period
        grouped = defaultdict(lambda: defaultdict(list))
        for job, period, student in assignments:
            grouped[job][period].append(student)

        #sorts the workjobs into priority
        sorted_workjobs = sorted(self.workjobs, key=lambda x: x.priority)

        #display assignments in priority order; creates frames for each workjob and smaller frames for each period, and adds the students names
        for workjob in sorted_workjobs:
            if workjob.name in grouped:
                job_frame = ctk.CTkFrame(self.assignments_frame, fg_color="#f0f8ff")
                job_frame.pack(fill="x", padx=5, pady=5)
                header_text = f"Priority {workjob.priority} - {workjob.name}"
                header = ctk.CTkLabel(
                    job_frame,
                    text=header_text,
                    font=("Helvetica", 16, "bold"),
                    text_color="#1e90ff"
                )
                header.pack(anchor="w", padx=10, pady=5)
                for period, students in grouped[workjob.name].items():
                    period_frame = ctk.CTkFrame(job_frame, fg_color="white")
                    period_frame.pack(fill="x", padx=20, pady=2)
                    
                    period_text = f"Period {period}: {', '.join(sorted(students))}"
                    period_label = ctk.CTkLabel(
                        period_frame,
                        text=period_text,
                        wraplength=900,
                        text_color="black"
                    )
                    period_label.pack(anchor="w", padx=10, pady=2)
                    
    #fucntion to display the unassigned students
    def display_unassigned(self, unassigned_students):
        #displays the students name if unassigned
        if unassigned_students:
            ctk.CTkLabel(
                self.unassigned_frame,
                text="Unassigned Students:",
                font=("Helvetica", 16, "bold")
            ).pack(anchor="w", padx=10, pady=5)
            for student in unassigned_students:
                ctk.CTkLabel(
                    self.unassigned_frame,
                    text=f"• {student}"
                ).pack(anchor="w", padx=20, pady=2)
        #displays a message if all students are assigned
        else:
            ctk.CTkLabel(
                self.unassigned_frame,
                text="All students have been assigned!",
                font=("Helvetica", 16)
            ).pack(padx=10, pady=20)

    #function to export the results to a CSV
    def export_results(self, assignments, unassigned_students):
        #exports workjob, period, name of assigned students to a CSV
        assignments_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv")],
            title="Save Assignments CSV"
        )
        if assignments_path:
            with open(assignments_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Workjob", "Period", "Student"])
                for assignment in assignments:
                    writer.writerow(assignment)

        #exports name of unassigned students to CSV
        if unassigned_students:
            unassigned_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv")],
                title="Save Unassigned Students CSV"
            )
            if unassigned_path:
                with open(unassigned_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Unassigned Students"])
                    for student in unassigned_students:
                        writer.writerow([student])

#call the main loop on the gui class
WorkjobDisplay().mainloop()
    
