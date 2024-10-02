#import statements
import csv
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tkinter import ttk

#define the time class
class Time:
    #init funtion to format the time into minutes and seconds
    def __init__(self, race_time):
        self.minutes, self.seconds = [float(t) for t in race_time.split(":")]

    #str function to be able to print the time nicely
    def __str__(self):
        return f"{int(self.minutes):02}:{self.seconds:05.2f}"

#define the athlete class
class Athlete:
    #init function to take in the info of the athletes; name, team, place, time, new_place
    def __init__(self, name, team, place, time):
        self.name = name
        self.team = team
        self.place = place
        self.time = Time(time)
        self.new_place = None 

    #str function to be able to print the athlete nicely
    def __str__(self):
        return (f"Athlete: {self.name}, Team: {self.team}, Place: {self.place}, "f"Time: {self.time}")

    #repr function to be able to view the athlete in their dictionaries when printing debug statments
    def __repr__(self):
        return f"('{self.name}', '{self.team}', {self.place}, '{self.time}')"

#define the team class
class Team:
    #init function to take create an inital teams dictionary 
    def __init__(self):
        self.teams = {}

    #adds the athletes to their respective teams and create new teams
    def add_athlete(self, athlete):
        if athlete.team not in self.teams:
            self.teams[athlete.team] = []
        self.teams[athlete.team].append(athlete)

    #gets the varsity runners by sorting the athletes and taking the the top 7, also makes sure teams with less then 5 get removed
    def get_varsity(self):
        varsity_teams = {}
        for team_name, athletes in self.teams.items():
            sorted_athletes = sorted(athletes, key=lambda x: int(x.place))
            top_7 = sorted_athletes[:7]
            varsity_teams[team_name] = top_7
            if len(top_7) < 5:
                del varsity_teams[team_name]
        return varsity_teams

    #gets the junior varsity runners by sorting the athletes and taking the the next 7, also makes sure teams with less then 5 get removed
    def get_junior_varsity(self):
        junior_varsity_teams = {}
        for team_name, athletes in self.teams.items():
            sorted_athletes = sorted(athletes, key=lambda x: int(x.place))
            next_7 = sorted_athletes[7:14]
            junior_varsity_teams[team_name] = next_7
            if len(next_7) < 5:
                del junior_varsity_teams[team_name]
        return junior_varsity_teams

#function to create athletes from CSV
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

#global variables to store data across views of gui
athletes_list = []
varsity_results = {}
jv_results = {}
file_path = ""

#function to import CSV file
def import_file():
    global athletes_list, varsity_results, jv_results, file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")],title="Select a CSV file")
    varsity_results, jv_results, athletes_list = process_file(file_path)  
    create_dashboard()

#function to process the CSV file
def process_file(file_path):
    #creates the athletes by calling the athlete creator fucntion
    athletes_list = athlete_creator(file_path)

    #filters the athletes into teams by creating a team object and using the add athlete function
    team_filter = Team()
    for athlete in athletes_list:
        team_filter.add_athlete(athlete)

    #creates the varsity teams and then creates and scores all the matchups needed 
    varsity_teams = team_filter.get_varsity()
    varsity_results = compare_all_teams(varsity_teams)

    #creates the junior varsity teams and then creates and scores all the matchups needed 
    junior_varsity_teams = team_filter.get_junior_varsity()
    jv_results = compare_all_teams(junior_varsity_teams)

    #returns the results of the scored matchups and a list of the athletes for the times tab
    return varsity_results, jv_results, athletes_list

#function to score a matchup between two teams
def scorer(team_1, team_2, team_1_name, team_2_name):
    #intializes all needed dictionaries and sorts the runners from the matchup
    all_athletes = team_1 + team_2
    sorted_athletes = sorted(all_athletes, key=lambda x: int(x.place))
    team_1_score = {}
    team_1_rest = {}
    team_2_score = {}
    team_2_rest = {}
    new_place = 1

    #assigns new placement to the runner, using only the runners from the matchup
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

    #sums the new places to get each teams score
    team_1_total = sum(team_1_score.values())
    team_2_total = sum(team_2_score.values())

    #decides which teams wins based on the given scores
    if team_1_total < team_2_total:
        winner = team_1_name
    elif team_2_total < team_1_total:
        winner = team_2_name
    else:
        winner = "Tie"

    #formats the results of the athletes for easy display on the gui
    team_1_list = [f"{athlete} - {place}" for athlete, place in team_1_score.items()]
    team_2_list = [f"{athlete} - {place}" for athlete, place in team_2_score.items()]
    team_1_rest_list = [f"{athlete} - {place}" for athlete, place in team_1_rest.items()]
    team_2_rest_list = [f"{athlete} - {place}" for athlete, place in team_2_rest.items()]

    #returns all the needed results as a dictonary for easy access
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

# function to create all matchups and call the scorer
def compare_all_teams(teams):
    #intializes the dict for the results
    results = {}

    #loops through all the teams to create all possible matchup and return the scores
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

# function to create the sidebar
def create_sidebar(parent_frame, times_command=None, scoring_command=None, download_command=None):

    #sidebar frame
    sidebar = ctk.CTkFrame(
        parent_frame,
        width=100,
        height=900,
        corner_radius=15,
        fg_color="#992b2c"
    )
    sidebar.grid(row=0, column=0, rowspan=1, sticky="nsew", padx=(15, 0), pady=20)

    #load images 
    logo_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/logo.jpg"), size=(90, 110))
    clock_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/clock.png"), size=(45, 45))
    trophy_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/trophy.png"), size=(45, 50))
    download_img = ctk.CTkImage(Image.open("cl_topics_a/projects/xc_girls/download.png"), size=(55, 60))


    #logo on sidebar
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

    #times button on sidebar
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

    #scores button on sidebar
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

    #download button on sidebar
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

    #allows sidebar to expand vertically
    sidebar.grid_rowconfigure(4, weight=1)  
    
    #return the sidebar for use across different windows
    return sidebar

#function to create the dashboard view
def create_dashboard():
    #global the widgets from the import screen and the frame from this screen so we can tell what window we arey in
    global dashboard_frame, image_label, import_button

    #hide the import screen widgets
    image_label.grid_forget()
    import_button.grid_forget()

    #hide the times frame if it's visible
    if 'times_frame' in globals() and times_frame.winfo_exists():
        times_frame.grid_forget()

    #create dashboard_frame
    dashboard_frame = ctk.CTkFrame(app, fg_color="#A9A9A9")
    dashboard_frame.grid(row=0, column=0, sticky="nsew", columnspan=1, rowspan=1) 
    dashboard_frame.grid_columnconfigure(1, weight=1)  
    dashboard_frame.grid_rowconfigure(0, weight=1)

    # Create the sidebar using function
    sidebar = create_sidebar(
        dashboard_frame,
        times_command=show_times,
        download_command=download_results  
    )

    #main content area 
    results_area = ctk.CTkFrame(dashboard_frame, corner_radius=20, fg_color="#A9A9A9")
    results_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    results_area.grid_rowconfigure(0, weight=1)
    results_area.grid_rowconfigure(1, weight=1)
    results_area.grid_columnconfigure(0, weight=1)

    #upper frame for varsity results
    upper_box = ctk.CTkFrame(results_area, fg_color="#932b2c")
    upper_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
    upper_box.grid_rowconfigure(1, weight=1)
    upper_box.grid_columnconfigure(0, weight=1)

    #lower frame for jv results
    lower_box = ctk.CTkFrame(results_area, fg_color="#932b2c")
    lower_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
    lower_box.grid_rowconfigure(1, weight=1)
    lower_box.grid_columnconfigure(0, weight=1)

    #call display results for varsity and jv in the upper and lower boxes
    display_results(upper_box, varsity_results, "Varsity Results")
    display_results(lower_box, jv_results, "Junior Varsity Results")

#function to download results
def download_results():
    #prompt the user to select a file save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="save results as"
    )

    #open the file in write mode to write into csv
    with open(file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        #write headers
        writer.writerow([
            "Type",
            "Matchup",
            "Team 1 Name",
            "Team 1 Score",
            "Team 2 Name",
            "Team 2 Score",
            "Winner",
            "Runner Name",
            "Runner Team",
            "Runner New Place",
            "Runner Time"
        ])

        #function to write matchup and runners
        def write_results(results, category, list):
            for matchup, data in results.items():
                writer.writerow([
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])

                #write teams and scores
                writer.writerow([
                    category,
                    matchup,
                    data["Team 1 Name"],
                    data["Team 1 Score"],
                    data["Team 2 Name"],
                    data["Team 2 Score"],
                    data["Winner"],
                    "",
                    "",
                    "",
                    ""
                ])

                #write runners for team 1
                for athlete_info in data["Team 1 Results"]:
                    runner_name, runner_place = athlete_info.split(" - ")
                    athlete = next(a for a in athletes_list if a.name == runner_name and a.team == data["Team 1 Name"])
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        runner_name,
                        data["Team 1 Name"],
                        runner_place,
                        str(athlete.time) 
                    ])

                #write runners for team 2
                for athlete_info in data["Team 2 Results"]:
                    runner_name, runner_place = athlete_info.split(" - ")
                    athlete = next(a for a in athletes_list if a.name == runner_name and a.team == data["Team 2 Name"])
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        runner_name,
                        data["Team 2 Name"],
                        runner_place,
                        str(athlete.time) 
                    ])

                #write runners in rest for team 1
                for athlete_info in data.get("Team 1 Rest", []):
                    runner_name, runner_place = athlete_info.split(" - ")
                    athlete = next(a for a in athletes_list if a.name == runner_name and a.team == data["Team 1 Name"])
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        runner_name,
                        data["Team 1 Name"],
                        runner_place,
                        str(athlete.time)
                    ])

                #write runners in rest for team 2
                for athlete_info in data.get("Team 2 Rest", []):
                    runner_name, runner_place = athlete_info.split(" - ")
                    athlete = next(a for a in athletes_list if a.name == runner_name and a.team == data["Team 2 Name"])
                    writer.writerow([
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        runner_name,
                        data["Team 2 Name"],
                        runner_place,
                        str(athlete.time)
                    ])

        #call write varsity results
        write_results(varsity_results, "Varsity", athletes_list)

        #call write junior varsity results
        write_results(jv_results, "Junior Varsity", athletes_list)

#function to show the times view
def show_times():
    #global the times frame so we can tell what window it is in
    global times_frame

    #hide the dashboard frame if it's visible
    if 'dashboard_frame' in globals() and dashboard_frame.winfo_exists():
        dashboard_frame.grid_forget()

    #create the times frame
    times_frame = ctk.CTkFrame(app, fg_color="#A9A9A9")
    times_frame.grid(row=0, column=0, sticky="nsew", columnspan=1, rowspan=1)
    times_frame.grid_columnconfigure(1, weight=1)  
    times_frame.grid_rowconfigure(0, weight=1)

    #create sidebar fro funtion
    sidebar = create_sidebar(
        times_frame, 
        scoring_command=create_dashboard, 
        download_command=download_results  
    )

    #create main content area
    content_frame = ctk.CTkFrame(times_frame, fg_color="#A9A9A9")
    content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    #create a frame for the times 
    times_box = ctk.CTkFrame(content_frame, fg_color="#932b2c")
    times_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    times_box.grid_columnconfigure(0, weight=1)
    times_box.grid_rowconfigure(1, weight=1)

    #create the title label
    title_label = ctk.CTkLabel(times_box, text="Athlete Times", font=("Arial", 30, "bold"), text_color="white")
    title_label.grid(row=0, column=0, pady=10)

    #create a frame to hold the treeview
    tree_frame = ctk.CTkFrame(times_box, fg_color="#A9A9A9")
    tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    tree_frame.grid_columnconfigure(0, weight=1)
    tree_frame.grid_rowconfigure(0, weight=1)

    #create the treeview to display times
    tree_columns = ("Place", "Name", "Team", "Time")
    tree = ttk.Treeview(tree_frame, columns=tree_columns, show="headings")
    tree.grid(row=0, column=0, sticky='nsew')
    style = ttk.Style()
    style.configure("Treeview", background="white", foreground="black", fieldbackground="blue", rowheight=75, font=("Arial", 36))
    style.configure("Treeview.Heading", font=("Arial", 50, "bold"))
                    
    #define headings of tree view
    for col in tree_columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    #access athletes_list and sort athletes_list by place
    sorted_athletes = sorted(athletes_list, key=lambda x: int(x.place))

    #insert data into treeview
    for athlete in sorted_athletes:
        tree.insert("", "end", values=(athlete.place, athlete.name, athlete.team, str(athlete.time)))

    #add scrollbar to tree view
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

#function to display the results of each matchup
def display_results(frame, results, title):

    #create title label for varsity or junior varisty
    title_label = ctk.CTkLabel(
        frame, 
        text=title, 
        font=("Arial", 30, "bold"), 
        text_color="white"
    )
    title_label.grid(row=0, column=0, pady=10, sticky="nsew", padx=10)

    #create a frame for the scrollable area,
    scrollable_frame = ctk.CTkFrame(frame, fg_color="#A9A9A9")
    scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    scrollable_frame.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_rowconfigure(0, weight=1)

    #create a canvas in the scrollable frame 
    canvas = ctk.CTkCanvas(scrollable_frame, bg="#A9A9A9", highlightthickness=0)

    #create a scrollbar inside the scrollable frame and link it to the canvas's yview 
    scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)

    #allow the canvas to update the scrollbar position during scrolling
    canvas.configure(yscrollcommand=scrollbar.set)

    # create a frame inside the canvas to hold the scrollable content
    scrollable_content = ctk.CTkFrame(canvas, fg_color="#A9A9A9")

    #add the scrollable_content frame to the canvas
    scrollable_window = canvas.create_window((0, 0), window=scrollable_content, anchor="nw")

    #bind the <Configure> event of scrollable_content to update the scroll region when the content size changes
    scrollable_content.bind(
        "<Configure>",
        lambda x: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    #define a function to adjust the width of the scrollable_content frame to match the canvas width
    def on_canvas_configure(event):
        canvas.itemconfig(scrollable_window, width=event.width)

    #bind the <Configure> event of the canvas to call the function that adjusts the width of scrollable_content
    canvas.bind("<Configure>", on_canvas_configure)

    #pack the canvas to fill the left side of the scrollable frame
    canvas.pack(side="left", fill="both", expand=True)

    #pack the scrollbar on the right side of the scrollable frame
    scrollbar.pack(side="right", fill="y")

    #create frames to hold the matchups
    matchups_frame = ctk.CTkFrame(scrollable_content, fg_color="#A9A9A9")
    matchups_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    #calculate the number of teams using a set
    team_names = set()
    for data in results.values():
        team_names.add(data['Team 1 Name'])
        team_names.add(data['Team 2 Name'])
    number_of_teams = len(team_names)
    
    #calulate the number of columns based on the number of teams, matchups
    if number_of_teams <= 3:
        columns = int(number_of_teams * (number_of_teams - 1) / 2)
    else:
        columns = 3

    #make the columns evenly sizes 
    for col in range(columns):
        matchups_frame.grid_columnconfigure(col, weight=1, uniform="matchup")

    #variables to placement of matchup frames
    current_column = 0
    current_row = 0

    #for each matchup create a frame inside matchups_frame
    for matchup_key, data in results.items():
        matchup_frame = ctk.CTkFrame(matchups_frame, fg_color="#992b2c", corner_radius=10)
        matchup_frame.grid(row=current_row, column=current_column, padx=10, pady=10, sticky="nsew")
        matchup_frame.grid_rowconfigure(0, weight=1)
        matchup_frame.grid_columnconfigure(0, weight=1)

        #update column and row counters for placement
        current_column += 1
        if current_column >= columns:
            current_column = 0
            current_row += 1

        #add a title to each matchup frame
        teams_title = f"{data['Team 1 Name']} vs {data['Team 2 Name']}"
        teams_label = ctk.CTkLabel(
            matchup_frame, 
            text=teams_title, 
            font=("Arial", 22, "bold"), 
            text_color="white"
        )
        teams_label.grid(row=0, column=0, pady=5, sticky="nsew", padx=10)

        #columns frame to hold the results for each teams
        columns_frame = ctk.CTkFrame(matchup_frame, fg_color="#A9A9A9")
        columns_frame.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)

        #team 1 results frame
        team1_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team1_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        team1_frame.grid_columnconfigure(0, weight=1)

        #team 2 results frame 
        team2_frame = ctk.CTkFrame(columns_frame, fg_color="#ffffff")
        team2_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        team2_frame.grid_columnconfigure(0, weight=1)

        #team 1 label for results frame
        team1_label = ctk.CTkLabel(
            team1_frame, 
            text=data['Team 1 Name'], 
            font=("Arial", 14, "bold"), 
            anchor="center"
        )
        team1_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        
        #loops through atheletes in team 1 results to create labels for 1 to 5 runners
        for i, athlete_info in enumerate(data['Team 1 Results']):
            athlete_label = ctk.CTkLabel(
                team1_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i + 1, column=0, padx=5, pady=2, sticky="nsew")

        #separator for extra runners
        separator = ctk.CTkLabel(
            team1_frame, 
            text="--", 
            fg_color="#ffffff", 
            anchor="center", 
            width=100
        )
        separator.grid(row=6, column=0, padx=5, pady=2, sticky="nsew")

        #loops through atheletes in team 1 rest to create labels for 6 and 7 runners
        for i, athlete_info in enumerate(data['Team 1 Rest'], start=7):
            athlete_label = ctk.CTkLabel(
                team1_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i, column=0, padx=5, pady=2, sticky="nsew")

        #total score for team 1 at the bottom
        team1_total_label = ctk.CTkLabel(
            team1_frame, 
            text=f"Total: {data['Team 1 Score']}", 
            font=("Arial", 12, "bold"), 
            anchor="center"
        )
        team1_total_label.grid(row=9, column=0, pady=5, padx=5, sticky="nsew")

        #team 2 label for results frame
        team2_label = ctk.CTkLabel(
            team2_frame, 
            text=data['Team 2 Name'], 
            font=("Arial", 14, "bold"), 
            anchor="center"
        )
        team2_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        #loops through atheletes in team 2 results to create labels for 1 to 5 runners
        for i, athlete_info in enumerate(data['Team 2 Results']):
            athlete_label = ctk.CTkLabel(
                team2_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i + 1, column=0, padx=5, pady=2, sticky="nsew")

        #seperator for extra runners
        separator = ctk.CTkLabel(
            team2_frame, 
            text="--", 
            fg_color="#ffffff", 
            anchor="center", 
            width=100
        )
        separator.grid(row=6, column=0, padx=5, pady=2, sticky="nsew")

        #loops through atheletes in team 2 rest to create labels for 6 and 7 runners
        for i, athlete_info in enumerate(data['Team 2 Rest'], start=7):
            athlete_label = ctk.CTkLabel(
                team2_frame, 
                text=f"{athlete_info}", 
                fg_color="#ffffff", 
                anchor="center", 
                width=100
            )
            athlete_label.grid(row=i, column=0, padx=5, pady=2, sticky="nsew")

        #total score for team 2 at the bottom
        team2_total_label = ctk.CTkLabel(
            team2_frame, 
            text=f"Total: {data['Team 2 Score']}", 
            font=("Arial", 12, "bold"), 
            anchor="center"
        )
        team2_total_label.grid(row=9, column=0, pady=5, padx=5, sticky="nsew")

        #winner of team 1 vs team 2 label
        winner_label = ctk.CTkLabel(
            matchup_frame, 
            text=f"Winner: {data['Winner']}", 
            font=("Arial", 16, "bold"), 
            text_color="white", 
            anchor="center"
        )
        winner_label.grid(row=2, column=0, pady=5, sticky="nsew", padx=10)

#create the main window
app = ctk.CTk()
app.title("Cross Country Scorer Application")
app.geometry("1500x920")

#set the appearance mode and color theme
ctk.set_appearance_mode("light")
app.configure(fg_color="#A9A9A9")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)

#load the main image for import screen 
image_path = "cl_topics_a/projects/xc_girls/xc.png"
image = ctk.CTkImage(Image.open(image_path), size=(585, 640))

#create a label for the image to display it
image_label = ctk.CTkLabel(app, image=image, text="")
image_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nsew")

#create the "Import Race Results" button
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
