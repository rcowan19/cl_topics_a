import csv
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk  

class Time:
    def __init__(self, race_time):
        self.minutes, self.seconds = [float(t) for t in race_time.split(":")]

    def __str__(self):
        return f"{int(self.minutes):02}:{self.seconds:05.2f}"
    
class Athlete:
    def __init__(self, name, team, place, time):
        self.name = name
        self.team = team
        self.place = place
        self.time = Time(time)
        
    def __str__(self):
        return (f"Athlete: {self.name}, Team: {self.team}, Place: {self.place}, " 
                f"Time: {self.time}")

    def __repr__(self):
        return f"('{self.name}', '{self.team}', {self.place}, '{self.time}')"
    
class Team:
    def __init__(self):
        self.teams = {}

    def add_athlete(self, athlete):
        if athlete.team not in self.teams:
            self.teams[athlete.team] = []
        self.teams[athlete.team].append(athlete)

    def display_teams(self):
        for team_name, athletes in self.teams.items():
            print(f"Team: {team_name}")
            for athlete in athletes:
                print(f"{athlete}")
            print()

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
    
# Define the athlete_creator function before it is used
def athlete_creator(csv_file):
    athletes = []
    with open(csv_file, mode='r') as file:
        csv_dict = csv.DictReader(file)
        for dict in csv_dict:
            name = dict['Name']
            team = dict['Team name']
            place = dict['Place']
            time = dict['Time']
            athlete = Athlete(name, team, place, time)
            athletes.append(athlete)
    return athletes

# Function to handle file import
def import_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],  
        title="Select a CSV file"
    )
    
    process_file(file_path)  # Process the imported file
    create_dashboard() 

def process_file(file_path):
    athletes_list = athlete_creator(file_path)

    team_filter = Team()
    for athlete in athletes_list:
        team_filter.add_athlete(athlete)

    team_filter.display_teams()
   
    # Varsity results
    varsity_teams = team_filter.get_varsity()
    results = compare_all_teams(varsity_teams)
    for dual, result in results.items():
        print(f"\nV {dual}")
        print()
        print(f"{result["Team 1 Name"]} Score: {result['Team 1 Score']}")
        for athlete in result["Team 1 Results"]:
            print(athlete)
        print()
        print(f"{result["Team 2 Name"]} Score: {result['Team 2 Score']}")
        for athlete in result["Team 2 Results"]:
            print(athlete)
        print(f"Winner: {result['Winner']}")

    # Junior Varsity results
    junior_varsity_teams = team_filter.get_junior_varsity()
    results = compare_all_teams(junior_varsity_teams)
    for dual, result in results.items():
        print(f"\nV {dual}")
        print()
        print(f"{result["Team 1 Name"]} Score: {result['Team 1 Score']}")
        for athlete in result["Team 1 Results"]:
            print(athlete)
        print()
        print(f"{result["Team 2 Name"]} Score: {result['Team 2 Score']}")
        for athlete in result["Team 2 Results"]:
            print(athlete)
        print(f"Winner: {result['Winner']}")
    

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

    team_1_list = []
    for key, value in team_1_score.items():
        team_1_list.append(f"{key} - {value}")
    team_2_list = []
    for key, value in team_2_score.items():
        team_2_list.append(f"{key} - {value}")

    return {
        "Team 1 Score": team_1_total,
        "Team 1 Results": team_1_list,
        "Team 2 Score": team_2_total,
        "Team 2 Results": team_2_list,
        "Winner": winner,
        "Team 1 Name": team_1_name,
        "Team 2 Name": team_2_name
    }

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

def create_dashboard():
    global root
    root.destroy()
    root = ctk.CTk()
    root.title("Dashboard")
    root.geometry("1600x900")
    
    # Create a CTkFrame to act as the background and cover the root window
    background_frame = ctk.CTkFrame(root, fg_color="#A9A9A9")  # Updated background color (deep navy blue)
    background_frame.pack(fill="both", expand=True)
    
    # Grid configuration for the background frame
    background_frame.grid_columnconfigure(0, weight=0)
    background_frame.grid_columnconfigure(1, weight=1)
    background_frame.grid_rowconfigure(0, weight=1)

    # Sidebar with corner radius
    sidebar = ctk.CTkFrame(
        background_frame, 
        width=100, 
        height=900, 
        corner_radius=15,
        fg_color="#992b2c"  # Keeping the sidebar color the same
        )
    sidebar.grid(row=0, column=0, rowspan=1, sticky="nsew", padx=(15,0), pady=10)

    # Logo on sidebar
    img = Image.open("cl_topics_a\\projects\\xc_girls\\logo.jpg")  
    img_resized = img.resize((90, 110)) 
    logo_img = ImageTk.PhotoImage(img_resized)
    logo_button = ctk.CTkButton(
        sidebar, 
        text="",
        image=logo_img,
        width=100, 
        height=70,
        corner_radius=15,
        fg_color="#992b2c", 
        hover_color="#992b2c"
        )
    logo_button.grid(row=0, column=0, padx=5, pady=(5,5))

    # Times button on sidebar
    img = Image.open("cl_topics_a\\projects\\xc_girls\\clock.png")  
    img_resized = img.resize((45, 45))  
    clock_img = ImageTk.PhotoImage(img_resized)
    results_button = ctk.CTkButton(
        sidebar, 
        text="  Times  ", 
        width=100, 
        height=70,
        compound="top",
        image=clock_img,
        corner_radius=15,
        fg_color="#992b2c", 
        hover_color="#600000"
    )
    results_button.grid(row=1, column=0, padx=0, pady=(5,5))

    # Trophy button on sidebar
    img = Image.open("cl_topics_a\\projects\\xc_girls\\trophy.png")  
    img_resized = img.resize((45, 50))  
    trophy_img = ImageTk.PhotoImage(img_resized)
    courses_button = ctk.CTkButton(
        sidebar, 
        text="  Scoring  ",
        font=("Arial", 12),
        width=100,
        height=70,
        compound="top",
        image=trophy_img,
        corner_radius=15,
        fg_color="#992b2c", 
        hover_color="#600000"
    )
    courses_button.grid(row=2, column=0, padx=0, pady=(5,5))

    # Download button on sidebar
    img = Image.open("cl_topics_a\\projects\\xc_girls\\download.png")  
    img_resized = img.resize((55, 60)) 
    download_img = ImageTk.PhotoImage(img_resized)
    download_button = ctk.CTkButton(
        sidebar, 
        text="Download",
        image=download_img,
        compound="top",
        width=100, 
        height=70,
        corner_radius=15,
        fg_color="#992b2c", 
        hover_color="#600000"
        )
    download_button.grid(row=3, column=0, padx=0, pady=(10,5))

    # Main content area with two stacked frames
    results_area = ctk.CTkFrame(background_frame, corner_radius=15, fg_color="#f0f0f0")  # Updated content area color (light grey)
    results_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    results_area.grid_rowconfigure(0, weight=1)
    results_area.grid_rowconfigure(1, weight=1)
    results_area.grid_columnconfigure(0, weight=1)

    # Create the two stacked frames
    upper_box = ctk.CTkFrame(results_area, fg_color="#ffffff")  # Upper box with white background
    upper_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

    lower_box = ctk.CTkFrame(results_area, fg_color="#ffffff")  # Lower box with white background
    lower_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

    root.mainloop()

# Create the main window
root = ctk.CTk()
root.title("Cross Country Scorer Application")
root.geometry("1000x700")

# Set the appearance mode and color theme
ctk.set_appearance_mode("light")
root.configure(fg_color="#A9A9A9")

# Load the image
image_path = "cl_topics_a\\projects\\xc_girls\\xc.png"  
image = Image.open(image_path)
image = image.resize((685, 740))  
photo = ImageTk.PhotoImage(image)

# Create a label for the image
image_label = ctk.CTkLabel(root, image=photo, text="")
image_label.grid(row=0, column=0, padx=20, pady=(30, 10), columnspan=2, sticky="nsew")

# Create the "Import a File" button
import_button = ctk.CTkButton(
    root, 
    text="Import Race Results", 
    command=import_file, 
    corner_radius=25,  
    height=100, 
    width=300, 
    font=("Courier", 30, "bold"), 
    fg_color="#73000a", 
    hover_color="#950000"
)
import_button.grid(row=1, column=0, padx=20, pady=20, columnspan=2, sticky="sew")

# Configure grid columns and rows to expand and adjust
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)


# Start the Tkinter event loop
root.mainloop()