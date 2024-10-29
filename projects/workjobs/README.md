# Workjob Assignment Application 
The **Workjob Assignment Application** is a Python-based tool designed to facilitate priority-based assignment of workjobs to students, streamlining the scheduling process for Loomis Chaffee. With a user friendly GUI, the application allows Loomis faculty to import student and workjob data, configure priority settings, and quickly generate assignments that meet student and instituational needs.

## Installation 

**Prerequisites:**
- Python 3.6 or Higher

**Steps**
1. Download or clone the repository.
2. Instaall the required dependencies:
pip install --upgrade pip
pip install customtkinter

## File Input Format
**1. Student CSV:** Contains student information and free blocks.
- **Columns:**
    - Student ID: Unique Identifier for each student.
    - Name: Students Full Name.
    - Grade: Grade Level
    - All block day combos (D1B2 through D7B7): Used to check if student has a free block; value of 1 is free, blank is not free

**2. Workjobs CSV:** Defines all workjobs, their type, min/max and other prefrences
- **Columns:**
    - Workjob Name: Name of the workjob that is human readable
    - Type: "T" for total min/max and "E" for every period
    - Min: Total min for type "T"; Min per period for type "E"
    - Max: Total max for type "T"; Max per period for type "E"
    - Priority: Number 1-10; 1 Highest Priority and 10 Lowest Priority
    - Periods: A list of period when the workjob meets (1,2,3,4,B#)
    - Alt_name: Alternative name of workjob that is used for Veracross

## Usage

**1. Launching the Application:**
- Run the application with:
python main.py
- The GUI will open, displaying options for importing data and assigning workjobs

**2. Importing Data:**
- Use the "Import Students" button to load the Students CSV.
- Use the "Import Workjobs" button to load the Workjobs CSV.
- Buttons will turn green when files are succesfully uploaded 
- Error Message will appear if the files aren't correct

**3. Assigning Workjobs:**
- Click the "Assign Workjobs" button once both students and workjobs files are uploaded to generate assignments for student

**4. Reviewing Assignments:**
- Review the Assignments of students:
    - Assigned Students Tab: 
    View assignments of the students, workjob and period
    - Unassigned Students Tab:
    View any unassigned students
    - Drop Down:
    Filter the assignments by workjob for easier viewing

**5. Exporting Results:**
- Use "Export Results for Database" button to export results for veracross acceptable format:
- **Columns:**
    - Internal_Class_ID: Unique Identifier for each workjob.
    - Class_ID: Veracross Name for Workjob (D#-B#-WJ:internal_name-F)
    - School_year: Current school year, entered in entry box when exporting
    - Veracross_student_Id: Unique Identifier for eahc student
    - Grade_level: Students grade level
- Use "Export {Workjob}" to export a human readable results of each workjob:
- **Columns:**
    - Period: All block day combos (D1B2 through D7B7) when workjob meets
    - Student Names: Name of Students that are assigned to that workjob

**6. Resetting Saved Data:**
The application automatically saves the uploaded workjob and students csv, use the "Reset All" button to restart and clear all existing data

## Features

- **Priority-Based Assignment**: Automatically assigns students to workjobs based on preferences, grade level, and availability.
- **Data Import and Export**: Import student and workjob data from CSV files and export finalized assignments.

## Troubleshooting and Tips

- **CSV Formatting**: Ensure CSV files have consistent headers. Errors may occur if columns are misnamed or misaligned.
- **Reimporting Data**: If any data updates, simply reimport the CSV files without restarting the application.
- **Error Logs**: Check the console for any error messages related to data parsing or assignment conflicts.

## Contact Information

For assistance or to provide feedback, please contact:

**Email**: roan_cowan@loomis.org