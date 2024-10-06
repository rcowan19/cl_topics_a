import csv

# Define the student 
class Student:
    def __init__(self, name, frees, grade):
        self.name = name
        self.frees = frees 
        self.grade = grade

# Define the workjob 
class Workjob:
    def __init__(self, name, w_type, min_students, max_students, priority, periods):
        self.name = name
        self.type = w_type
        self.min_students = min_students
        self.max_students = max_students
        self.priority = priority
        self.periods = periods  

# Read student information from the csv
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
            free_list = []
            for period, value in frees.items():
                if value == 1:
                    free_list.append(period)
            students.append(Student(name, free_list, grade))
    return students

# Read workjob information from the csv
def read_workjob_file(filename):
    workjobs = []
    with open(filename, 'r') as file:
        reader_dict = csv.DictReader(file)
        for row in reader_dict:
            name = row["name"]
            w_type = row["type"]
            min_students = row["min_students"]
            max_students = row["max_students"]
            priority = row["priority"]
            periods = list(row["periods"].split(','))
            workjobs.append(Workjob(name, w_type, min_students, max_students, priority, periods))
    return workjobs


students = read_student_file('cl_topics_a\\projects\\workjobs\\StudentFreesClean.csv')
workjobs = read_workjob_file('cl_topics_a\\projects\\workjobs\\Workjobs.csv')

for student in students:
    print(f"Student: {student.name}, Grade:{student.grade} Frees: {student.frees}")

for workjob in workjobs:
    print(f"Workjob: {workjob.name}, Periods: {workjob.periods}, Priority: {workjob.priority}")
