import csv
import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import random

# Initialize dates list
dates = []
students = []
unassigned = []

#define date class
class Date:
    # init to allow the date to have all needed information
    def __init__(self, month, day, blocklist, weekday, term):
        self.month = month
        self.day = day
        self.blocklist = blocklist
        self.weekday = weekday
        term_conversion = {"FALL TERM": "Fall", "WINTER TERM": "Winter", "SPRING TERM": "Spring"}
        self.term = term_conversion[term]
        self.month_day = f"{self.month}-{self.day}"

    #function to convert the date to a dictonary for persistence
    def to_dict(self):
        return {
            'month': self.month,
            'day': self.day,
            'blocklist': self.blocklist,
            'weekday': self.weekday,
            'term': self.term,
            'cycle': self.cycle,
            'month_day': self.month_day
        }

    #fucntion to create a date object from info read into a dict using a decorator to allow me to call the fucntion before an instance of the class is created
    @classmethod
    def from_dict(cls, data):
        reverse_term_conversion = {"Fall": "FALL TERM", "Winter": "WINTER TERM", "Spring": "SPRING TERM"}
        date = cls(
            data['month'],
            data['day'],
            data['blocklist'],
            data['weekday'],
            reverse_term_conversion[data['term']]
        )
        date.cycle = data['cycle']
        return date
    
    #function to find what cyclke the date is in: purely numeric
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

#define student class
class Student:
    # init to allow the student to have all needed information
    def __init__(self, name, frees, free_number):
        self.name = name
        self.frees = frees
        self.free_number = free_number
        self.assignment_number = 0
        self.assignment = None
        self.confirmed = False

    #function to convert the date to a dictonary for persistence
    def to_dict(self):
        return {
            'name': self.name,
            'frees': self.frees,
            'free_number': self.free_number,
            'assignment_number': self.assignment_number,
            'assignment': self.assignment,
            'confirmed': self.confirmed
        }

    #fucntion to create a student object from info read into a dict using a decorator to allow me to call the fucntion before an instance of the class is created
    @classmethod
    def from_dict(cls, data):
        student = cls(
            data['name'],
            data['frees'],
            data['free_number']
        )
        student.assignment_number = data['assignment_number']
        student.assignment = data['assignment']
        student.confirmed = data['confirmed']
        return student

    #fucntion to confirm a student: place them in confirmed side and remove from all other periods
    def confirm_student(self, assignments, day=None, period=None):
        self.confirmed = True
        
        if day and period:
            self.assignment = f"{day}-{period}"
            assignments[day][period]["unconfirmed"].remove(self)
            assignments[day][period]["confirmed"].append(self)
        
        for d, periods in assignments.items():
            for p, data in periods.items():
                if self in data["unconfirmed"]:
                    self.assignment_number -= 1
                    data["unconfirmed"].remove(self)

#define DataManager class
class DataManager:
    #function to save all the students and dates by calling there to_dict functions, using a decorator to allow me to use the fucntion without creating an instance of a class
    @staticmethod
    def save_data():
        students_data = [student.to_dict() for student in students]
        with open('students_data.json', 'w') as f:
            json.dump(students_data, f)

        dates_data = [date.to_dict() for date in dates]
        with open('dates_data.json', 'w') as f:
            json.dump(dates_data, f)

    #function to upload all the students and dates by calling there from_dict functions, and verify if they exsist, and using a decorator to allow me to use the fucntion without creating an instance of a class
    @staticmethod
    def load_data():
        global students, dates
        success = True
        try:
            with open('students_data.json', 'r') as f:
                students_data = json.load(f)
                students = [Student.from_dict(data) for data in students_data]
            with open('dates_data.json', 'r') as f:
                dates_data = json.load(f)
                dates = [Date.from_dict(data) for data in dates_data]
            if not students or not dates:
                success = False
            return success
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

#define Algorithm class
class Algorithm:
    # init to allow the algorithm to have all needed information
    def __init__(self,students,dates, start_date, end_date):
        self.students = students
        self.dates = dates
        self.assignments = {}
        self.usable_days =  ["Monday", "Wednesday", "Friday"]
        self.start_date = start_date
        self.end_date = end_date
    
    #fucntion that creates the assignments dict based on if the date fall within a cycles dates and on a usable day
    def populate_dict(self, date):
        start_month = self.start_date.split("-")[0]
        start_day = int(self.start_date.split("-")[1])
        end_month = self.end_date.split("-")[0]
        end_day = int(self.end_date.split("-")[1])
        if date.weekday in self.usable_days:
            if start_month == end_month:
                if date.month == start_month:
                    if int(date.day) >= start_day and int(date.day) <= end_day:
                        self.assignments[date.month_day] = {}
            elif start_month != end_month:
                if date.month == start_month:
                    if int(date.day) >= start_day:
                        self.assignments[date.month_day] = {}
                elif date.month == end_month:
                    if int(date.day) <= end_day:
                        self.assignments[date.month_day] = {}
            
        if date.month_day in self.assignments.keys():
            for block in date.blocklist:
                self.assignments[date.month_day][block] = {"confirmed": [], "unconfirmed": []}
    
    #function to assign all students to every free period they can be assigned too
    def assign_all_students(self, date):
        for student in students:
            for free_period in student.frees:
                if free_period in date.blocklist:
                    if date.month_day in self.assignments.keys():
                        self.assignments[date.month_day][free_period]["unconfirmed"].append(student)
                        student.assignment_number += 1

    #fucntion to check the total # of students in a period after a update adn remove the period if it doesnt have enough to possibly satisfy the minimum condition
    def check_min(self):
        for day, periods in list(self.assignments.items()):
                    for period in list(periods.keys()):
                        if len(self.assignments[day][period]["unconfirmed"]) + len(self.assignments[day][period]["confirmed"]) <2:
                            del self.assignments[day][period]

    #fucntion to confirm all the students that only have one available free period
    def assign_people_with_one(self):
        for student in students:
            if student.assignment_number == 1:
                for day, periods in self.assignments.items():
                    for period, data in periods.items():
                        if student in data["unconfirmed"]:
                            student.confirm_student(self.assignments, day, period)
                            break
    
    #fucntion to loop through all period and find the one with the least students confirmed, but atleast one, and then move the students with least number of assignment into that confirmed section
    def take_student(self):
        least = None  
        least_num = None  
        for day, periods in self.assignments.items():
            for period, data in periods.items():
                confirmed_count = len(data["confirmed"])
                unconfirmed_count = len(data["unconfirmed"])
                if confirmed_count > 0 and confirmed_count < 4 and unconfirmed_count > 0:
                    if least is None or confirmed_count < least_num:
                        least = (day, period)  
                        least_num = confirmed_count
                    elif confirmed_count == least_num:  
                        if random.choice([True, False]):
                            least = (day, period)
                            
        if least:
            day, period = least
            least_student = None
            least_num = None
            for student in self.assignments[day][period]["unconfirmed"]:
                assign_count = student.assignment_number
                if least_student is None or assign_count < least_num:
                    least_student = student
                    least_num = assign_count
                elif assign_count == least_num: 
                    if random.choice([True, False]):
                        least_student = student
            if least_student:
                least_student.confirm_student(self.assignments, day, period)
        else:
            self.take_student_end()

    #fucntion to loop through all period and find the one with the least students confirmed, after all with some have been filled and then move the students with least number of assignment into that confirmed section
    def take_student_end(self):
            least = None  
            least_num = None  
            for day, periods in self.assignments.items():
                for period, data in periods.items():
                    confirmed_count = len(data["confirmed"])
                    unconfirmed_count = len(data["unconfirmed"])
                    if confirmed_count < 4 and unconfirmed_count > 0:
                        if least is None or confirmed_count < least_num:
                            least = (day, period)  
                            least_num = confirmed_count
                        elif confirmed_count == least_num:  
                            if random.choice([True, False]):
                                least = (day, period)                 
            if least:
                day, period = least
                least_student = None
                least_num = None
                for student in self.assignments[day][period]["unconfirmed"]:
                    assign_count = student.assignment_number
                    if least_student is None or assign_count < least_num:
                        least_student = student
                        least_num = assign_count
                    elif assign_count == least_num: 
                        if random.choice([True, False]):
                            least_student = student
                if least_student:
                    least_student.confirm_student(self.assignments, day, period)
            
    #function to loop through the function needed for the algorithm and stop when no one more can be assigned
    def run_algorithm(self):
        for date in self.dates:
            self.populate_dict(date)
            self.assign_all_students(date)
        self.check_min()
        self.assign_people_with_one()
       

        previous_unconfirmed_count = -1
        while True:
            unconfirmed_students = []
            for student in self.students:
                if not student.confirmed:
                    unconfirmed_students.append(student)

            if len(unconfirmed_students) == previous_unconfirmed_count:
                break

            previous_unconfirmed_count = len(unconfirmed_students)
            self.take_student()
            self.check_min()

#define CycleDropdown Widget
class CycleSelectorWindow(QWidget):
    #init to set up how the widget should look and its behaviors when it is interacted with
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cycle Selector")
        layout = QGridLayout()
        
        self.cycle_dropdown = QComboBox()
        self.cycle_dropdown.currentIndexChanged.connect(self.on_cycle_selected)
        self.cycle_dropdown.setStyleSheet("""
            QComboBox {
                font-size: 25px;
                color: black;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                font-size: 25px;
            }
        """)
        layout.addWidget(self.cycle_dropdown, 0,0)
        
        self.cycle_info_label = QLabel("")
        layout.addWidget(self.cycle_info_label)
        
        self.submit_button = QPushButton("Submit")

        layout.addWidget(self.submit_button, 0,1)
        
        self.populate_cycles()
    
    #fucntion to populate the dropdown with all the correct cycles
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

    #fucntion to give the cycle label text based on the selected cycle
    def on_cycle_selected(self, index):
        term, cycle_number = self.cycle_dropdown.itemData(index)
        selected_cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]
        
        if selected_cycle_dates:
            start_date = f"{selected_cycle_dates[0].month}-{selected_cycle_dates[0].day}"
            end_date = f"{selected_cycle_dates[-1].month}-{selected_cycle_dates[-1].day}"
            self.start_date = start_date  
            self.end_date = end_date     
            self.cycle_info_label.setText(f"Cycle {cycle_number} {term}: {start_date}-{end_date}")
            self.cycle_info_label.setStyleSheet("""
                    QTextEdit {
                        background-color: white;
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 12px;
                        color: black;
                        font-weight: bold;
                        
                    }
                """)

        else:
            self.cycle_info_label.setText("")

#define a Upload Button Widget 
class UploadButton(QWidget):
    # Signal to notify successful upload
    upload_successful = Signal()  
    
    # Initialize the upload button widget
    def __init__(self, purpose):
        super().__init__()
        layout = QVBoxLayout(self)
        self.success = False  
        self.purpose = purpose  
        
        # Create upload button and label for feedback
        self.upload_button = QPushButton(f"Upload {purpose}")
        if "Student" in purpose:
            self.upload_button.clicked.connect(self.read_student_file)
        elif "Class" in purpose:
            self.upload_button.clicked.connect(self.read_classes_file)
        self.display = QLabel(f"{purpose} Data Not Loaded")
        
        layout.addWidget(self.upload_button)
        layout.addWidget(self.display)
    
    # Update the UI to reflect the success state of the upload
    def set_success_state(self, success=True):
        self.success = success
        if success:
            self.upload_button.setStyleSheet("background-color: green; color: white;")
            self.display.setText(f"{self.purpose} Successfully Uploaded")
        else:
            self.upload_button.setStyleSheet("")
            self.display.setText(f"{self.purpose} Data Not Loaded")
    
    # Function to read student data from a file and save to persist
    def read_student_file(self):
        dialog = QFileDialog()
        file_path, _ = dialog.getOpenFileName(parent=None, caption="Select a file", dir=".", filter="All Files (*)")
        if not file_path: 
            return
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
            
            self.set_success_state(bool(students)) 
            self.upload_successful.emit()  
            DataManager.save_data()  
        except Exception as e:
            self.set_success_state(False)
            self.display.setText(f"Error: {e}")
    
    # Function to read class data from a file and save to persist
    def read_classes_file(self):
        dialog = QFileDialog()
        file_path, _ = dialog.getOpenFileName(parent=None, caption="Select a file", dir=".", filter="All Files (*)")
        if not file_path:  
            return
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
                    date.find_cycle()  
                
                self.set_success_state(bool(dates)) 
                self.upload_successful.emit() 
                DataManager.save_data()  
        except Exception as e:
            self.set_success_state(False)
            self.display.setText(f"Error: {e}")

    # function to create block list based on day label
    def create_blocklist(self, day):
        block_list = []
        if len(day) > 1 and day[1:].isdigit():
            day_num = int(day[1:])
            for i in range(4):
                block_num = ((day_num + i - 1) % 7) + 1
                block_list.append(f"{day}B{block_num}")
        return block_list

#define a Upload Window
class UploadWindow(QMainWindow):
    #fuicntion to initialize the main upload window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISA Workjob Assigner")
        
        # Create central widget and grid layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)
        
        # Add upload buttons for students and classes
        self.upload_students = UploadButton("Student Frees")
        self.upload_classes = UploadButton("Class Info")
        grid.addWidget(self.upload_students, 1, 0)
        grid.addWidget(self.upload_classes, 2, 0)
        
        # Create the continue button and disable initially
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.run_cycle)
        self.continue_button.setEnabled(bool(students and dates))
        grid.addWidget(self.continue_button, 3, 0)

        # Try to load saved data
        if DataManager.load_data():
            self.success_label = QLabel("Loaded saved data successfully!")
            self.success_label.setStyleSheet("color: green; font-weight: bold;")
            grid.addWidget(self.success_label, 0, 0)

            # Update upload buttons to reflect loaded data
            self.upload_students.set_success_state(True)
            self.upload_classes.set_success_state(True)
            self.check_uploads()  

        # Connect upload success signals to the method for enabling continue button
        self.upload_students.upload_successful.connect(self.check_uploads)
        self.upload_classes.upload_successful.connect(self.check_uploads)

        # Add a clear data button for resetting the application state
        self.clear_button = QPushButton("Clear Saved Data")
        self.clear_button.clicked.connect(self.clear_saved_data)
        grid.addWidget(self.clear_button, 4, 0)

    #function to enable the continue button if both uploads are successful
    def check_uploads(self):
        if self.upload_students.success and self.upload_classes.success:
            self.continue_button.setEnabled(True)
        else:
            self.continue_button.setEnabled(False)

    #function to  Open the main UI window when continuing
    def run_cycle(self):
        self.cycle_window = MainUI()
        self.cycle_window.show()
        self.close()
    
    #function to Clear saved data and reset the application state
    def clear_saved_data(self):
        
        try:
            import os
            if os.path.exists('students_data.json'):
                os.remove('students_data.json')
            if os.path.exists('dates_data.json'):
                os.remove('dates_data.json')
            
            global students, dates
            students = []
            dates = []
            
            self.upload_students.set_success_state(False)
            self.upload_classes.set_success_state(False)
            self.continue_button.setEnabled(False)
            
            if hasattr(self, 'success_label'):
                self.success_label.setText("")
            
            QMessageBox.information(self, "Success", "Saved data cleared successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to clear data: {str(e)}")

#define MainUi Window
class MainUI(QMainWindow):
    # Initialize the main UI window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISA Workjob Assigner")

        # Set up central widget and layout
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background-color: grey;")
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)

        # Create and style the top frame for cycle selection
        self.other_frame = QFrame()
        self.other_frame.setStyleSheet("background-color: lightgrey; border-radius: 10px;")
        self.other_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.other_frame.setMaximumHeight(100)

        other_layout = QHBoxLayout(self.other_frame)
        other_layout.setContentsMargins(10, 10, 10, 10)
        other_layout.setSpacing(20)

        # Set up the left layout with dropdown and submit button
        left_layout = QVBoxLayout()
        self.cycle_selector = CycleSelectorWindow()
        cycle_dropdown = self.cycle_selector.cycle_dropdown
        submit_button = self.cycle_selector.submit_button
        submit_button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    font-size: 20px;
                    color: black;
                }
                QPushButton:hover {
                    background-color: gray;
                }
            """)

        left_layout.addWidget(cycle_dropdown)
        left_layout.addWidget(submit_button)

        # Wrap the left layout in a widget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        other_layout.addWidget(left_widget)

        # Add cycle date display to the frame
        self.cycle_dates_label = QLabel("Sep-10 to Sep-18")
        self.cycle_dates_label.setAlignment(Qt.AlignCenter)
        self.cycle_dates_label.setStyleSheet("font-size: 50px; font-weight: bold; color: black;")
        self.cycle_dates_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        other_layout.addWidget(self.cycle_dates_label)
        other_layout.addWidget(left_widget)
        other_layout.setStretch(1, 1) 
        other_layout.setStretch(0, 1)

        grid.addWidget(self.other_frame, 0, 0, 1, 1)

        # Set up the main grid for displaying assignments
        self.assigned_frame = QFrame()
        self.assigned_frame.setStyleSheet("background-color: lightgrey; border-radius:10px;")
        self.assigned_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.assigned_frame, 1, 0, 4, 1)

        self.grid_assigned = QGridLayout(self.assigned_frame)

        # Create grid cells for assignment display
        self.block_labels = []
        for row in range(4):
            row_labels = []
            for col in range(7):
                text_edit = QTextEdit()
                text_edit.setStyleSheet("""
                    QTextEdit {
                        background-color: white;
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 12px;
                        color: black;
                        font-weight: bold;
                        border-radius:10px;
                    }
                """)
                text_edit.setReadOnly(True)
                text_edit.setMinimumSize(150, 100)

                self.grid_assigned.addWidget(text_edit, row + 1, col + 1)
                row_labels.append(text_edit)
            self.block_labels.append(row_labels)

        self.update_headers()

        # Create and style unassigned students display frame
        self.unassigned_frame = QFrame()
        self.unassigned_frame.setStyleSheet("background-color: lightgrey; border-radius:10px;")
        self.unassigned_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.unassigned_frame.setMaximumHeight(150)

        self.unassigned_text = QTextEdit()
        self.unassigned_text.setStyleSheet("""
            QTextEdit {
                color: black;
                font-size: 20px;
                background-color: lightgrey;
                border-radius: 10px;
            }
        """)
        self.unassigned_text.setReadOnly(True)
        unassigned_layout = QVBoxLayout(self.unassigned_frame)
        unassigned_label = QLabel("Unassigned Students:")
        unassigned_label.setStyleSheet("color: black; font-weight: bold; font-size:25px; ")
        unassigned_layout.addWidget(unassigned_label)
        unassigned_layout.addWidget(self.unassigned_text)

        grid.addWidget(self.unassigned_frame, 5, 0, 1, 1)

        # Connect cycle selector submit button to functionality
        self.cycle_selector.submit_button.clicked.connect(self.on_submit)
        self.cycle_selector.cycle_dropdown.currentIndexChanged.connect(self.update_cycle_dates_label)

    # Function to update grid headers based on cycle dates
    def update_headers(self):
        for col in range(7):
            item = self.grid_assigned.itemAtPosition(0, col + 1)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        current_index = self.cycle_selector.cycle_dropdown.currentIndex()
        if current_index >= 0:
            term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(current_index)
            cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]

            for i, date in enumerate(cycle_dates):
                if i < 7:
                    header_widget = QWidget()
                    header_layout = QVBoxLayout(header_widget)
                    header_layout.setSpacing(0)
                    header_layout.setContentsMargins(0, 0, 0, 0)

                    day_label = QLabel(f"Day {date.blocklist[0][1]}")
                    day_label.setAlignment(Qt.AlignCenter)
                    day_label.setStyleSheet("font-weight: bold; color: black;")

                    date_label = QLabel(f"{date.month}-{date.day}\n{date.weekday}")
                    date_label.setAlignment(Qt.AlignCenter)
                    date_label.setStyleSheet("color: black;")

                    header_layout.addWidget(day_label)
                    header_layout.addWidget(date_label)
                    self.grid_assigned.addWidget(header_widget, 0, i + 1)

                    for row in range(4):
                        if row < len(date.blocklist):
                            block_number = date.blocklist[row].split('B')[1]
                            self.block_labels[row][i].setPlainText(f"Block {block_number}")
                        else:
                            self.block_labels[row][i].setPlainText("")

    # Function to update cycle date labels when selection changes
    def update_cycle_dates_label(self, index):
        term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(index)
        selected_cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]

        if selected_cycle_dates:
            start_date = f"{selected_cycle_dates[0].month}-{selected_cycle_dates[0].day}"
            end_date = f"{selected_cycle_dates[-1].month}-{selected_cycle_dates[-1].day}"
            self.cycle_dates_label.setText(f"{start_date} to {end_date}")
        else:
            self.cycle_dates_label.setText("No cycle selected")

    # Function to reset data and run assignment algorithm on submit
    def on_submit(self):
        self.update_headers()
        for student in students:
            student.confirmed = False
            student.assignment = None
            student.assignment_number = 0
        algorithm = Algorithm(students, dates,
                               self.cycle_selector.start_date,
                               self.cycle_selector.end_date)
        algorithm.run_algorithm()
        self.display_assignments(algorithm)
        self.display_unassigned_students([s for s in students if not s.confirmed])

    # Function to display assignments in the grid
    def display_assignments(self, algorithm):
        for row in self.block_labels:
            for block in row:
                
                block.setPlainText(block.toPlainText().split('\n')[0])
                block.setStyleSheet("""
                    QTextEdit {
                        background-color: white;
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 25px;
                        color: black;
                        font-weight: bold;
                    }
                """)

        
        current_index = self.cycle_selector.cycle_dropdown.currentIndex()
        if current_index >= 0:
            term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(current_index)
            cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]

            
            for col, date in enumerate(cycle_dates):
                if col >= 7: 
                    break
                day = f"{date.month}-{date.day}"
                if day in algorithm.assignments:
                    for row, block in enumerate(date.blocklist):
                        if block in algorithm.assignments[day]:
                            
                            confirmed_students = algorithm.assignments[day][block]["confirmed"]
                            student_names = [s.name for s in confirmed_students]

                            
                            current_text = self.block_labels[row][col].toPlainText()
                            block_header = current_text.split('\n')[0]
                            students_text = "<br>".join(student_names)
                            formatted_text = f"<strong>{block_header}:</strong><br>{students_text}"
                            self.block_labels[row][col].setHtml(formatted_text) 

                            self.block_labels[row][col].setStyleSheet("""
                                QTextEdit {
                                    background-color: white;
                                    border: 1px solid black;
                                    padding: 5px;
                                    font-size: 17px;
                                    color: black;
                                    border-radius: 10px;
                                }
                            """)
                        else:
                            
                            current_text = self.block_labels[row][col].toPlainText()
                            block_header = current_text.split('\n')[0]
                            empty_text = "Empty"
                            formatted_text = f"<strong>{block_header}:</strong><br>{empty_text}"
                            self.block_labels[row][col].setHtml(formatted_text)

                            self.block_labels[row][col].setStyleSheet("""
                                QTextEdit {
                                    background-color: white;
                                    border: 1px solid black;
                                    padding: 5px;
                                    font-size: 17px;
                                    color: black;
                                    border-radius: 10px;
                                }
                            """)
                else:
                    for row, block in enumerate(date.blocklist):
                        current_text = self.block_labels[row][col].toPlainText()
                        block_header = current_text.split('\n')[0]
                        empty_text = "Empty"
                        formatted_text = f"<strong>{block_header}:</strong><br>{empty_text}"
                        self.block_labels[row][col].setHtml(formatted_text)

                        self.block_labels[row][col].setStyleSheet("""
                            QTextEdit {
                                background-color: darkgrey;
                                border: 1px solid black;
                                padding: 5px;
                                font-size: 17px;
                                color: black;
                                border-radius: 10px;
                            }
                        """)

    # Function to display unassigned students
    def display_unassigned_students(self, unassigned_students):
        if unassigned_students:
            unassigned_names = [student.name for student in unassigned_students]
            self.unassigned_text.setPlainText("\n".join(unassigned_names))
        else:
            self.unassigned_text.setPlainText("No unassigned students")

# Application setup
app = QApplication(sys.argv)
main_window = UploadWindow()
main_window.show()
app.exec()