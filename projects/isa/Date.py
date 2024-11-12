import csv
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *

# Initialize dates list
dates = []
students = []
unassigned = []

class Date:
    def __init__(self, month, day, blocklist, weekday, term):
        self.month = month
        self.day = day
        self.blocklist = blocklist
        self.weekday = weekday
        self.term = term
        self.cycle = None

    def __repr__(self):
        return f"Month:{self.month} Day:{self.day} BlockList:{self.blocklist} Weekday:{self.weekday} Term:{self.term} Cycle:{self.cycle}"

    def find_cycle(self):
        cycle = 1
        cycle_days = []
        for day in dates:
            if day.term != self.term:
                continue
            if len(cycle_days) >= 7:
                cycle += 1
                cycle_days = []
            day.cycle = cycle
            cycle_days.append(day)

class Student:
    def __init__(self, name, frees, free_number):
        self.name = name
        self.frees = frees
        self.free_number = free_number
        self.assignment_number = 0
        self.assignment = None
        self.confirmed = False

    def __repr__(self):
        return f"{self.name} (Free Number: {self.free_number}, Free Periods: {self.frees})"
    
    def confirm_student(self, assignments, day=None, period=None):
        self.confirmed = True
        # Confirm the student only for the specified day-period
        if day and period:
            self.assignment = f"{day}-{period}"
            assignments[day][period]["unconfirmed"].remove(self)
            assignments[day][period]["confirmed"].append(self)
        
        # Remove student from all other unconfirmed slots
        for d, periods in assignments.items():
            for p, data in periods.items():
                if self in data["unconfirmed"]:
                    data["unconfirmed"].remove(self)
    
class CycleSelectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cycle Selector")
        layout = QVBoxLayout()
        
        # Cycle dropdown and info display
        self.cycle_dropdown = QComboBox()
        self.cycle_dropdown.currentIndexChanged.connect(self.on_cycle_selected)
        layout.addWidget(QLabel("Select Cycle:"))
        layout.addWidget(self.cycle_dropdown)
        
        self.cycle_info_label = QLabel("")
        layout.addWidget(self.cycle_info_label)
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_cycle)
        layout.addWidget(self.submit_button)
        
        self.populate_cycles()
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def populate_cycles(self):
        cycles = {}
        for date in dates:
            if date.term not in cycles:
                cycles[date.term] = {}
            if date.cycle not in cycles[date.term]:
                cycles[date.term][date.cycle] = []
            cycles[date.term][date.cycle].append(date)
        for term, cycle_term in cycles.items():
            for idx, cycle_dates in enumerate(cycle_term.values(), start=1):
                start_date = f"{cycle_dates[0].month}-{cycle_dates[0].day}"
                end_date = f"{cycle_dates[-1].month}-{cycle_dates[-1].day}"
                cycle_label = f"Cycle {idx} {term}: {start_date} - {end_date}"
                self.cycle_dropdown.addItem(cycle_label, (term, idx))

    def on_cycle_selected(self, index):
        term, cycle_number = self.cycle_dropdown.itemData(index)
        selected_cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]
        
        if selected_cycle_dates:
            start_date = f"{selected_cycle_dates[0].month}-{selected_cycle_dates[0].day}"
            end_date = f"{selected_cycle_dates[-1].month}-{selected_cycle_dates[-1].day}"
            self.start_date = start_date  # Store start date
            self.end_date = end_date      # Store end date
            self.cycle_info_label.setText(f"Cycle {cycle_number} {term}:\nStart Date: {start_date}\nEnd Date: {end_date}")
        else:
            self.cycle_info_label.setText("")

    def submit_cycle(self):
        selected_cycle = self.cycle_dropdown.currentText()
        QMessageBox.information(self, "Cycle Submitted", f"You have selected {selected_cycle}")

        
        # Run the algorithm with the selected dates
        run_algorithm(dates, students, self.start_date, self.end_date)

class UploadButton(QWidget):
    upload_successful = Signal()  
    
    def __init__(self, purpose):
        super().__init__()
        layout = QVBoxLayout(self)
        self.success = False
        self.upload_button = QPushButton(f"Upload {purpose}")
        if "Student" in purpose:
            self.upload_button.clicked.connect(self.read_student_file)
        elif "Class" in purpose:
            self.upload_button.clicked.connect(self.read_classes_file)

        self.display = QLabel(f"{purpose} Data Not Loaded")
        
        layout.addWidget(self.upload_button)
        layout.addWidget(self.display)
    
    def read_student_file(self):
        dialog = QFileDialog()
        file_path, _ = dialog.getOpenFileName(parent=None, caption="Select a file", dir=".", filter="All Files (*)")
        
        try:
            with open(file_path, 'r') as file:
                reader_dict = csv.DictReader(file)
                for row in reader_dict:
                    name = row["Full Name"]
                    frees = {block: int(row[block]) if row[block] else 0 
                             for block in row if block not in ["Total Frees", "Full Name", "Grade"]}
                    free_list = [period for period, value in frees.items() if value == 1]
                    free_number = int(row["Total Frees"])
                    students.append(Student(name, free_list, free_number))
            
            self.success = bool(students)
            self.upload_successful.emit()
            self.display.setText("Students Successfully Uploaded" if students else "No Students Data Found")
            if self.success:
                self.upload_button.setStyleSheet("background-color: green; color: white;")
        except Exception as e:
            self.success = False
            self.display.setText(f"Error: {e}")
    
    def read_classes_file(self):
        dialog = QFileDialog()
        file_path, _ = dialog.getOpenFileName(parent=None, caption="Select a file", dir=".", filter="All Files (*)")
        
        try:
            with open(file_path, 'r', encoding="utf-8-sig") as file:
                reader_dict = csv.DictReader(file)
                term = ""
                global dates
                dates = []
                for row in reader_dict:
                    if row["term"] in ["FALL TERM", "WINTER TERM", "SPRING TERM"]:
                        term = row["term"]
                    calendar_day = row["calendar_day"]
                    block_list = self.create_blocklist(row["d_label"])
                    weekday = row["weekday"]
                    if not calendar_day or not block_list or not weekday:
                        continue
                    day, month = calendar_day.split("-")
                    dates.append(Date(month, day, block_list, weekday, term))

                for date in dates:
                    date.find_cycle()  # Populate cycles after uploading files
                
                self.success = bool(dates)
                self.upload_successful.emit()
                self.display.setText("Class Info Successfully Uploaded" if dates else "No Class Info Data Found")
                if self.success:
                    self.upload_button.setStyleSheet("background-color: green; color: white;")
        except Exception as e:
            self.success = False
            self.display.setText(f"Error: {e}")

    def create_blocklist(self, day):
        block_list = []
        if len(day) > 1 and day[1:].isdigit():
            day_num = int(day[1:])
            for i in range(4):
                block_num = ((day_num + i - 1) % 7) + 1
                block_list.append(f"{day}B{block_num}")
        return block_list

class UploadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISA Workjob Assigner")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)
        
        self.upload_students = UploadButton("Student Frees")
        self.upload_classes = UploadButton("Class Info")
        grid.addWidget(self.upload_students, 0, 0)
        grid.addWidget(self.upload_classes, 1, 0)
        
        self.upload_students.upload_successful.connect(self.check_success)
        self.upload_classes.upload_successful.connect(self.check_success)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.run_cycle)
        self.continue_button.setEnabled(False)
        grid.addWidget(self.continue_button, 2, 0)
        
    def check_success(self):
        if self.upload_students.success and self.upload_classes.success:
            self.continue_button.setEnabled(True)
        else:
            self.continue_button.setEnabled(False)

    def run_cycle(self):
        self.cycle_window = CycleSelectorWindow()
        self.cycle_window.show()
        self.close()  # Close the first window upon continuing


def run_algorithm(dates, students, start_date, end_date):
    assignments = {}
    usable_days = ["Monday", "Wednesday", "Friday"]

    for date in dates:
        if date.weekday in usable_days:
            start_date = start_date
            start_month = start_date.split("-")[0]
            start_day = int(start_date.split("-")[1])
            end_date = end_date
            end_month = end_date.split("-")[0]
            end_day = int(end_date.split("-")[1])
            month_day = f"{date.month}-{date.day}"
           
            if date.month == start_month and int(date.day) >= start_day:
                assignments[month_day] = {}
            if date.month == end_month and int(date.day) <= end_day and int(date.day) >= start_day:
                assignments[month_day] = {}
            else:
                continue
            
            for block in date.blocklist:
                assignments[month_day][block] = {"confirmed": [], "unconfirmed": []}
            
            # Assign students based on their free periods and date's blocklist
            for student in students:
                for free_period in student.frees:
                    if free_period in date.blocklist:
                        assignments[month_day][free_period]["unconfirmed"].append(student)
                        student.assignment_number += 1

            # Remove periods with fewer than 2 unconfirmed students
            for day, periods in list(assignments.items()):
                for period in list(periods.keys()):
                    if len(assignments[day][period]["unconfirmed"]) < 2:
                        del assignments[day][period]

    # Sort students by assignment number
    students.sort(key=lambda student: student.assignment_number)
    for student in students:
        if student.assignment_number == 1:
            for day, periods in assignments.items():
                for period, data in periods.items():
                    if student in data["unconfirmed"]:
                        student.confirm_student(assignments, day, period)
                        break


    

    # Confirm students for periods with exactly 2 unconfirmed students
    for day, periods in assignments.items():
        for period, data in periods.items():
            if len(data["unconfirmed"]) == 2 and len(data["confirmed"]) == 0:
                for student in data["unconfirmed"][:]:
                    student.confirm_student(assignments, day, period)

    for day, periods in assignments.items():
        for period, data in periods.items():
            if len(data["unconfirmed"]) == 1 and len(data["confirmed"]) == 1:
                for student in data["unconfirmed"][:]:
                    student.confirm_student(assignments, day, period)

    for day, periods in assignments.items():
        for period, data in periods.items():
            if len(data["unconfirmed"]) > 0 and len(data["confirmed"]) == 1:
                for student in data["unconfirmed"][:]:
                    student.confirm_student(assignments, day, period)
                    if len(data["confirmed"]) >= 3:
                        break  
    
    # Confirm students for periods with exactly 2 unconfirmed students
    for day, periods in assignments.items():
        for period, data in periods.items():
            if len(data["unconfirmed"]) == 2 and len(data["confirmed"]) == 0:
                for student in data["unconfirmed"][:]:
                    student.confirm_student(assignments, day, period)
    print()
    # Print the assignments for debugging purposes
    for day, periods in assignments.items():
        for period, data in periods.items():
            confirmed_names = [s.name for s in data["confirmed"]]
            unconfirmed_names = [s.name for s in data["unconfirmed"]]
            print(f"Date: {day} Period {period} - Confirmed: {confirmed_names}, Unconfirmed: {unconfirmed_names}")
    
    for day, periods in assignments.items():
        for period, data in periods.items():
            if len(data["confirmed"]) < 2:
                for student in data["confirmed"][:]:
                    unassigned.append(student)

    print(unassigned)
    
    with open("assignments_debug_output.txt", "w") as file:
    # Print the assignments for debugging purposes
        for day, periods in assignments.items():
            for period, data in periods.items():
                confirmed_names = [s.name for s in data["confirmed"]]
                unconfirmed_names = [s.name for s in data["unconfirmed"]]
                file.write(f"Date: {day} Period {period} - Confirmed: {confirmed_names}, Unconfirmed: {unconfirmed_names}\n")
        
        for day, periods in assignments.items():
            for period, data in periods.items():
                if len(data["confirmed"]) < 2:
                    for student in data["confirmed"][:]:
                        unassigned.append(student)

        file.write(f"{unassigned}\n")
    
# Application setup
app = QApplication(sys.argv)
main_window = UploadWindow()
main_window.show()
app.exec()
