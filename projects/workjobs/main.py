#import statements
import customtkinter as ctk
from tkinter import filedialog, messagebox
from collections import defaultdict
import csv
import os
import json

# define the Student class
class Student:
    # init to allow the student to have all needed information
    def __init__(self, name, frees, grade, free_number, id):
        self.id = id
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
    def __init__(self, name, w_type, min_students, max_students, priority, periods,alt_name):
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
        self.internal_name = alt_name
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
            id = row["Person ID"]
            name = row["Full Name"]
            grade = row["Grade"]
            frees = {}
            for block in row.keys():
                if block not in ["Person ID", "Full Name", "Grade"]:
                    frees[block] = int(row[block]) if row[block] != '' else 0
            free_list = [period for period, value in frees.items() if value == 1]
            free_number = len(free_list)
            students.append(Student(name, free_list, grade, free_number, id))
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
            internal_name = row["alt_name"]
            workjobs.append(Workjob(name, w_type, min_students, max_students, priority, periods, internal_name))
    return workjobs

# assigns students to workjobs based on their free periods and job requirements
def assign_students_to_workjobs(students, workjobs):
    #initialize variables
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
                    assignments.append([workjob.name, period, student.id,student.name])
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
                        assignments.append([workjob.name, period,student.id,student.name])
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
    #init fucntion to intialzie all variables and the ctk window
    def __init__(self):
        super().__init__()
        self.title("Workjob Assignment System")
        self.geometry("1000x700")
        self.students = []
        self.workjobs = []
        self.current_assignments = []  
        self.year = None
        self.export_file_path = None
        self.selected_workjob_button = None
        self.config_file = "workjob_config.json"
        self.saved_paths = {}
        
        #call to create main layout and load saved files if the exist
        self.load_config()
        self.create_gui()
        self.load_saved_files()

    #fucntion to create main ui layout
    def create_gui(self):
        # create main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create top frame 
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.top_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # create upload students button
        self.student_button = ctk.CTkButton(
            self.top_frame, 
            text="Upload Students CSV",
            command=self.upload_students
        )
        self.student_button.grid(row=0, column=0, padx=10, pady=10)

        # create upload workjob button
        self.workjob_button = ctk.CTkButton(
            self.top_frame, 
            text="Upload Workjobs CSV",
            command=self.upload_workjobs
        )
        self.workjob_button.grid(row=0, column=1, padx=10, pady=10)

        # create assign button
        self.assign_button = ctk.CTkButton(
            self.top_frame,
            text="Assign & Display Results",
            command=self.assign_and_display,
            state="disabled"
        )
        self.assign_button.grid(row=0, column=2, padx=10, pady=10)

         # Create reset button
        self.reset_button = ctk.CTkButton(
            self.top_frame,
            text="Reset All",
            command=self.reset_application,
            fg_color="red"
        )
        self.reset_button.grid(row=0, column=3, padx=10, pady=10)

        # create and add tabview for results
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.tabview.add("Assignments")
        self.tabview.add("Unassigned Students")
     
        #call functions that assign tabs to frames
        self.setup_assignments_tab()
        self.setup_unassigned_tab()
    
    #fucntion to load the saved json with paths into a dictonary
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                    self.saved_paths = json.load(file)
            
    #function to load the dictonary with save paths into a json
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.saved_paths, f)

    #fucntion of open the saved paths from the python dictonary and make the ui respond accordignly
    def load_saved_files(self):
        if 'student_file' in self.saved_paths:
            self.students = read_student_file(self.saved_paths['student_file'])
            self.student_button.configure(fg_color="green")
        if 'workjob_file' in self.saved_paths:
            self.workjobs = read_workjob_file(self.saved_paths['workjob_file'])
            self.workjob_button.configure(fg_color="green")
        self.check_enable_assign()

    #function to rest the application by removing the json and clearing saved paths and reseting the UI
    def reset_application(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset? This will clear all loaded files and assignments."):
            #clear saved paths and remove json
            self.saved_paths = {}
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            
            #reset variables
            self.students = []
            self.workjobs = []
            self.current_assignments = []
            
            #reset UI
            self.student_button.configure(fg_color="#1f6aa5")
            self.workjob_button.configure(fg_color="#1f6aa5")
            self.assign_button.configure(state="disabled")
            self.clear_results()
            self.workjob_dropdown.configure(values=["All Workjobs"])
            self.workjob_dropdown.set("All Workjobs")
            if self.selected_workjob_button:
                self.selected_workjob_button.destroy()
                self.selected_workjob_button = None

    #fucntion that get called when students button is clicked to allow upload of a file and call a fucntion to parse it
    def upload_students(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.students = read_student_file(file_path)
            self.student_button.configure(fg_color="green")
            self.saved_paths['student_file'] = file_path
            self.save_config()
            self.check_enable_assign()

    #fucntion that get called when  workjob button is clicked to allow upload of a file and call a fucntion to parse it
    def upload_workjobs(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.workjobs = read_workjob_file(file_path)
            self.workjob_button.configure(fg_color="green")
            self.saved_paths['workjob_file'] = file_path
            self.save_config()
            self.check_enable_assign()

    #fucntion to intialize the assigned tab
    def setup_assignments_tab(self):
        #create main frame for assignments tab
        assignments_main_frame = ctk.CTkFrame(self.tabview.tab("Assignments"))
        assignments_main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        #create filter frame at the top
        filter_frame = ctk.CTkFrame(assignments_main_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # add label to dropdown
        ctk.CTkLabel(filter_frame, text="Select Workjob:").pack(side="left", padx=5)
        
        #create dropdown for workjob selection 
        self.workjob_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Workjobs"],
            command=self.filter_assignments
        )
        self.workjob_dropdown.pack(side="left", padx=5)
        
        #create scrollable frame for assignments
        self.assignments_frame = ctk.CTkScrollableFrame(assignments_main_frame)
        self.assignments_frame.pack(fill="both", expand=True, padx=5, pady=5)

    #function to intiialize the unassigned tab
    def setup_unassigned_tab(self):
        self.unassigned_frame = ctk.CTkScrollableFrame(self.tabview.tab("Unassigned Students"))
        self.unassigned_frame.pack(fill="both", expand=True, padx=10, pady=10)

    #function to check if student and workjob files are uploaded to allow assignment to happen
    def check_enable_assign(self):
        if self.students and self.workjobs:
            self.assign_button.configure(state="normal")

    #function to clear all previous results in order to run again
    def clear_results(self):
        for widget in self.assignments_frame.winfo_children():
            widget.destroy()
        for widget in self.unassigned_frame.winfo_children():
            widget.destroy()

    #fucntion to call all relevant fucntions needed to get info an display it on the UI
    def assign_and_display(self):
        self.clear_results()

        #check min/max requirements and return errors if needed
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

        #get assignments by calling the assign_students function
        self.current_assignments, unassigned_students = assign_students_to_workjobs(self.students, self.workjobs)

        #update workjob dropdown values based on the assignments
        workjob_names = ["All Workjobs"] + list(set(assignment[0] for assignment in self.current_assignments))
        self.workjob_dropdown.configure(values=workjob_names)
        self.workjob_dropdown.set("All Workjobs")

        #call fucntions to display results in proper tabs
        self.display_assignments(self.current_assignments)
        self.display_unassigned(unassigned_students)

        #add export for database button
        export_button = ctk.CTkButton(
            self.top_frame,
            text="Export Results for Database",
            command=lambda: self.download_results(self.current_assignments)
        )
        export_button.grid(row=1, column=0, padx=10, pady=10)

    #fucntion get the year from the entry box and allow a file path for saving database export 
    def get_year(self):
        self.year = self.entry.get()
        self.entry.delete(0, "end")
        self.submit_button.configure(fg_color="green")
        self.entry.configure(state="disabled")
        #prompt the user to select a file save location
        self.export_file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save results as"
            )
       
    #fucntion to filter the assignment displayed base on choice of dropdown
    def filter_assignments(self, selected_workjob):
        #clear current choice assignments 
        for widget in self.assignments_frame.winfo_children():
            widget.destroy()
            
        #filter assignments based on selection
        if selected_workjob == "All Workjobs":
            filtered_assignments = self.current_assignments
        else:
            filtered_assignments = []
            for assignment in self.current_assignments:
                if assignment[0] == selected_workjob:
                    filtered_assignments.append(assignment)

        #checks is a previous export button exsits
        if self.selected_workjob_button is not None:
            self.selected_workjob_button.destroy()

         # create a button for export with the name of the selected workjob 
        self.selected_workjob_button = ctk.CTkButton(
            self.top_frame,
            text=f"Export {selected_workjob} File",
            command=lambda: self.export_workjobs(filtered_assignments, selected_workjob)
        )
        self.selected_workjob_button.grid(row=1, column=1, padx=10, pady=10)
   
        #call display assignment fucntion with filtered assignments
        self.display_assignments(filtered_assignments)

    #function to display the assigned students in the assigned students tab
    def display_assignments(self, assignments):
        #groups assignment by workjob and period
        grouped = {}
        for job, period, student_id, student_name in assignments:
            if job not in grouped:
                grouped[job] = {}  
            if period not in grouped[job]:
                grouped[job][period] = []  
            grouped[job][period].append(student_name)  

        #sort workjobs by priority for all workjobs display
        sorted_workjobs = [wj for wj in sorted(self.workjobs, key=lambda x: x.priority) 
                          if wj.name in grouped]

        #display assignments frames in priority order
        for workjob in sorted_workjobs:
            job_frame = ctk.CTkFrame(self.assignments_frame, fg_color="#f0f8ff")
            job_frame.pack(fill="x", padx=5, pady=5)
            header_text = f"{workjob.name}"
            header = ctk.CTkLabel(
                job_frame,
                text=header_text,
                font=("Helvetica", 16, "bold"),
                text_color="#1e90ff"
            )
            header.pack(anchor="w", padx=10, pady=5)

             #sort periods by D# and then B#
            sorted_periods = sorted(workjob.periods, key=lambda period: (
                int(period.split('B')[0][1:]),  
                int(period.split('B')[1])      
            ))

            #display the sorted periods
            for period in sorted_periods:
                period_frame = ctk.CTkFrame(job_frame, fg_color="white")
                period_frame.pack(fill="x", padx=20, pady=2)

                #check if the period ahs students assigned 
                if period in grouped[workjob.name]:
                    students = grouped[workjob.name][period]
                    period_text = f"{period}: {', '.join(students)}" 
                else:
                    period_text = f"{period}: Empty"

                period_label = ctk.CTkLabel(
                    period_frame,
                    text=period_text,
                    wraplength=900,
                    text_color="black"
                )
                period_label.pack(anchor="w", padx=10, pady=2)
            
    #fucntion to display the unassigned studenta in the unassigned tab
    def display_unassigned(self, unassigned_students):
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
        else:
            ctk.CTkLabel(
                self.unassigned_frame,
                text="All students have been assigned!",
                font=("Helvetica", 16)
            ).pack(padx=10, pady=20)

   #fucntion that allows user to start download process by prompting a year entry box
    def download_results(self, assignments):
        #create a new top-level window for year entry
        self.year_window = ctk.CTkToplevel(self)
        self.year_window.title("Enter School Year")
        self.year_window.geometry("400x200")
        self.year_window.transient(self) 
        
        #center window on application
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (200 // 2)
        self.year_window.geometry(f"+{x}+{y}")

        #create frame for entry
        content_frame = ctk.CTkFrame(self.year_window)
        content_frame.pack(expand=True, padx=20, pady=20)

        #add label with instructions
        instructions = ctk.CTkLabel(
            content_frame,
            text="Please enter the school year",
            font=("Helvetica", 12)
        )
        instructions.pack(pady=(0, 10))

        #add year entry
        self.year_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="YYYY",
            width=200
        )
        self.year_entry.pack(pady=(0, 20))

        #create button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        #add cancel and submit buttons
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=80,
            fg_color="gray",
            command=self.create_gui
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Submit",
            width=80,
            command=lambda: self.validate_and_submit_year(assignments)
        ).pack(side="right", padx=5)
    
    #function that finishes the download process by prompting the user with file save loaction and saving
    def validate_and_submit_year(self, assignments):
        self.year = self.year_entry.get()
        self.year_window.destroy()
        
        #prompt for save location and continue with existing export logic
        self.export_file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save results as"
        )
        
        if self.export_file_path:
            # intialize a mapping dictonary of workjob names to their internal class IDs from classes.csv
            workjob_mapping = {}

            #open classes.csv to get the info for each class into a list
            with open("cl_topics_a\projects\workjobs\classes.csv", 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                class_data = [row for row in reader]
            
            #loop through the workjobs 
            for workjob in self.workjobs:
                internal_name = workjob.internal_name
                class_info = []

                #loop to find the info of all needed classes, ones that students are assigned to by looping through assignments
                for assignment in assignments: 
                    period = assignment[1]
                    formatted_period = f"{period[:2]}-{period[2:]}"

                    #loop through class data to see if class is in assignments and append it's info to class_info list
                    for row in class_data:
                        if (internal_name in row['Class ID'] and formatted_period in row['Class ID']):
                            class_info_entry = {'internal_class_id': row['Internal Class ID'],'class_id': row['Class ID'],'period': period}
                            # Check if class_info_entry is already in class_info
                            if class_info_entry not in class_info:
                                class_info.append(class_info_entry)
                            break

                # add all workjobs to the mapping and add the class_info to that workjob if its not already there
                if workjob.name not in workjob_mapping:
                    workjob_mapping[workjob.name] = class_info
                else:
                    for entry in class_info:
                        if entry not in workjob_mapping[workjob.name]:
                            workjob_mapping[workjob.name].append(entry)
            

            #write assignments to csv
            with open(self.export_file_path, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                #write headers
                writer.writerow([
                    "internal_class_id",
                    "class_id",
                    "school_year",
                    "veracross_student_id",
                    "grade_level"
                ])

                #get the  assignment data; student and workjob
                for assignment in assignments:
                    workjob_name = assignment[0]
                    period = assignment[1]
                    student_id = assignment[2]
                    
                    #find the class info that corelates to the period that the student is assigned to
                    class_ids = workjob_mapping.get(workjob_name, [])
                    for entry in class_ids:
                        if entry['period'] == period:
                            student_grade = None
                            for student in self.students:
                                if student.id == student_id:
                                    student_grade = student.grade
                                    break
                            
                            #write  the needed data into the csv
                            writer.writerow([
                                entry['internal_class_id'],
                                entry['class_id'],
                                self.year,
                                student_id,  
                                student_grade
                            ])
            messagebox.showinfo("Export Successful", "Assignments have been successfully exported to CSV.")
    
    #function to export a human readable for each period
    def export_workjobs(self, assignments, selected_workjob=None):
        #prompt the user to select a file save location
        export_file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Assignments As"
        )
        if not export_file_path:
            return  

        #open CSV file for writing assignmnet
        with open(export_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            #write the headers
            writer.writerow(["Period", "Student Names"])

        
            #find the workjob object corresponding to the selected workjob
            workjob_obj = next((wj for wj in self.workjobs if wj.name == selected_workjob), None)
            sorted_periods = sorted(workjob_obj.periods, key=lambda period: (
                int(period.split('B')[0][1:]),  
                int(period.split('B')[1])      
            ))


            if workjob_obj:
                #for each period in the workjob, check if there are assigned students
                for period in sorted_periods:
                    students_in_period = [assignment for assignment in assignments if assignment[1] == period]
                    if students_in_period:
                        for assignment in students_in_period:
                            info = [assignment[1],assignment[3]]
                            writer.writerow(info)
                    else:
                        writer.writerow([period, "Empty"])
      
        #show a success message
        messagebox.showinfo("Export Successful", f"{selected_workjob} Assignments have been successfully exported to CSV.")

# Start the application
WorkjobDisplay().mainloop()
