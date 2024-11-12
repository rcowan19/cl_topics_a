import csv

# Define or import your Date and Student classes
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


# Hardcoded file paths
STUDENT_FILE_PATH = "projects\isa\isa_frees.csv"
CLASS_FILE_PATH = "projects\isa\classes.csv"
# Initialize lists
dates = []
students = []
unassigned = []

# Function to read student data
def read_student_file():
    try:
        with open(STUDENT_FILE_PATH, 'r') as file:
            reader_dict = csv.DictReader(file)
            for row in reader_dict:
                name = row["Full Name"]
                frees = {block: int(row[block]) if row[block] else 0 
                         for block in row if block not in ["Total Frees", "Full Name", "Grade"]}
                free_list = [period for period, value in frees.items() if value == 1]
                free_number = int(row["Total Frees"])
                students.append(Student(name, free_list, free_number))
        print("Students successfully loaded.")
    except Exception as e:
        print(f"Error loading students: {e}")

# Function to read class data
def read_classes_file():
    try:
        with open(CLASS_FILE_PATH, 'r', encoding="utf-8-sig") as file:
            reader_dict = csv.DictReader(file)
            term = ""
            for row in reader_dict:
                if row["term"] in ["FALL TERM", "WINTER TERM", "SPRING TERM"]:
                    term = row["term"]
                calendar_day = row["calendar_day"]
                block_list = create_blocklist(row["d_label"])
                weekday = row["weekday"]
                if not calendar_day or not block_list or not weekday:
                    continue
                day, month = calendar_day.split("-")
                dates.append(Date(month, day, block_list, weekday, term))
        print("Class info successfully loaded.")
    except Exception as e:
        print(f"Error loading classes: {e}")

# Helper function to create blocklist
def create_blocklist(day):
    block_list = []
    if len(day) > 1 and day[1:].isdigit():
        day_num = int(day[1:])
        for i in range(4):
            block_num = ((day_num + i - 1) % 7) + 1
            block_list.append(f"{day}B{block_num}")
    return block_list

# Update run_algorithm to use Student objects directly
def run_algorithm(dates, students):
    assignments = {}
    usable_days = ["Monday", "Wednesday", "Friday"]

    for date in dates:
        if date.weekday in usable_days:
            start_date = "Sep-10"
            start_month = start_date.split("-")[0]
            start_day = int(start_date.split("-")[1])
            end_date = "Sep-18"
            end_month = end_date.split("-")[0]
            end_day = int(end_date.split("-")[1])
            month_day = f"{date.month}-{date.day}"
            print(int(date.day)>= start_day)
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
# Load data and run algorithm
if __name__ == "__main__":
    read_student_file()
    read_classes_file()
    run_algorithm(dates, students)
    print(unassigned)
