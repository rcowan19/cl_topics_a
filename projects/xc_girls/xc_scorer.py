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
            if len(top_7) < 5:
                del varsity_teams[team_name]
        return varsity_teams

    def get_junior_varsity(self):
        junior_varsity_teams = {}
        for team_name, athletes in self.teams.items():
            sorted_athletes = sorted(athletes, key=lambda x: int(x.place))
            next_7 = sorted_athletes[7:14]
            junior_varsity_teams[team_name] = next_7
            if len(next_7) < 5:
                del junior_varsity_teams[team_name]
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
        varsity_results, jv_results, athletes_list = process_file(file_path)  
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
    team_1_rest = {}
    team_2_score = {}
    team_2_rest = {}
    new_place = 1

    for athlete in sorted_athletes:
        if athlete in team_1 and len(team_1_score) < 5:
            team_1_score[athlete.name] = new_place
            athlete.new_place = new_place
        elif athlete in team_1 and len(team_1_score) >= 5 and len(team_1_rest) < 2:
            team_1_rest[athlete.name] = new_place
            athlete.new_place = new_place
        elif athlete in team_2 and len(team_2_score) < 5:
            team_2_score[athlete.name] = new_place
            athlete.new_place = new_place
        elif athlete in team_2 and len(team_2_score) >= 5 and len(team_2_rest) < 2:
            team_2_rest[athlete.name] = new_place
            athlete.new_place = new_place
        new_place += 1

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

    team_1_list = [f"{athlete} - {place}" for athlete, place in team_1_score.items()]
    team_2_list = [f"{athlete} - {place}" for athlete, place in team_2_score.items()]
    team_1_rest_list = [f"{athlete} - {place}" for athlete, place in team_1_rest.items()]
    team_2_rest_list = [f"{athlete} - {place}" for athlete, place in team_2_rest.items()]

    return {
        "Team 1 Score": team_1_total,
        "Team 1 Results": team_1_list,
        "Team 1 Rest": team_1_rest_list,  
        "Team 2 Score": team_2_total,
        "Team 2 Results": team_2_list,
        "Team 2 Rest": team_2_rest_list, 
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
    if logo_img:
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
    if 'times_frame' in globals() and times_frame.winfo_exists():
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
        download_command=download_results  # Implement this function
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


# Placeholder function for download functionality
def download_results():
    # Implement the download functionality here
    pass

# Function to show the times view
def show_times():
    # Hide the dashboard frame
    if 'dashboard_frame' in globals() and dashboard_frame.winfo_exists():
        dashboard_frame.grid_forget()

    global times_frame
    times_frame = ctk.CTkFrame(app, fg_color="#A9A9A9")
    times_frame.grid(row=0, column=0, sticky="nsew", columnspan=1, rowspan=1)

    # Grid configuration for the times frame
    times_frame.grid_columnconfigure(0, weight=0) 
    times_frame.grid_columnconfigure(1, weight=1)  
    times_frame.grid_rowconfigure(0, weight=1)

    # Create sidebar
    sidebar = create_sidebar(
        times_frame,
        times_command=None,  
        scoring_command=create_dashboard, 
        download_command=download_results  
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

def display_results(frame, results, title):
    # Create title label
    title_label = ctk.CTkLabel(
        frame, 
        text=title, 
        font=("Arial", 30, "bold"), 
        text_color="white"
    )
    title_label.grid(row=0, column=0, pady=10, sticky="nsew", padx=10)

    # Create a frame for the scrollable area
    scrollable_frame = ctk.CTkFrame(frame, fg_color="#A9A9A9")
    scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    scrollable_frame.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_rowconfigure(0, weight=1)

    # Create a canvas and a scrollbar
    canvas = ctk.CTkCanvas(scrollable_frame, bg="#A9A9A9", highlightthickness=0)
    scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the scrollable content
    scrollable_content = ctk.CTkFrame(canvas, fg_color="#A9A9A9")

    # Add the scrollable_content to the canvas
    scrollable_window = canvas.create_window((0, 0), window=scrollable_content, anchor="nw")

    # Bind the <Configure> event of scrollable_content to update the scrollregion
    scrollable_content.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Bind the <Configure> event of the canvas to adjust the width of scrollable_content
    def on_canvas_configure(event):
        canvas.itemconfig(scrollable_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create frames to hold the matchups
    matchups_frame = ctk.CTkFrame(scrollable_content, fg_color="#A9A9A9")
    matchups_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Calculate the number of teams
    team_names = set()
    for data in results.values():
        team_names.add(data['Team 1 Name'])
        team_names.add(data['Team 2 Name'])
    number_of_teams = len(team_names)
    
    if number_of_teams <= 3:
        columns = int(number_of_teams * (number_of_teams - 1) / 2)
    else:
        columns = 3

    # Configure the columns to be even
    for col in range(columns):
        matchups_frame.grid_columnconfigure(col, weight=1, uniform="matchup")

    # Variables to loop through making matchups
    current_column = 0
    current_row = 0

    # For each matchup, create a frame inside matchups_frame
    for matchup_key, data in results.items():
        matchup_frame = ctk.CTkFrame(matchups_frame, fg_color="#992b2c", corner_radius=10)
        matchup_frame.grid(row=current_row, column=current_column, padx=10, pady=10, sticky="nsew")
        matchup_frame.grid_rowconfigure(0, weight=1)
        matchup_frame.grid_columnconfigure(0, weight=1)

        # Update column and row counters
        current_column += 1
        if current_column >= columns:
            current_column = 0
            current_row += 1

        # Teams Title
        teams_title = f"{data['Team 1 Name']} vs {data['Team 2 Name']}"
        teams_label = ctk.CTkLabel(
            matchup_frame, 
            text=teams_title, 
            font=("Arial", 22, "bold"), 
            text_color="white"
        )
        teams_label.grid(row=0, column=0, pady=5, sticky="nsew", padx=10)

        # Columns Frame
        columns_frame = ctk.CTkFrame(matchup_frame, fg_color="#A9A9A9")
        columns_frame.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)

        # Team 1 Frame
        team1_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        team1_frame.grid_columnconfigure(0, weight=1)

        # Team 2 Frame
        team2_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        team2_frame.grid_columnconfigure(0, weight=1)

        # Team 1 Results
        team1_label = ctk.CTkLabel(
            team1_frame, 
            text=data['Team 1 Name'], 
            font=("Arial", 14, "bold"), 
            anchor="center"
        )
        team1_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        for i, athlete_info in enumerate(data['Team 1 Results']):
            athlete_label = ctk.CTkLabel(
                team1_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i + 1, column=0, padx=5, pady=2, sticky="nsew")

        # Separator for extra runners (Team 1)
        separator = ctk.CTkLabel(
            team1_frame, 
            text="--", 
            fg_color="#ffffff", 
            anchor="center", 
            width=100
        )
        separator.grid(row=6, column=0, padx=5, pady=2, sticky="nsew")

        # Display the 6th and 7th runners (Team 1)
        for i, athlete_info in enumerate(data['Team 1 Rest'], start=7):
            athlete_label = ctk.CTkLabel(
                team1_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i, column=0, padx=5, pady=2, sticky="nsew")

        # Total at the bottom (Team 1)
        team1_total_label = ctk.CTkLabel(
            team1_frame, 
            text=f"Total: {data['Team 1 Score']}", 
            font=("Arial", 12, "bold"), 
            anchor="center"
        )
        team1_total_label.grid(row=9, column=0, pady=5, padx=5, sticky="nsew")

        # Team 2 Results
        team2_label = ctk.CTkLabel(
            team2_frame, 
            text=data['Team 2 Name'], 
            font=("Arial", 14, "bold"), 
            anchor="center"
        )
        team2_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        for i, athlete_info in enumerate(data['Team 2 Results']):
            athlete_label = ctk.CTkLabel(
                team2_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i + 1, column=0, padx=5, pady=2, sticky="nsew")

        # Separator for extra runners (Team 2)
        separator = ctk.CTkLabel(
            team2_frame, 
            text="--", 
            fg_color="#ffffff", 
            anchor="center", 
            width=100
        )
        separator.grid(row=6, column=0, padx=5, pady=2, sticky="nsew")

        # Display the 6th and 7th runners (Team 2)
        for i, athlete_info in enumerate(data['Team 2 Rest'], start=7):
            athlete_label = ctk.CTkLabel(
                team2_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i, column=0, padx=5, pady=2, sticky="nsew")

        # Total at the bottom (Team 2)
        team2_total_label = ctk.CTkLabel(
            team2_frame, 
            text=f"Total: {data['Team 2 Score']}", 
            font=("Arial", 12, "bold"), 
            anchor="center"
        )
        team2_total_label.grid(row=9, column=0, pady=5, padx=5, sticky="nsew")

        # Winner Label
        winner_label = ctk.CTkLabel(
            matchup_frame, 
            text=f"Winner: {data['Winner']}", 
            font=("Arial", 16, "bold"), 
            text_color="white", 
            anchor="center"
        )
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
image_path = "cl_topics_a/projects/xc_girls/xc.png"
image = ctk.CTkImage(Image.open(image_path), size=(485, 540))

# Create a label for the image
image_label = ctk.CTkLabel(app, image=image, text="")
image_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nsew")

# Create the "Import Race Results" button
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
