import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import threading
import requests
import os
import time
from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect, jsonify

app = Flask(__name__)
app.secret_key = "Felix.com"

lock = threading.Lock()

class Window(tk.Tk):
    def create_navigation_bar(self):
        navigation_frame = tk.Frame(self, bg="lightgray")
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y)

        buttons = [
            ("Team", self.show_Team_frame),
            ("Players", self.show_player_frame),
            ("SPIEL", self.show_SPIEL_frame),
            #("Contact", self.show_contact_frame),
        ]

        button_width = 10  # Set a fixed width for all buttons

        for text, command in buttons:
            button = tk.Button(navigation_frame, text=text, command=command, width=button_width, pady=5, font=("Helvetica", 14))
            button.pack(side=tk.TOP, anchor=tk.W)
            
            
    def __init__(self, start_server=True):
        super().__init__()
        self.name_entries = []
        self.label_list = []
        self.updated_data = {}
        self.variable_dict = {}
        self.team_button_list = []
        self.spiel_buttons = {}
        self.teams_playing = [None, None]

        # Set window title
        self.title("Football Tournament Manager")
        self.state('zoomed')

        menu = tk.Menu(self)
        self.config(menu=menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label="Manager", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.quit)

        # Create and pack the navigation bar
        self.create_navigation_bar()

        # Create frames for different sets of elements
        self.Team_frame = tk.Frame(self, bg="lightblue")
        self.player_frame = tk.Frame(self, bg="lightgreen")
        self.SPIEL_frame = tk.Frame(self, bg="lightcoral")
        #self.contact_frame = tk.Frame(self, bg="lightyellow")

        # Create elements for each frame
        self.create_Team_elements()
        self.create_player_elements()
        self.create_SPIEL_elements()
        #self.create_contact_elements()

        # Display the default frame
        self.show_frame(self.Team_frame)
        
        
        if start_server:
            server_thread = threading.Thread(target=self.start_server)
            server_thread.start()
        
    def start_server(self):
        app.run(debug=False, threaded=True, port=5000, host="0.0.0.0", use_reloader=False)
        

            
            
##############################################################################################
    def add_name_entry(self, entry_text=""):
        count = len(self.name_entries) + 1

        # Create a label with "Team 1" and the count
        label_text = f'Team {count}'
        label = tk.Label(self.frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.name_entries), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = tk.Entry(self.frame, font=("Helvetica", 14))  # Increase font size
        
        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)

        new_entry.grid(row=len(self.name_entries), column=1, pady=5, sticky='we')
        self.name_entries.append(new_entry)
        self.label_list.append(label)

    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def reload_button_command(self):
        # Delete all entry fields
        for entry in self.name_entries:
            entry.destroy()
        self.name_entries = []
        
        for label in self.label_list:
            label.destroy()
        
        # Read the names from the file and put them into the entry fields
        self.write_names_into_entry_fields()
        
    def save_names(self):
        with open("data/team_names.txt", "w+") as f:
            for entry in self.name_entries:
                if entry != "" and entry != "\n":
                    f.write(entry.get() + " - 0\n")
        self.updated_data.update({"Teams": self.read_team_names()})

                
    def read_team_names(self, teams_to_read="all", read_score_from_team=False):
        with open("data/team_names.txt", "r") as f:
            self.name_entries_read = []
            scores = []
            if teams_to_read == "all":
                for line in f:
                    line, score = line.split(" - ", 1)
                    self.name_entries_read.append(line.replace("\n", ""))
                    scores.append(score.replace("\n", ""))
            else:
                print(teams_to_read)
                for line_number_to_read in teams_to_read:
                    # Subtract 1 since enumerate starts counting from 1 and list indices start from 0
                    if line_number_to_read != None:
                        index = line_number_to_read - 1

                        # Read the line at the specified index
                        f.seek(0)  # Move the file pointer to the beginning of the file
                        for i2, line in enumerate(f, start=0):
                            if i2 == line_number_to_read:
                                line, score = line.split(" - ", 1)
                                scores.append(score.replace("\n", ""))
                                self.name_entries_read.append(line.replace("\n", ""))
                                break  # Stop reading once the line is found

        if read_score_from_team:
            return self.name_entries_read, scores                
        
        return self.name_entries_read
    
    def write_names_into_entry_fields(self):
        try:
            with open("data/team_names.txt", "r") as f:
                # if the file is empty, do nothing
                if os.stat("data/team_names.txt").st_size == 0:
                    self.add_name_entry()

                
                # if the file is not empty, read the names from the file and put them into the entry fields
                else:
                    for line in f:
                        if line != "\n" and line != "":
                            self.add_name_entry(line.replace("\n", ""))
                    return False
        except FileNotFoundError:
            print("File not found")
            self.add_name_entry()
            return True


    def create_Team_elements(self):
        
        # Create elements for the Team frame
        canvas = tk.Canvas(self.Team_frame, bg="lightblue")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ttk.Scrollbar(self.Team_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frame = tk.Frame(canvas, bg="lightblue")
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        name_entries = []
        self.write_names_into_entry_fields()

        self.frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        # Button to add a new name entry
        add_button = tk.Button(self.Team_frame, text="Add Name", command=self.add_name_entry, font=("Helvetica", 14))
        add_button.pack(pady=10)

        # Button to retrieve the entered names


        submit_button = tk.Button(self.Team_frame, text="Submit", command=self.save_names, font=("Helvetica", 14))
        submit_button.pack(pady=10)

        
        reload_button = tk.Button(self.Team_frame, text="Reload", command=self.reload_button_command, font=("Helvetica", 14))
        reload_button.pack(pady=10)
        

        

##############################################################################################

##############################################################################################

    def create_player_elements(self):
        # Create elements for the player frame
        #player_button = tk.Button(self.player_frame, text="player Button", command=self.player_button_command)
        #player_button.pack(pady=10)
        # Create elements for the Team frame
        canvas = tk.Canvas(self.player_frame, bg="lightgreen")
        canvas.pack( fill="both", expand=True, side="bottom")
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ttk.Scrollbar(self.player_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frameplayer = tk.Frame(canvas, bg="lightgreen")
        canvas.create_window((0, 0), window=self.frameplayer, anchor="nw")
        
        
        # Button to add a new name entry
        add_button = tk.Button(self.player_frame, text="Add Name", command=lambda: self.add_name_entry_player(self.frameplayer, "Player"), font=("Helvetica", 14))
        add_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    

        # Button to retrieve the entered names


        submit_button = tk.Button(self.player_frame, text="Submit", command=self.save_names_player, font=("Helvetica", 14))
        submit_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    

        
        reload_button = tk.Button(self.player_frame, text="Reload", command=self.reload_button_player_command, font=("Helvetica", 14))
        reload_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    
        
        self.selected_team = ""
        self.team_button_list = []
        
        teams_list = self.read_teams_from_file('data/team_names.txt')
        
        for i, team_name in enumerate(teams_list):
            team_button = tk.Button(
                self.player_frame,
                text=team_name,
                command=lambda name=team_name, i2=i: self.select_team(name, self.team_button_list, i2)
            )
            team_button.pack(pady=5, padx=5, anchor=tk.NW, side=tk.LEFT)
            self.team_button_list.append(team_button)
            team_button.config(bg="lightgray")
        
        
    def save_names_player(self, team_name=""):
        entries = self.variable_dict.get(f"entries{self.frameplayer}")
        entries2 = self.variable_dict.get(f"entries2{self.frameplayer}")
        entries3 = self.variable_dict.get(f"entries3{self.frameplayer}")
        
        if team_name == "":
            team_name = self.selected_team
        
        if entries:
            
            
            with open(f"data/{team_name}.txt", "w+") as f:
                for i, (entry, entrie2, entrie3) in enumerate(zip(entries, entries2, entries3)):
                    # Check if the entry widget exists
                    if entry.winfo_exists():
                        entry_text = str(entry.get())
                        entry_text2 = str(entrie2.get())
                        entry_text3 = str(entrie3.get())
                        if entry_text and entry_text != "\n":
                            combined_entry_text = f"{entry_text.replace(' - ',' ')} - {entry_text2.replace(' - ',' ')} - {entry_text3.replace(' - ',' ')}"
                            if combined_entry_text and combined_entry_text != "\n":
                                
                                f.write(combined_entry_text + "\n")

        ###self.updated_data.update({"Players": {self.selected_team: self.read_team_names_player(self.selected_team)}})
            
    
    def add_name_entry_player(self, Frame, Counter, entry_text="", entry_text2="", entry_text3=""):
        varcountname = f"count{Frame}"
        varentrie1name = f"entries{Frame}"
        varentrie2name = f"entries2{Frame}"
        varentrie3name = f"entries3{Frame}"
        varlabelname = f"label{Frame}"

        # Check if the variable already exists in the dictionary
        if varcountname not in self.variable_dict:
            self.variable_dict[varcountname] = 0  # Initialize count to 0

        if varentrie1name not in self.variable_dict:
            self.variable_dict[varentrie1name] = []
            
        if varentrie2name not in self.variable_dict:
            self.variable_dict[varentrie2name] = []

        if varentrie3name not in self.variable_dict:
            self.variable_dict[varentrie3name] = []
        
        if varlabelname not in self.variable_dict:
            self.variable_dict[varlabelname] = []

        # Now you can access the count using the dynamic variable name
        count = self.variable_dict[varcountname] + 1

        # Update the count in the dictionary
        self.variable_dict[varcountname] = count

        # Create a label with "Team 1" and the count
        label_text = f'{Counter} {count}'
        label = tk.Label(Frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.variable_dict[varentrie1name]), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = tk.Entry(Frame, font=("Helvetica", 14))  # Increase font size
        
        new_entry2 = tk.Entry(Frame, font=("Helvetica", 14))  # Increase font size
        
        new_entry3 = tk.Entry(Frame, font=("Helvetica", 14))  # Increase font size
        #print("entry_text", entry_text)
        #print("new_entry")

        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)
            
        if entry_text2:
            new_entry2.insert(0, entry_text2)
            
        if entry_text3:
            new_entry3.insert(0, entry_text3)
        else:
            new_entry3.insert(0, "0")
        
        

        new_entry.grid(row=len(self.variable_dict[varentrie1name]), column=1, pady=5, sticky='we')
        new_entry2.grid(row=len(self.variable_dict[varentrie1name]), column=2, pady=5, sticky='we')
        new_entry3.grid(row=len(self.variable_dict[varentrie1name]), column=3, pady=5, sticky='we')
        self.variable_dict[varentrie1name].append(new_entry)
        self.variable_dict[varentrie2name].append(new_entry2)
        self.variable_dict[varentrie3name].append(new_entry3)
        self.variable_dict[varlabelname].append(label)

    
    
    def write_names_into_entry_fields_players(self, txt_file, Counter, Frame):
        try:
            # Read player names using read_player_names function
            player_names, player_ids, scores = self.read_player_names(txt_file)

            # if the file is empty or no names are read, add an empty entry
            if not player_names:
                self.add_name_entry_player(Frame, Counter)
            else:
                # if names are read, put them into the entry fields
                for player_name, player_id, score in zip(player_names, player_ids, scores):
                    self.add_name_entry_player(Frame, Counter, player_name, player_id, score)

            return False

        except FileNotFoundError:
            
            with open(f"data/{txt_file}.txt", "w+") as f:
                f.write("")
            
            self.add_name_entry_player(Frame, Counter)
            
            return True


    
    def reload_button_player_command(self):
        
        for button in self.team_button_list:
            button.destroy()
        
        self.selected_team = ""
        self.team_button_list = []
        
        teams_list = self.read_teams_from_file('data/team_names.txt')
        
        for i, team_name in enumerate(teams_list):
            team_button = tk.Button(
                self.player_frame,
                text=team_name,
                command=lambda name=team_name, i2=i: self.select_team(name, self.team_button_list, i2)
            )
            team_button.pack(pady=5, padx=5, anchor=tk.NW, side=tk.LEFT)
            self.team_button_list.append(team_button)
            team_button.config(bg="lightgray")
    
        
        varcountname = f"count{str(self.frameplayer)}"
        varentrie1name = f"entries{str(self.frameplayer)}"
        varentrie2name = f"entries2{str(self.frameplayer)}"
        varentrie3name = f"entries3{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentrie1name):
            # Access the value associated with the key
            if self.variable_dict[varentrie1name] != []:
                for entry in self.variable_dict[varentrie1name]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
                
                for entry in self.variable_dict[varentrie2name]:
                    entry.destroy()
                    
                for entry in self.variable_dict[varentrie3name]:
                    entry.destroy()
    
        
        
        self.variable_dict[varcountname] = 0
    
    
    def select_team(self, team_name, team_button_list, index):
        
        for button in team_button_list:
            button.config(bg="lightgray")
        
        team_button = team_button_list[index]
        
        team_button.config(bg="red")
        
        varcountname = f"count{str(self.frameplayer)}"
        varentrie1name = f"entries{str(self.frameplayer)}"
        varentrie2name = f"entries2{str(self.frameplayer)}"
        varentrie3name = f"entries3{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentrie1name):
            # Access the value associated with the key
            if self.variable_dict[varentrie1name] != []:
                for entry in self.variable_dict[varentrie1name]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
                
                for entry in self.variable_dict[varentrie2name]:
                    entry.destroy()
                
                for entry in self.variable_dict[varentrie3name]:
                    entry.destroy()
        
        self.selected_team = team_name
        
        self.variable_dict[varcountname] = 0
        
        self.write_names_into_entry_fields_players(team_name, "Player", self.frameplayer)
          
            
    def read_player_names(self, team_name):
        with open(f"data/{team_name}.txt", "r") as f:
            self.name_entries_read = []
            player_id_list = []
            scores = []
            for line in f:
                player_name, player_id, score = line.split(" - ", 2)
                self.name_entries_read.append(player_name.replace("\n", ""))
                player_id_list.append(player_id.replace("\n", ""))
                scores.append(score.replace("\n", ""))
        return self.name_entries_read, player_id_list, scores
    
    
    def read_teams_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                teams = [line.strip() for line in file.readlines() if line.strip()]
            return teams
        except FileNotFoundError:
            print("File not found")
            return []

##############################################################################################

##############################################################################################

    def create_SPIEL_elements(self):
        # Create elements for the SPIEL frame
        
        manual_frame = tk.Frame(self.SPIEL_frame, bg="lightcoral")
        manual_frame.pack(pady=5, anchor=tk.S, side=tk.BOTTOM, padx=5, fill=tk.X)
        
        manual_manual_frame = tk.Frame(manual_frame, bg="lightcoral")
        manual_manual_frame.pack(pady=0, anchor=tk.SE, side=tk.RIGHT, padx=0)
        
        SPIEL_button = tk.Button(manual_manual_frame, text="Reload", command=lambda : self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements), font=("Helvetica", 14))
        SPIEL_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.S) 
        
        
        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}


        # Inside your loop
        for team in self.read_team_names(self.teams_playing):
            #print(team)
            
            # Initialize the dictionary for the current team
            self.spiel_buttons[team] = {}

            try:
                with open(f"data/{team}.txt", "r") as f:
                    
                    self.for_team_frame = tk.Frame(self.SPIEL_frame, background="lightblue")
                    self.for_team_frame.pack(pady=10, anchor=tk.NW, side=tk.TOP, fill="both", padx=10, expand=True)
                    
                    # Create global scores buttons, one for up and one for down
                    score_button_frame = tk.Frame(self.for_team_frame, background="lightblue")
                    score_button_frame.pack(pady=10, anchor=tk.E, side=tk.RIGHT, padx=10)
                    
                    score_button_up = tk.Button(score_button_frame, text="UP", command=lambda team=team: self.global_scored_a_point(team, "UP"), font=("Helvetica", 22))
                    score_button_up.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
                    
                    score_label = tk.Label(score_button_frame, text="45", font=("Helvetica", 22))
                    score_label.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
                    
                    score_button_down = tk.Button(score_button_frame, text="DOWN", command=lambda team=team: self.global_scored_a_point(team, "DOWN"), font=("Helvetica", 22))
                    score_button_down.pack(pady=2, anchor=tk.N, side=tk.BOTTOM, expand=True, fill=tk.X)
                    
                    self.team_label = tk.Label(self.for_team_frame, text=team, font=("Helvetica", 18))
                    self.team_label.pack(side=tk.LEFT, pady=2, anchor=tk.NW)
                    
                    self.spiel_buttons[team]["global"] = (self.for_team_frame, self.team_label)
                    
                    frame_frame = tk.Frame(self.for_team_frame, background="lightblue")
                    frame_frame.pack(side=tk.TOP, pady=0, anchor=tk.N)

                    up_frame = tk.Frame(frame_frame, background="lightblue")
                    up_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

                    down_frame = tk.Frame(frame_frame, background="lightblue")
                    down_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
                    
                    for i, line in enumerate(f):
                        
                        if i < 8:
                            self.group_frame = tk.Frame(up_frame, background="lightblue")
                            self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
                        else:
                            self.group_frame = tk.Frame(down_frame, background="lightblue")
                            self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
                        
                        #self.group_frame = tk.Frame(self.for_team_frame, background="lightcoral")
                        #self.group_frame.pack(side=tk.LEFT, padx=10, pady=10)

                        playertext1 = tk.Label(self.group_frame, text=f"Player {i}", font=("Helvetica", 14))
                        playertext1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                        
                        player_name, player_id, score = line.split(" - ", 2)
                        score = score.replace("\n", "")
                        playertext2_text = f"{player_name} - {player_id}"
                        
                        playertext2 = tk.Label(self.group_frame, text=playertext2_text , font=("Helvetica", 14))
                        playertext2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                        
                        playertext3 = tk.Label(self.group_frame, text=f"Tore {str(score)}", font=("Helvetica", 14))
                        playertext3.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)

                        playerbutton1 = tk.Button(self.group_frame, text="UP", command=lambda team=team, player_index=i: self.player_scored_a_point(team, player_index, "UP"), font=("Helvetica", 14))
                        playerbutton1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                        
                        playerbutton2 = tk.Button(self.group_frame, text="DOWN", command=lambda team=team, player_index=i: self.player_scored_a_point(team, player_index, "DOWN"), font=("Helvetica", 14))
                        playerbutton2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                        
                        
                        #print("team", team, "i", i)

                        # Save the group_frame, playertext1, and playerbutton in each for loop with the team name as key
                        self.spiel_buttons[team][i] = (self.group_frame, playertext1, playertext2, playertext3, playerbutton1, playerbutton2)  # Use append for a list
                        
                        #self.spiel_buttons[team] = (playerbutton)  # Use append for a list

            except FileNotFoundError:
                with open(f"data/{team}.txt", "w+") as f:
                    f.write("")

        
        self.manual_team_select_1 = ttk.Combobox(manual_manual_frame, values=self.read_team_names(), font=("Helvetica", 14))
        self.manual_team_select_1.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        self.manual_team_select_1.bind("<<ComboboxSelected>>", lambda event, nr=1: self.on_team_select(event, nr))
        
        
        self.manual_team_select_2 = ttk.Combobox(manual_manual_frame, values=self.read_team_names(), font=("Helvetica", 14))
        self.manual_team_select_2.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        self.manual_team_select_2.bind("<<ComboboxSelected>>", lambda event, nr=0: self.on_team_select(event, nr))


        self.create_matches_labels(manual_frame)


        if self.teams_playing.count(None) == 0:
            #print(self.teams_playing)
            self.manual_team_select_1.set(self.read_team_names()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_team_names()[self.teams_playing[0]])
            
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.state(["disabled"])
        
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.state(["!disabled"])
            #print(self.teams_playing)
            self.manual_team_select_2.set(self.read_team_names()[self.teams_playing[0]])        

    def on_team_select(self, event, nr):
        selected_team = event.widget.get()
        
        # Convert the value to the team index
        team_index = self.read_team_names().index(selected_team)

        # Ensure self.teams_playing has enough elements
        while len(self.teams_playing) <= nr:
            self.teams_playing.append(None)

        # Assign the team index to the specified position
        self.teams_playing[nr] = team_index
        
        
        if self.teams_playing.count(None) == 0:
            self.manual_team_select_1.set(self.read_team_names()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_team_names()[self.teams_playing[0]])
        
        #print(self.teams_playing)
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.state(["!disabled"])
            print(self.teams_playing)
            self.manual_team_select_2.set(self.read_team_names()[self.teams_playing[0]])
            
        
        
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.state(["disabled"])
            
        
        
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)

        
    def delete_all_in_frame(self, frame):
        if frame.winfo_exists():
            for widget in frame.winfo_children():
                if widget.winfo_class() == 'Frame':
                    # Recursively delete widgets in nested frames
                    widget.grid_forget()
                    widget.pack_forget()
                    self.delete_all_in_frame(widget)
                    widget.destroy()
                else:
                    widget.destroy()

            # Update the layout
            frame.update_idletasks()
            frame.update()

    
    def reload_button_command_common(self, frame, create_function_name):
        # Delete all entry fields
        self.delete_all_in_frame(frame)
        
        # Read the names from the file and put them into the entry fields
        self.create_function_name = create_function_name
        
        self.create_function_name()
        

    def player_scored_a_point(self, team, player_index, direction="UP"):
        # Get the current score
        current_score = int(self.read_specific_player_stats(team, player_index, "score"))
        # Update the score
        if direction == "UP":
            current_score += 1
        else:
            current_score -= 1
        # Update the score label
        self.spiel_buttons[team][player_index][3].config(text=f"Tore {current_score}")
        
        with open(f"data/{team}.txt", "r") as f:
            # read the line with the index of the player
            lines = f.readlines()
            line = lines[player_index]
            # split the line into player name and score
            player_name, player_id, _ = line.split(" - ", 2)
            
        with open(f"data/{team}.txt", "w") as f:
            # write the line with the index of the player
            lines[player_index] = f"{player_name} - {player_id} - {current_score}\n"
            f.writelines(lines)
        
        ###self.updated_data.update({"SPIEL": {team: self.read_team_names_player(team)}})
    
    
    def read_specific_player_stats(self, team_name, player_index, stat):
        with open(f"data/{team_name}.txt", "r") as f:
            # read the line with the index of the player
            lines = f.readlines()
            line = lines[player_index]
            # split the line into player name and score
            player_name, player_id, score = line.split(" - ", 2)
            if stat == "name":
                return player_name
            elif stat == "id":
                return player_id
            elif stat == "score":
                return score
            else:
                return 0
    
    
    def create_matches_labels(self, frame):
        matches = self.calculate_matches()
        
        spiel_select_frame = tk.Frame(frame, bg="lightcoral")
        spiel_select_frame.pack(pady=10, padx=10, anchor=tk.SW, side=tk.LEFT)
        
        spiel_select = ttk.Combobox(spiel_select_frame, font=("Helvetica", 14), width=35)
        spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N)

        spiel_select.bind("<<ComboboxSelected>>", lambda event: self.on_match_select(event, matches))
    
        # Initialize the values as an empty list
        values_list = []

        for match in matches:
            # Append each match label to the values list
            values_list.append(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])

        # Set the values of the Combobox after the loop
        spiel_select["values"] = values_list
        
        # get the index of the match that is currently being played and set the Combobox value to that match without using self.match_count - 1
        
        for match in matches:
            match_teams_indexes = [self.read_team_names().index(match_team) for match_team in match["teams"]]
            if match_teams_indexes == self.teams_playing or match_teams_indexes[::-1] == self.teams_playing:
                se = match["number"]
                #print("got it")
                break
            #print(match["teams"], self.teams_playing, match["number"], match_teams_indexes, match_teams_indexes[::-1])
        else:
            if self.teams_playing.count(None) == 0:
                values_list = []
                values_list.append("No Match found")
                spiel_select["values"] = values_list
                spiel_select.set(values_list[0])
                print("no match found")
                return
        
        if self.teams_playing.count(None) == 0:
            
            se = int(se.replace("Spiel ", "")) - 1
            current_match_index = se
            spiel_select.set(values_list[current_match_index])
            
            
        
        next_match_button = tk.Button(spiel_select_frame, text="Next Match", command=lambda : self.next_previous_match_button(spiel_select, matches), font=("Helvetica", 14))
        next_match_button.pack(pady=10, padx=5, side=tk.LEFT, anchor=tk.SW)
        
        previous_match_button = tk.Button(spiel_select_frame, text="Previous Match", command=lambda : self.next_previous_match_button(spiel_select, matches, False), font=("Helvetica", 14))
        previous_match_button.pack(pady=10, padx=5, side=tk.RIGHT, anchor=tk.SE)


    def on_match_select(self, event, matches):
        selected_match = event.widget.get()
        #print(selected_match)
        #print(matches)
        # Convert the value to the match index
        match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(selected_match)

        # Get the teams playing in the selected match and if there are none, set teams_playing to None
        team_names = self.read_team_names()
        
        self.teams_playing = [team_names.index(matches[match_index]["teams"][0]), team_names.index(matches[match_index]["teams"][1])] if [team_names.index(matches[match_index]["teams"][0]), team_names.index(matches[match_index]["teams"][1])] else [None, None]
        # Update the buttons
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)
        print("match selected")
        
    
    def next_previous_match_button(self, spiel_select, matches, next_match=True):
        
        # Get the current match index
        match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(spiel_select.get())
        
        
        
        if next_match:
            match_index += 1
        else:
            match_index -= 1

        # Get the teams playing in the selected match
        team_names = self.read_team_names()
        print(matches[match_index]["teams"][0], matches[match_index]["teams"][1], team_names)
        self.teams_playing = [team_names.index(matches[match_index]["teams"][0]), team_names.index(matches[match_index]["teams"][1])] if [team_names.index(matches[match_index]["teams"][0]), team_names.index(matches[match_index]["teams"][1])] else [None, None]
        
        # Update the buttons
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)


    def global_scored_a_point(self, team, direction="UP"):
        # Get the current score
        current_score = int(self.read_team_stats(team, "score"))
        # Update the score
        if direction == "UP":
            current_score += 1
        else:
            current_score -= 1
            
        self.write_score_for_team_into_file(team, current_score)
    

        # Update the score label
        self.spiel_buttons[team]["global"][1].config(text=team + " " + str(current_score))
        
    def write_score_for_team_into_file(self, team_name, score):
        with open(f"data/team_names.txt", "r") as f:
            # read the line with the index of the player
            lines = f.readlines()
            line = lines[team_name]
            line = line.replace("\n", "")
            line, _ = line.split(" - ", 1)
            # split the line into player name and score
            line = f"{line} - {score}\n"
        
        with open(f"data/team_names.txt", "w") as f:
            # write the line with the index of the player
            lines[team_name] = line
            f.writelines(lines)
            
    
    def read_team_stats(self, team_name, stat):
        score = self.read_team_names(self.teams_playing, True)
        score = score[score.index(team_name)]
        if stat == "score":
            return score
        
    

##############################################################################################

##############################################################################################

    #def create_contact_elements(self):
        # Create elements for the Contact frame
        #contact_button = tk.Button(self.contact_frame, text="Contact Button", command=self.contact_button_command)
        #contact_button.pack(pady=10)
        

##############################################################################################

    def show_frame(self, frame):
        # Hide all frames and pack the selected frame
        for frm in [self.Team_frame, self.player_frame, self.SPIEL_frame]: # self.contact_frame
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def show_Team_frame(self):
        self.reload_button_command()
        self.show_frame(self.Team_frame)

    def show_player_frame(self):
        self.reload_button_player_command()
        self.show_frame(self.player_frame)

    def show_SPIEL_frame(self):
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)
        print(stored_data)
        self.writeInMatches()
        self.show_frame(self.SPIEL_frame)

    #def show_contact_frame(self):
        #self.show_frame(self.contact_frame)

    # Button command functions

    #def player_button_command(self):
        #print("player Button Clicked")

    #def SPIEL_button_command(self):
        #print("SPIEL Button Clicked")

    #def contact_button_command(self):
        #print("Contact Button Clicked")
        
    ##############################################################################################
            
    def test(self):
        print("test")
        
    def delete_updated_data(self):
        #print("delete")
        #print(self.updated_data)
        self.updated_data = {}
        
    def writeInMatches(self):
        self.matches = matchData

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

def get_initial_data(template_name):
    global initial_data
    tkapp.test()
    initial_data = {
        "Teams": tkapp.read_team_names(),
        "Tore": [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "ZeitIntervall": 10,
        "Startzeit": [9,30],
        "LastUpdate": 0
    }
    return make_response(render_template(template_name, initial_data=initial_data))

@app.route("/")
def index():
    return get_initial_data("websitegroup.html")

@app.route("/tree")
def tree_index():
    return get_initial_data("websitetree.html")

@app.route("/plan")
def plan_index():
    return get_initial_data("websiteplan.html")

@app.route("/tv")
def tv_index():
    return get_initial_data("websitetv.html")


@app.route('/update_data')
def update_data():
    
    timeatstart = time.time()
    
    last_data_update = request.headers.get('Last-Data-Update', 0)
    #print(last_data_update)
    
    updated_data = tkapp.updated_data
    
    
    if updated_data != {}:
        
        #print(updated_data)  
        #print(updated_data.keys())
        #print(updated_data.values())
        for key, value in updated_data.items():
            for key2, value2 in stored_data.items():
                if key in value2.keys():
                    stored_data.pop(key2)
                    break
            
            stored_data.update({time.time()+2:{key:value}})
            print(stored_data)
        
        updated_data.update({"LastUpdate": timeatstart})
        
    for key, value in stored_data.items():
        #print("magucken")
        if key >= float(last_data_update):
            #print("key", key, "value", value, "last_data_update", last_data_update, "should be updated")
            updated_data.update(value)
            #print("updated_data", updated_data)
            
    
    #print("stored_data", stored_data, "updated_data", updated_data, "last_data_update", last_data_update)
        
    #print(updated_data)
    tkapp.delete_updated_data()
    #updated_data = {'Teams': tkapp.read_team_names(), 'Players': {"Player1":"Erik Van Doof","Player2":"Felix Schweigmann"}}  # You can modify this data as needed
    return jsonify(updated_data)


@app.route('/senddata', methods=['POST'])
def receive_data():
    global matchData
    
    matchData = request.json  # Assuming the data is sent in JSON format
    # Process the received data as needed
    print("Received match data")

    # Send a response back to the client
    response_data = {"message": "Data received successfully"}
    return jsonify(response_data)


global tkapp
global server_thread
global stored_data
global initial_data


stored_data = {}
tkapp = Window(True)

if __name__ == "__main__":
    
    
    tkapp.mainloop()
    