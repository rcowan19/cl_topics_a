# ISA Assignment Application

The **ISA Assignment Application** is a Python-based tool designed to facilitate priority-based assignment of ISA to Workjobs, streamlining the scheduling process for Mrs.Pond. With a user friendly GUI, the application allows Mrs.Pond to import student and classes data, and quickly generate assignments that meet student and instituational needs.

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

**2. Classes CSV:** Defines all dates, their term, month, day, and school day label

- **Columns:**
  - Term: Write the term on its own line with only this colunm filled; All dates under it until next term will be assinged to this term
  - calendar_day: day-month (3 letter abreviation, ex. Sep)
  - d_label: The school day that the day is "D#"
  - weekday: Day of the week the date falls on

## Usage

**1. Launching the Application:**

- Run the application with:
  python main.py
- The GUI will open, displaying options for importing data or clearing loaded data

**2. Importing Data:**

- Use the "Upload Student Frees" button to load the Students CSV.
- Use the "Upload Classes Info" button to load the Classes CSV.
- Buttons will turn green when files are succesfully uploaded
- Error Message will appear if the files aren't correct
- If data is persisted it will say, click "Clear Saved Data" to reset

**3. Assigning Workjobs:**

- Click the "Countinue" button once both students and classes files are uploaded to open main ui
- Select a Cycle from the Cycle Dropdown
- Hit sumbit to run the assignment algorithm and assign students

**4. Reviewing Assignments:**

- Review the Assignments of students:
  - Assigned Students Tab:
    View assignments of the students, as a grid with all relvant info about the block a student is assigned too
  - Unassigned Students Tab:
    View any unassigned students
- Since the Algorithm has random, hitting submit multiple times will allow you to find a potential better results

**6. Resetting Saved Data:**
The application automatically saves the uploaded classes and students info, if data is persisted it will say it; On the upload wiondow click "Clear Saved Data" to reset and upload new files

## Features

- **Assigns all ISAs quickly and correctly**: Automatically assigns students to blocks based on availability.
- **Visually Appeling GUI**: UI is made intuitatively to allow the user to easily read the assignments that have been made
- **Program Persits**: The program saves your data so you can come back and assign studetns without having to reupload the files

## Troubleshooting and Tips

- **CSV Formatting**: Ensure CSV files have consistent headers. Errors may occur if columns are misnamed or misaligned.
- **Reimporting Data**: If any data updates, simply reimport the CSV files without restarting the application.

## Contact Information

For assistance or to provide feedback, please contact:

**Email**: roan_cowan@loomis.org
