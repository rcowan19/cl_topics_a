import csv
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import random

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
        term_conversion = {"FALL TERM": "Fall", "WINTER TERM": "Winter", "SPRING TERM": "Spring"}
        self.term = term_conversion[term]
        self.cycle = None
        self.month_day = f"{self.month}-{self.day}"

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
        
        if day and period:
            self.assignment = f"{day}-{period}"
            assignments[day][period]["unconfirmed"].remove(self)
            assignments[day][period]["confirmed"].append(self)
        
        
        for d, periods in assignments.items():
            for p, data in periods.items():
                if self in data["unconfirmed"]:
                    self.assignment_number -= 1
                    data["unconfirmed"].remove(self)

class Algorithm:
    def __init__(self,students,dates,unassigned, start_date, end_date):
        self.students = students
        self.dates = dates
        self.assignments = {}
        self.usable_days =  ["Monday", "Wednesday", "Friday"]
        self.start_date = start_date
        self.end_date = end_date
        
    def populate_dict(self, date):
        start_month = None
        start_day = None
        end_month = None
        end_day = None
        if date.weekday in self.usable_days:
            start_month = self.start_date.split("-")[0]
            start_day = int(self.start_date.split("-")[1])
            end_month = self.end_date.split("-")[0]
            end_day = int(self.end_date.split("-")[1])
            
        if date.month == start_month and int(date.day) >= start_day and int(date.day) <= end_day:
            self.assignments[date.month_day] = {}
        if date.month == end_month and int(date.day) <= end_day and int(date.day) >= start_day:
            self.assignments[date.month_day] = {}
        
        if date.month_day in self.assignments.keys():
            for block in date.blocklist:
                self.assignments[date.month_day][block] = {"confirmed": [], "unconfirmed": []}
    
    def assign_all_students(self, date):
        for student in students:
            for free_period in student.frees:
                if free_period in date.blocklist:
                    if date.month_day in self.assignments.keys():
                        self.assignments[date.month_day][free_period]["unconfirmed"].append(student)
                        student.assignment_number += 1

    def check_min(self):
        for day, periods in list(self.assignments.items()):
                    for period in list(periods.keys()):
                        if len(self.assignments[day][period]["unconfirmed"]) + len(self.assignments[day][period]["confirmed"]) <2:
                            del self.assignments[day][period]

    def assign_people_with_one(self):
        for student in students:
            if student.assignment_number == 1:
                for day, periods in self.assignments.items():
                    for period, data in periods.items():
                        if student in data["unconfirmed"]:
                            student.confirm_student(self.assignments, day, period)
                            break
    
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
            
    def run_algorithm(self):
        for date in self.dates:
            self.populate_dict(date)
            self.assign_all_students(date)

        self.assign_people_with_one()
        self.check_min()

        previous_unconfirmed_count = -1
        while True:
            unconfirmed_students = []
            for student in self.students:
                if not student.confirmed:
                    unconfirmed_students.append(student)

            if len(unconfirmed_students) == previous_unconfirmed_count:
                print(f"No further assignments can be made. {len(self.students) - len(unconfirmed_students)} students confirmed. {len(unconfirmed_students)} students remain unconfirmed.")
                break

            previous_unconfirmed_count = len(unconfirmed_students)
            self.take_student()
            self.check_min()
    
    def __str__(self):
        output = []
        for day, periods in self.assignments.items():
            for period, data in periods.items():
                confirmed_names = [s.name for s in data["confirmed"]]
                unconfirmed_names = [s.name for s in data["unconfirmed"]]
                output.append(f"Date: {day} Period {period} - Confirmed: {confirmed_names}, Unconfirmed: {unconfirmed_names}")
        return "\n".join(output)
    
class CycleSelectorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cycle Selector")
        layout = QGridLayout()
        
        # Cycle dropdown and info display
        self.cycle_dropdown = QComboBox()
        self.cycle_dropdown.currentIndexChanged.connect(self.on_cycle_selected)
        layout.addWidget(self.cycle_dropdown, 0,0)
        
        self.cycle_info_label = QLabel("")
        layout.addWidget(self.cycle_info_label)
        
        self.submit_button = QPushButton("Submit")

        layout.addWidget(self.submit_button, 0,1)
        
        self.populate_cycles()
        
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
            self.start_date = start_date  
            self.end_date = end_date     
            self.cycle_info_label.setText(f"Cycle {cycle_number} {term}: {start_date}-{end_date}")
        else:
            self.cycle_info_label.setText("")
    
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
        self.main = MainUI()
        self.main.show()
        self.close()  # Close the first window upon continuing

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISA Workjob Assigner")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)

        # Frame for other widgets (modified layout)
        self.other_frame = QFrame()
        self.other_frame.setStyleSheet("background-color: lightblue;")
        self.other_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.other_frame.setMaximumHeight(100)
        
        # Change the layout to QHBoxLayout
        other_layout = QHBoxLayout(self.other_frame)
        other_layout.setContentsMargins(10, 10, 10, 10)
        other_layout.setSpacing(20)

        # Left layout: cycle_dropdown and submit_button vertically
        left_layout = QVBoxLayout()
        self.cycle_selector = CycleSelectorWindow()
        cycle_dropdown = self.cycle_selector.cycle_dropdown
        submit_button = self.cycle_selector.submit_button
        left_layout.addWidget(cycle_dropdown)
        left_layout.addWidget(submit_button)
        
        # Wrap left_layout in a QWidget to manage its size within the HBoxLayout
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        other_layout.addWidget(left_widget)

        # Middle label
        self.cycle_dates_label = QLabel("Sep-10 - Sep-18")
        self.cycle_dates_label.setAlignment(Qt.AlignCenter)
        self.cycle_dates_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.cycle_dates_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        other_layout.addWidget(self.cycle_dates_label)

        # Download button
        self.download_button = QPushButton("Download Results")
        self.download_button.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.download_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        other_layout.addWidget(self.download_button)

        # Set equal stretch factors for all three elements
        other_layout.setStretch(0, 1)  # left_widget
        other_layout.setStretch(1, 1)  # cycle_dates_label
        other_layout.setStretch(2, 1)  # download_button

        grid.addWidget(self.other_frame, 0, 0, 1, 1)

        # Assigned frame (large)
        self.assigned_frame = QFrame()
        self.assigned_frame.setStyleSheet("background-color: lightgreen;")
        self.assigned_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.assigned_frame, 1, 0, 4, 1)
        self.grid_assigned = QGridLayout(self.assigned_frame)

        # Initialize the block labels array
        self.block_labels = []
        
        for row in range(4):
            row_labels = []
            for col in range(7):
                # Create a QTextEdit instead of QLabel for multi-line text
                text_edit = QTextEdit()
                text_edit.setStyleSheet("""
                    QTextEdit {
                        background-color: white;
                        border: 1px solid black;
                        padding: 5px;
                        font-size: 12px;
                        color: black;
                        font-weight: bold;
                    }
                """)
                text_edit.setReadOnly(True)  # Make it read-only
                text_edit.setMinimumSize(150, 100)  # Adjust size as needed
                
                self.grid_assigned.addWidget(text_edit, row + 1, col + 1)
                row_labels.append(text_edit)
            self.block_labels.append(row_labels)

        # Update headers initially
        self.update_headers()

        # Unassigned frame
        self.unassigned_frame = QFrame()
        self.unassigned_frame.setStyleSheet("background-color: lightcoral;")
        self.unassigned_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.unassigned_frame.setMaximumHeight(150)
        
        # Add a QTextEdit for unassigned students with black text
        self.unassigned_text = QTextEdit()
        self.unassigned_text.setStyleSheet("""
            QTextEdit {
                color: black;
                font-size: 12px;
            }
        """)
        self.unassigned_text.setReadOnly(True)
        unassigned_layout = QVBoxLayout(self.unassigned_frame)
        unassigned_label = QLabel("Unassigned Students:")
        unassigned_label.setStyleSheet("color: black; font-weight: bold;")
        unassigned_layout.addWidget(unassigned_label)
        unassigned_layout.addWidget(self.unassigned_text)
        
        grid.addWidget(self.unassigned_frame, 5, 0, 1, 1)

        # Connect the cycle selector's submit button
        self.cycle_selector.submit_button.clicked.connect(self.on_submit)
        # Connect cycle selector's dropdown change to update the cycle_dates_label
        self.cycle_selector.cycle_dropdown.currentIndexChanged.connect(self.update_cycle_dates_label)

    def update_headers(self):
        # Clear existing headers first
        for col in range(7):
            item = self.grid_assigned.itemAtPosition(0, col + 1)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Get the selected cycle's dates
        current_index = self.cycle_selector.cycle_dropdown.currentIndex()
        if current_index >= 0:
            term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(current_index)
            cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]
            
            # Add the new headers and update block labels
            for i, date in enumerate(cycle_dates):
                if i < 7:
                    # Update header
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
                    
                    # Update block labels for this column
                    for row in range(4):
                        if row < len(date.blocklist):
                            block_number = date.blocklist[row].split('B')[1]
                            self.block_labels[row][i].setPlainText(f"Block {block_number}")
                        else:
                            self.block_labels[row][i].setPlainText("")

    def update_cycle_dates_label(self, index):
        """Update the large cycle dates label in the middle based on selection."""
        term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(index)
        selected_cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]
        
        if selected_cycle_dates:
            start_date = f"{selected_cycle_dates[0].month}-{selected_cycle_dates[0].day}"
            end_date = f"{selected_cycle_dates[-1].month}-{selected_cycle_dates[-1].day}"
            self.cycle_dates_label.setText(f"{start_date} - {end_date}")
        else:
            self.cycle_dates_label.setText("No cycle selected")

    def on_submit(self):
        self.update_headers()
        # Reset all student confirmations
        for student in students:
            student.confirmed = False
            student.assignment = None
            student.assignment_number = 0
            
       
        algorithm = Algorithm(students, dates, unassigned, 
                               self.cycle_selector.start_date, 
                               self.cycle_selector.end_date)
        algorithm.run_algorithm()
            

        self.display_assignments(algorithm)
        self.display_unassigned_students([s for s in students if not s.confirmed])

    def display_assignments(self, algorithm):
        # Clear all block contents first
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

        # Get the selected cycle's dates
        current_index = self.cycle_selector.cycle_dropdown.currentIndex()
        if current_index >= 0:
            term, cycle_number = self.cycle_selector.cycle_dropdown.itemData(current_index)
            cycle_dates = [date for date in dates if date.cycle == cycle_number and date.term == term]

            # For each day in the cycle
            for col, date in enumerate(cycle_dates):
                if col >= 7:  # Ensure we don't exceed grid width
                    break
                    
                day = f"{date.month}-{date.day}"
                if day in algorithm.assignments:
                    # For each block in the day
                    for row, block in enumerate(date.blocklist):
                        if block in algorithm.assignments[day]:
                            # Get confirmed students for this block
                            confirmed_students = algorithm.assignments[day][block]["confirmed"]
                            student_names = [s.name for s in confirmed_students]
                            
                            # Update the block text
                            current_text = self.block_labels[row][col].toPlainText()
                            block_header = current_text.split('\n')[0]  # Keep the block number
                            students_text = "\n".join(student_names)
                            self.block_labels[row][col].setPlainText(f"{block_header}\n{students_text}")
                        
                            self.block_labels[row][col].setStyleSheet("""
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
                            current_text = self.block_labels[row][col].toPlainText()
                            block_header = current_text.split('\n')[0]
                            empty_text = "Empty"
                            self.block_labels[row][col].setPlainText(f"{block_header}\n{empty_text}")
                            self.block_labels[row][col].setStyleSheet("""
                                        QTextEdit {
                                            background-color: red;
                                            border: 1px solid black;
                                            padding: 5px;
                                            font-size: 12px;
                                            color: black;
                                            font-weight: bold;
                                        }
                                    """)
                else:
                    for row, block in enumerate(date.blocklist):
                        
                        current_text = self.block_labels[row][col].toPlainText()
                        block_header = current_text.split('\n')[0]
                        empty_text = "Empty"
                        self.block_labels[row][col].setPlainText(f"{block_header}\n{empty_text}")  
                        self.block_labels[row][col].setStyleSheet("""
                                        QTextEdit {
                                        background-color: red;
                                        border: 1px solid black;
                                        padding: 5px;
                                        font-size: 12px;
                                        color: black;
                                        font-weight: bold;
                                            }
                                        """)

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
