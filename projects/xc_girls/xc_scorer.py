import csv
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tkinter import ttk

# Define the Time class
class Time:
    def __init__(self, race_time):
        self.minutes, self.seconds = [float(t) for t in race_time.split(":")]

    def __str__(self):
        return f"{int(self.minutes):02}:{self.seconds:05.2f}"

# Define the Athlete class
class Athlete:
    def __init__(self, name, team, place, time):
        self.name = name
        self.team = team
        self.place = place
        self.time = Time(time)
        self.new_place = None  # Initialize new_place

    def __str__(self):
        return (f"Athlete: {self.name}, Team: {self.team}, Place: {self.place}, "
                f"Time: {self.time}")

    def __repr__(self):
        return f"('{self.name}', '{self.team}', {self.place}, '{self.time}')"

# Define the Team class
class Team:
    def __init__(self):
        self.teams = {}

    def add_athlete(self, athlete):
        if athlete.team not in self.teams:
            self.teams[athlete.team] = []
        self.teams[athlete.team].append(athlete)

    def get_varsity(self):
        varsity_teams = {}
        for team_name, athletes in self.teams.items():
            sorted_athletes = sorted(athletes, key=lambda x: int(x.place))
            top_7 = sorted_athletes[:7]
            varsity_teams[team_name] = top_7
        return varsity_teams

    def get_junior_varsity(self):
        junior_varsity_teams = {}
        for team_name, athletes in self.teams.items():
            sorted_athletes = sorted(athletes, key=lambda x: int(x.place))
            next_7 = sorted_athletes[7:14]
            junior_varsity_teams[team_name] = next_7
        return junior_varsity_teams

# Function to create athletes from CSV
def athlete_creator(csv_file):
    athletes = []
    with open(csv_file, mode='r') as file:
        csv_dict = csv.DictReader(file)
        for dict_row in csv_dict:
            name = dict_row['Name']
            team = dict_row['Team name']
            place = dict_row['Place']
            time = dict_row['Time']
            athlete = Athlete(name, team, place, time)
            athletes.append(athlete)
    return athletes

# Global variables to store data across views
athletes_list = []
varsity_results = {}
jv_results = {}
file_path = ""

# Function to import CSV file
def import_file():
    global athletes_list, varsity_results, jv_results, file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Select a CSV file"
    )
    if file_path:
        varsity_results, jv_results, athletes_list = process_file(file_path)  # Process the imported file
        create_dashboard()

# Function to process the CSV file
def process_file(file_path):
    athletes_list = athlete_creator(file_path)

    team_filter = Team()
    for athlete in athletes_list:
        team_filter.add_athlete(athlete)

    # Varsity results
    varsity_teams = team_filter.get_varsity()
    varsity_results = compare_all_teams(varsity_teams)

    # Junior Varsity results
    junior_varsity_teams = team_filter.get_junior_varsity()
    jv_results = compare_all_teams(junior_varsity_teams)

    return varsity_results, jv_results, athletes_list

# Function to score a matchup between two teams
def scorer(team_1, team_2, team_1_name, team_2_name):
    all_athletes = team_1 + team_2
    sorted_athletes = sorted(all_athletes, key=lambda x: int(x.place))
    team_1_score = {}
    team_2_score = {}
    new_place = 1

    for athlete in sorted_athletes:
        if athlete in team_1 and len(team_1_score) < 5:
            team_1_score[athlete.name] = new_place
            athlete.new_place = new_place
        elif athlete in team_2 and len(team_2_score) < 5:
            team_2_score[athlete.name] = new_place
            athlete.new_place = new_place
        new_place += 1
        if len(team_1_score) == 5 and len(team_2_score) == 5:
            break

    team_1_total = sum(team_1_score.values())
    team_2_total = sum(team_2_score.values())

    if team_1_total < team_2_total:
        winner = team_1_name
    elif team_2_total < team_1_total:
        winner = team_2_name
    else:
        winner = "Tie"

    for athlete in team_1 + team_2:
        if athlete.name not in team_1_score and athlete.name not in team_2_score:
            athlete.new_place = None

    team_1_list = []
    for athlete in team_1:
        if athlete.new_place is not None:
            team_1_list.append(f"{athlete.name} - {athlete.new_place}")
    team_2_list = []
    for athlete in team_2:
        if athlete.new_place is not None:
            team_2_list.append(f"{athlete.name} - {athlete.new_place}")

    return {
        "Team 1 Score": team_1_total,
        "Team 1 Results": team_1_list,
        "Team 2 Score": team_2_total,
        "Team 2 Results": team_2_list,
        "Winner": winner,
        "Team 1 Name": team_1_name,
        "Team 2 Name": team_2_name
    }

# Function to compare all teams
def compare_all_teams(teams):
    results = {}
    team_names = list(teams.keys())
    for i in range(len(team_names)):
        for j in range(i + 1, len(team_names)):
            team_1_name = team_names[i]
            team_2_name = team_names[j]
            team_1 = teams[team_1_name]
            team_2 = teams[team_2_name]
            result = scorer(team_1, team_2, team_1_name, team_2_name)
            results[f"{team_1_name} vs {team_2_name}"] = result
    return results

# Function to create the sidebar
def create_sidebar(parent_frame, times_command=None, scoring_command=None, download_command=None):
    # Sidebar with corner radius
    sidebar = ctk.CTkFrame(
        parent_frame,
        width=100,
        height=900,
        corner_radius=15,
        fg_color="#992b2c"
    )
    sidebar.grid(row=0, column=0, rowspan=1, sticky="nsew", padx=(15, 0), pady=20)

    # Load images using CTkImage
    logo_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/logo.jpg"), size=(90, 110))
    clock_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/clock.png"), size=(45, 45))
    trophy_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/trophy.png"), size=(45, 50))
    download_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/download.png"), size=(55, 60))

    # Logo on sidebar
    logo_button = ctk.CTkButton(
        sidebar,
        text="",
        image=logo_img,
        width=100,
        height=70,
        corner_radius=15,
        fg_color="#932b2c",
        hover_color="#932b2c"
    )
    logo_button.grid(row=0, column=0, padx=5, pady=(15, 15))

    # Times button on sidebar
    results_button = ctk.CTkButton(
        sidebar,
        text="  Times  ",
        width=100,
        height=70,
        compound="top",
        image=clock_img,
        corner_radius=15,
        fg_color="#932b2c",
        hover_color="#600000",
        command=times_command  
    )
    results_button.grid(row=1, column=0, padx=0, pady=(15, 15))

    # Trophy button on sidebar
    scoring_button = ctk.CTkButton(
        sidebar,
        text="  Scoring  ",
        font=("Arial", 12),
        width=100,
        height=70,
        compound="top",
        image=trophy_img,
        corner_radius=15,
        fg_color="#932b2c",
        hover_color="#600000",
        command=scoring_command 
    )
    scoring_button.grid(row=2, column=0, padx=0, pady=(15, 15))

    # Download button on sidebar
    download_button = ctk.CTkButton(
        sidebar,
        text="Download",
        image=download_img,
        compound="top",
        width=100,
        height=70,
        corner_radius=15,
        fg_color="#932b2c",
        hover_color="#600000",
        command=download_command  
    )
    download_button.grid(row=3, column=0, padx=0, pady=(15, 15))

    # Configure sidebar grid to expand vertically
    sidebar.grid_rowconfigure(4, weight=1)  

    return sidebar

# Function to create the dashboard view
def create_dashboard():
    global dashboard_frame, image_label, import_button
    # Hide the initial widgets
    image_label.grid_forget()
    import_button.grid_forget()

    # Hide the times frame if it's visible
    if 'times_frame' in globals():
        times_frame.grid_forget()

    # Now create dashboard_frame and use grid
    dashboard_frame = ctk.CTkFrame(app, fg_color="#A9A9A9")
    dashboard_frame.grid(row=0, column=0, sticky="nsew", columnspan=1, rowspan=1)

    # Grid configuration for the dashboard frame
    dashboard_frame.grid_columnconfigure(0, weight=0)  # Sidebar column
    dashboard_frame.grid_columnconfigure(1, weight=1)  # Content column
    dashboard_frame.grid_rowconfigure(0, weight=1)

    # Create the sidebar
    sidebar = create_sidebar(
        dashboard_frame,
        times_command=show_times,
        scoring_command=None,
        download_command=None
    )

    # Main content area with two stacked frames
    results_area = ctk.CTkFrame(dashboard_frame, corner_radius=20, fg_color="#A9A9A9")
    results_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    results_area.grid_rowconfigure(0, weight=1)
    results_area.grid_rowconfigure(1, weight=1)
    results_area.grid_columnconfigure(0, weight=1)

    # Create the two stacked frames
    upper_box = ctk.CTkFrame(results_area, fg_color="#932b2c")
    upper_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
    upper_box.grid_rowconfigure(0, weight=0)
    upper_box.grid_rowconfigure(1, weight=1)
    upper_box.grid_columnconfigure(0, weight=1)

    lower_box = ctk.CTkFrame(results_area, fg_color="#932b2c")
    lower_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
    lower_box.grid_rowconfigure(0, weight=0)
    lower_box.grid_rowconfigure(1, weight=1)
    lower_box.grid_columnconfigure(0, weight=1)

    # Now, display the varsity and JV results in the upper and lower boxes
    display_results(upper_box, varsity_results, "Varsity Results")
    display_results(lower_box, jv_results, "Junior Varsity Results")

# Function to show the times view
def show_times():
    # Hide the dashboard frame
    dashboard_frame.grid_forget()

    global times_frame
    times_frame = ctk.CTkFrame(app, fg_color="#A9A9A9")
    times_frame.grid(row=0, column=0, sticky="nsew", columnspan=1, rowspan=1)

    # Grid configuration for the times frame
    times_frame.grid_columnconfigure(0, weight=0)  # Sidebar column
    times_frame.grid_columnconfigure(1, weight=1)  # Content column
    times_frame.grid_rowconfigure(0, weight=1)

    # Create sidebar
    sidebar = create_sidebar(
        times_frame,
        times_command=None,  # Disable Times button
        scoring_command=create_dashboard,  # Return to dashboard
        download_command=None
    )

    # Main content area
    content_frame = ctk.CTkFrame(times_frame, fg_color="#A9A9A9")
    content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    # Create a frame similar to upper_box in display_results
    times_box = ctk.CTkFrame(content_frame, fg_color="#932b2c")
    times_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    times_box.grid_columnconfigure(0, weight=1)
    times_box.grid_rowconfigure(0, weight=0)
    times_box.grid_rowconfigure(1, weight=1)

    # Create title label
    title_label = ctk.CTkLabel(times_box, text="Athlete Times", font=("Arial", 30, "bold"), text_color="white")
    title_label.grid(row=0, column=0, pady=10)

    # Create a frame to hold the Treeview
    tree_frame = ctk.CTkFrame(times_box, fg_color="#A9A9A9")
    tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    tree_frame.grid_columnconfigure(0, weight=1)
    tree_frame.grid_rowconfigure(0, weight=1)

    # Configure the style for Treeview to match the app's theme
    style = ttk.Style()
    style.theme_use("default")

    # Set the Treeview style to match the colors
    style.configure("Custom.Treeview",
                    background="#ffffff",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#ffffff",
                    bordercolor="#A9A9A9",
                    borderwidth=0)

    style.map('Custom.Treeview', background=[('selected', '#932b2c')])

    tree_columns = ("Place", "Name", "Team", "Time")
    tree = ttk.Treeview(tree_frame, columns=tree_columns, show="headings", style="Custom.Treeview")
    tree.grid(row=0, column=0, sticky='nsew')

    # Define headings with custom fonts
    for col in tree_columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    # Access athletes_list
    # Sort athletes_list by place
    sorted_athletes = sorted(athletes_list, key=lambda x: int(x.place))

    # Insert data
    for athlete in sorted_athletes:
        tree.insert("", "end", values=(athlete.place, athlete.name, athlete.team, str(athlete.time)))

    # Add scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    # Optional: Adjust the appearance of the scrollbar to match the theme
    style.configure("Vertical.TScrollbar",
                    gripcount=0,
                    background="#A9A9A9",
                    darkcolor="#A9A9A9",
                    lightcolor="#A9A9A9",
                    troughcolor="#A9A9A9",
                    bordercolor="#A9A9A9",
                    arrowcolor="#A9A9A9")

# Function to score a matchup between two teams
def scorer(team_1, team_2, team_1_name, team_2_name):
    all_athletes = team_1 + team_2
    sorted_athletes = sorted(all_athletes, key=lambda x: int(x.place))
    team_1_score = {}
    team_2_score = {}
    new_place = 1

    for athlete in sorted_athletes:
        if athlete in team_1 and len(team_1_score) < 5:
            team_1_score[athlete.name] = new_place
            athlete.new_place = new_place
        elif athlete in team_2 and len(team_2_score) < 5:
            team_2_score[athlete.name] = new_place
            athlete.new_place = new_place
        new_place += 1
        if len(team_1_score) == 5 and len(team_2_score) == 5:
            break

    team_1_total = sum(team_1_score.values())
    team_2_total = sum(team_2_score.values())

    if team_1_total < team_2_total:
        winner = team_1_name
    elif team_2_total < team_1_total:
        winner = team_2_name
    else:
        winner = "Tie"

    for athlete in team_1 + team_2:
        if athlete.name not in team_1_score and athlete.name not in team_2_score:
            athlete.new_place = None

    team_1_list = []
    for athlete in team_1:
        if athlete.new_place is not None:
            team_1_list.append(f"{athlete.name} - {athlete.new_place}")
    team_2_list = []
    for athlete in team_2:
        if athlete.new_place is not None:
            team_2_list.append(f"{athlete.name} - {athlete.new_place}")

    return {
        "Team 1 Score": team_1_total,
        "Team 1 Results": team_1_list,
        "Team 2 Score": team_2_total,
        "Team 2 Results": team_2_list,
        "Winner": winner,
        "Team 1 Name": team_1_name,
        "Team 2 Name": team_2_name
    }

# Function to compare all teams
def compare_all_teams(teams):
    results = {}
    team_names = list(teams.keys())
    for i in range(len(team_names)):
        for j in range(i + 1, len(team_names)):
            team_1_name = team_names[i]
            team_2_name = team_names[j]
            team_1 = teams[team_1_name]
            team_2 = teams[team_2_name]
            result = scorer(team_1, team_2, team_1_name, team_2_name)
            results[f"{team_1_name} vs {team_2_name}"] = result
    return results

# Function to display results in the dashboard
def display_results(frame, results, title):
    # Create title label
    title_label = ctk.CTkLabel(frame, text=title, font=("Arial", 30, "bold"), text_color="white")
    title_label.grid(row=0, column=0, pady=10, sticky="nsew", padx=10)

    # Create frames to hold the matchups
    matchups_frame = ctk.CTkFrame(frame, fg_color="#A9A9A9")
    matchups_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    matchups_frame.grid_columnconfigure(0, weight=1)

    # Calculate the number of teams
    team_names = set()
    for data in results.values():
        team_names.add(data['Team 1 Name'])
        team_names.add(data['Team 2 Name'])
    number_of_teams = len(team_names)

    # Set the number of columns based on the number of teams
    if number_of_teams <= 3:
        columns = int(number_of_teams * (number_of_teams - 1) / 2)
    else:
        columns = 10

    # Configure the columns to be even
    for col in range(columns):
        matchups_frame.grid_columnconfigure(col, weight=1, uniform="matchup")

    # Variables to loop through making matchups
    current_column = 0
    current_row = 0

    # For each matchup, create a frame inside matchups frame
    for data in results.values():
        matchup_frame = ctk.CTkFrame(matchups_frame, fg_color="#992b2c", corner_radius=10)
        matchup_frame.grid(row=current_row, column=current_column, padx=10, pady=10, sticky="nsew")
        matchup_frame.grid_rowconfigure(0, weight=1)
        matchup_frame.grid_columnconfigure(0, weight=1)

        current_column += 1
        if current_column >= columns:
            current_column = 0
            current_row += 1

        # Create a label for who's in each matchup
        teams_title = f"{data['Team 1 Name']} vs {data['Team 2 Name']}"
        teams_label = ctk.CTkLabel(matchup_frame, text=teams_title, font=("Arial", 22, "bold"), text_color="white")
        teams_label.grid(row=0, column=0, pady=5, sticky="nsew", padx=10)

        # Create a frame to hold result columns
        columns_frame = ctk.CTkFrame(matchup_frame, fg_color="#A9A9A9")
        columns_frame.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        columns_frame.grid_columnconfigure(0, weight=1, uniform="team")
        columns_frame.grid_columnconfigure(1, weight=1, uniform="team")
        columns_frame.grid_rowconfigure(0, weight=1)

        # Create result columns for each team
        team1_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        team1_frame.grid_columnconfigure(0, weight=1)
        team1_frame.grid_rowconfigure(1, weight=1)

        team2_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team2_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        team2_frame.grid_columnconfigure(0, weight=1)
        team2_frame.grid_rowconfigure(1, weight=1)

        # Add athlete and new_place to each column for team 1
        team1_label = ctk.CTkLabel(team1_frame, text=data['Team 1 Name'], font=("Arial", 14, "bold"))
        team1_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        athletes_frame1 = ctk.CTkFrame(team1_frame, fg_color="#ffffff")
        athletes_frame1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        athletes_frame1.grid_columnconfigure(0, weight=1)
        athletes_frame1.grid_rowconfigure(0, weight=1)
        for athlete_info in data['Team 1 Results']:
            athlete_label = ctk.CTkLabel(athletes_frame1, text=athlete_info, fg_color="#ffffff")
            athlete_label.pack(anchor="center", padx=5, pady=2)

        # Total at the bottom
        team1_total_label = ctk.CTkLabel(team1_frame, text=f"Total: {data['Team 1 Score']}", font=("Arial", 12, "bold"))
        team1_total_label.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

        # For team 2
        team2_label = ctk.CTkLabel(team2_frame, text=data['Team 2 Name'], font=("Arial", 14, "bold"))
        team2_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        athletes_frame2 = ctk.CTkFrame(team2_frame, fg_color="#ffffff")
        athletes_frame2.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        athletes_frame2.grid_columnconfigure(0, weight=1)
        athletes_frame2.grid_rowconfigure(0, weight=1)
        for athlete_info in data['Team 2 Results']:
            athlete_label = ctk.CTkLabel(athletes_frame2, text=athlete_info, fg_color="#ffffff")
            athlete_label.pack(anchor="center", padx=5, pady=2)

        # Total at the bottom
        team2_total_label = ctk.CTkLabel(team2_frame, text=f"Total: {data['Team 2 Score']}", font=("Arial", 12, "bold"))
        team2_total_label.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

        # At the bottom in the center, show the winner
        winner_label = ctk.CTkLabel(matchup_frame, text=f"Winner: {data['Winner']}", font=("Arial", 16, "bold"), text_color="white")
        winner_label.grid(row=2, column=0, pady=5, sticky="nsew", padx=10)

# Create the main window
app = ctk.CTk()
app.title("Cross Country Scorer Application")
app.geometry("1500x920")

# Set the appearance mode and color theme
ctk.set_appearance_mode("light")
app.configure(fg_color="#A9A9A9")

# Configure grid columns and rows to expand and adjust
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

# Load the image using CTkImage
try:
    image_path = "cl_topics_a/projects/xc_girls/xc.png"
    image = ctk.CTkImage(Image.open(image_path), size=(485, 540))
except Exception as e:
    print(f"Error loading image: {e}")
    image = None

# Create a label for the image
global image_label  # Declare as global to access later
if image:
    image_label = ctk.CTkLabel(app, image=image, text="")
    image_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nsew")
else:
    image_label = ctk.CTkLabel(app, text="Image not found", font=("Arial", 20))
    image_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nsew")

# Create the "Import Race Results" button
global import_button  # Declare as global to access later
import_button = ctk.CTkButton(
    app,
    text="Import Race Results",
    command=import_file,
    corner_radius=25,
    height=100,
    width=300,
    font=("Courier", 30, "bold"),
    fg_color="#992b2c",
    hover_color="#600000"
)
import_button.grid(row=1, column=0, padx=20, pady=20, sticky="s")

# Start the Tkinter event loop
app.mainloop()
