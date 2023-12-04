import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import threading
import requests
import os
import time
from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect, jsonify
import sqlite3
import vlc

app = Flask(__name__)
app.secret_key = "Felix.com"

lock = threading.Lock()

class Window(ctk.CTk):
    def create_navigation_bar(self):
        navigation_frame = ctk.CTkFrame(self)
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y)

        buttons = [
            ("Team", self.show_Team_frame),
            ("Players", self.show_player_frame),
            ("SPIEL", self.show_SPIEL_frame),
            #("Contact", self.show_contact_frame),
        ]

        button_width = 10  # Set a fixed width for all buttons

        for text, command in buttons:
            button = ctk.CTkButton(navigation_frame, text=text, command=command, width=button_width)
            button.pack(side=tk.TOP, anchor=tk.W, pady=5)
            
            
    def __init__(self, start_server):
        super().__init__()
        self.name_entries = []
        self.label_list = []
        self.file_dialog_list = []
        self.mp3_list = {}
        self.updated_data = {}
        self.variable_dict = {}
        self.team_button_list = []
        self.spiel_buttons = {}
        self.teams_playing = [None, None]

        # Set window title
        self.title("Football Tournament Manager")
        self.after(0, lambda:self.state('zoomed'))
        try:
            icon_path = os.path.join('..', 'icon.ico')
            self.iconbitmap(icon_path)
        except:
            icon_path = os.path.join('icon.ico')
            self.iconbitmap(icon_path)
        
        self.tk_setPalette(background='grey17', foreground='grey17',
               activeBackground='grey17', activeForeground='grey17')
        
        ctk.set_appearance_mode("dark")
        
        self.init_sqlite_db()
        
        self.media_player_instance = vlc.Instance()
        self.media_player_instance.log_unset()
        
        #menu = tk.Menu(self)
        #self.configure(menu=menu)
        #filemenu = tk.Menu(menu)
        #menu.add_cascade(label="Manager", menu=filemenu)
        #filemenu.add_command(label="Exit", command=self.quit)

        # Create and pack the navigation bar
        self.create_navigation_bar()

        # Create frames for different sets of elements
        self.Team_frame = ctk.CTkFrame(self)
        self.player_frame = ctk.CTkFrame(self, height=10)
        self.SPIEL_frame = ctk.CTkFrame(self)
        #self.contact_frame = ctk.CTkFrame(self, bg="lightyellow")

        # Create elements for each frame
        self.create_Team_elements()
        self.create_player_elements()
        self.create_SPIEL_elements()
        #self.create_contact_elements()

        # Display the default frame
        self.show_frame(self.Team_frame)
        
        #print("finished init")
        
        
        if start_server:
            server_thread = threading.Thread(target=self.start_server)
            server_thread.start()
    
        
    def start_server(self):
        app.run(debug=False, threaded=True, port=5000, host="0.0.0.0", use_reloader=False)
    
    
    def init_sqlite_db(self):
        self.db_path = "data/data.db"
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        teamDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS teamData (
            id INTEGER PRIMARY KEY,
            teamName TEXT UNIQUE,
            goals INTEGER DEFAULT 0,
            goalsReceived INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            mp3Path TEXT DEFAULT "",
            groupNumber INTEGER
        )
        """
        self.cursor.execute(teamDataTableCreationQuery)
        self.connection.commit()
        
        playerDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerData (
            id INTEGER PRIMARY KEY,
            playerName TEXT UNIQUE,
            playerNumber INTEGER,
            teamId INTEGER REFERENCES teamData(id) DEFAULT 0,
            goals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerDataTableCreationQuery)
        self.connection.commit()
        
        matchDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS matchData (
            matchId INTEGER PRIMARY KEY,
            groupNumber INTEGER,
            team1Id INTEGER REFERENCES teamData(id),
            team2Id INTEGER REFERENCES teamData(id),
            team1Goals INTEGER DEFAULT 0,
            team2Goals INTEGER DEFAULT 0,
            matchTime TEXT
        )
        """
        self.cursor.execute(matchDataTableCreationQuery)
        self.connection.commit()
        
        
##############################################################################################
    def add_name_entry(self, entry_text="", mp3_path=""):
        #print(entry_text)
        count = len(self.name_entries) + 1
        team_id = count - 1

        # Create a label with "Team 1" and the count
        label_text = f'Team {count}'
        label = ctk.CTkLabel(self.frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.name_entries), column=0, padx=5, pady=5, sticky='e')
        
        # Create a new entry field
        new_entry = ctk.CTkEntry(self.frame, font=("Helvetica", 14))  # Increase font size
        
        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)
        
        new_entry.grid(row=len(self.name_entries), column=1, pady=5, sticky='we')
        
        new_file_dialog = ctk.CTkButton(self.frame, text="Select mp3", command=lambda: self.save_mp3_path(new_file_dialog, team_id))
        new_file_dialog.grid(row=len(self.name_entries), column=2, pady=5, sticky='we', padx=5)
        
        if mp3_path:
            self.mp3_list[team_id] = mp3_path
            new_file_dialog.configure(text=os.path.basename(mp3_path))
        
        self.file_dialog_list.append(new_file_dialog)
        self.name_entries.append(new_entry)
        self.label_list.append(label)


    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    
    def save_mp3_path(self, new_file_dialog, team_id):
        file_path = filedialog.askopenfilename(initialdir="/", title="Select mp3 file", filetypes=(("mp3 files", "*.mp3"), ("all files", "*.*")))
        
        if file_path:
            self.mp3_list[team_id] = file_path
            new_file_dialog.configure(text=os.path.basename(file_path))

        #print(file_path)
        #self.cursor.execute("UPDATE teamData SET mp3Path = ? WHERE id = ?", (file_path, team_id))
        #self.connection.commit()
       
        
    def reload_button_command(self):
        # Delete all entry fields
        
        self.mp3_list = {}
        
        for entry in self.name_entries:
            entry.destroy()
        self.name_entries = []
        
        for label in self.label_list:
            label.destroy()
            
        for file_fialog in self.file_dialog_list:
            file_fialog.destroy()
        
        # Read the names from the file and put them into the entry fields
        self.write_names_into_entry_fields()
        
        
    def save_team_names_in_db(self):
        old_mp3_list = []
        name_entries = self.name_entries
        
        get_team_ids = "SELECT id FROM teamData"
        old_team_ids = self.cursor.execute(get_team_ids).fetchall()

        print("old_team_ids", old_team_ids)
        self.cursor.execute("SELECT mp3Path FROM teamData")
        entries = self.cursor.fetchall()
        
        for i in enumerate(old_team_ids):
            old_mp3_list.append("")
            
        print("entries", entries)
        for i, entry in enumerate(entries):
            old_mp3_list[i] = entry
            
        # Get existing teams from the database
        self.cursor.execute("DROP TABLE teamData")      
        
        teamDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS teamData (
            id INTEGER PRIMARY KEY,
            teamName TEXT UNIQUE,
            goals INTEGER DEFAULT 0,
            goalsReceived INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            mp3Path TEXT DEFAULT "",
            groupNumber INTEGER
        )
        """
        
        self.cursor.execute(teamDataTableCreationQuery)
        self.connection.commit()
        
        for entry in name_entries:
            entry_text = entry.get().strip()
            print("entry_text", entry_text)
            if entry_text:
                # Update existing team
                try:
                    insert_query = "INSERT INTO teamData (teamName) VALUES (?)"
                    self.cursor.execute(insert_query, (entry_text,))
                except sqlite3.IntegrityError:
                    for i in range(1, 100):
                        if f"{entry_text} {i}" not in self.read_teamNames():
                            entry_text = f"{entry_text} {i}"
                            break
                    insert_query = "INSERT INTO teamData (teamName) VALUES (?)"
                    self.cursor.execute(insert_query, (entry_text,))
                    
        #get all ids from teamData
        self.cursor.execute("SELECT id FROM teamData")
        team_ids = [row[0] for row in self.cursor.fetchall()]
        for team_id in team_ids:
            mp3_entry = self.mp3_list.get(team_id-1, "")
            print("mp3_entry", mp3_entry.strip())
            if mp3_entry.strip() == "" and old_mp3_list is not None and team_id - 1 < len(old_mp3_list) and old_mp3_list[team_id - 1] is not None:
                self.mp3_list[team_id-1] = old_mp3_list[team_id-1][0]

        set_mp3_paths = "UPDATE teamData SET mp3Path = ? WHERE id = ?"
        self.cursor.executemany(set_mp3_paths, [(mp3_path, team_id + 1) for team_id, mp3_path in self.mp3_list.items()])
        
        #self.updated_data.update({"Teams": team_names})
        self.connection.commit()
        
    
    def write_names_into_entry_fields(self):
        selectTeams = """
        SELECT teamName, mp3Path FROM teamData
        ORDER BY id ASC
        """
        self.cursor.execute(selectTeams)
        
        allfetched = self.cursor.fetchall()
        
        if allfetched == []:
            self.add_name_entry()
        
        #print("allfetched", allfetched)
        for teamName, mp3_path in allfetched:
            #print("teamName", teamName)
            #print("mp3_path", mp3_path)
            self.add_name_entry(teamName, mp3_path)
           

    def create_Team_elements(self):
        # Create elements for the Team frame
        canvas = tk.Canvas(self.Team_frame)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ctk.CTkScrollbar(self.Team_frame, orientation='vertical', command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frame = ctk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        name_entries = []
        self.write_names_into_entry_fields()

        self.frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        # Button to add a new name entry
        add_button = ctk.CTkButton(self.Team_frame, text="Add Name", command=self.add_name_entry)
        add_button.pack(pady=10)

        # Button to retrieve the entered names


        submit_button = ctk.CTkButton(self.Team_frame, text="Submit", command=self.save_team_names_in_db)
        submit_button.pack(pady=10)

        
        reload_button = ctk.CTkButton(self.Team_frame, text="Reload", command=self.reload_button_command)
        reload_button.pack(pady=10)
        

##############################################################################################

##############################################################################################

    def create_player_elements(self):
        # Create elements for the player frame
        #player_button = tk.Button(self.player_frame, text="player Button", command=self.player_button_command)
        #player_button.pack(pady=10)
        # Create elements for the Team frame
        self.canvas = tk.Canvas(self.player_frame)
        self.canvas.pack(fill="both", expand=True, side="bottom")

        # Create a scrollbar and connect it to the canvas
        scrollbar = ctk.CTkScrollbar(self.player_frame, orientation='vertical', command= self.canvas.yview, height=25)
        scrollbar.pack(side=tk.LEFT, fill="y")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.configure(yscrollincrement=6)

        self.frameplayer = ctk.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frameplayer, anchor="nw")
        
        self.test_frame = ctk.CTkFrame(self.player_frame, bg_color='grey17', fg_color='grey17')
        self.test_frame.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.X, padx=10, expand=True)
        
        buttons_frame = ctk.CTkFrame(self.test_frame, bg_color='grey15', fg_color='grey15')
        buttons_frame.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)
        
        # Button to add a new name entry
        add_button = ctk.CTkButton(buttons_frame, text="Add Name", command=lambda: self.add_name_entry_player(self.frameplayer, "Player"))
        add_button.pack(pady=20, padx=20, anchor=tk.NE, side=tk.RIGHT)    

        # Button to retrieve the entered names
        submit_button = ctk.CTkButton(buttons_frame, text="Submit", command=self.save_names_player)
        submit_button.pack(pady=20, padx=20, anchor=tk.NE, side=tk.RIGHT)    

        reload_button = ctk.CTkButton(buttons_frame, text="Reload", command=self.reload_button_player_command)
        reload_button.pack(pady=20, padx=20, anchor=tk.NE, side=tk.RIGHT)    
        
        self.selected_team = ""
        self.team_button_list = []
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        teamNames.pop(0)
        #print("teamNames", teamNames, "team_IDs", team_IDs)
        
        self.player_top_frame = ctk.CTkFrame(self.test_frame, width=1, height=1)

        self.player_bottom_frame = ctk.CTkFrame(self.test_frame, width=1, height=1)

        for i, teamID in enumerate(team_IDs):
            try:
                teamName = teamNames[int(teamID-1)]
            except:
                print("teamID", teamID)
                print("teamNames", teamNames)
                print("team_IDs", team_IDs)
                print("i", i)

            if i < 10:
                team_button = ctk.CTkButton(
                    self.player_top_frame,
                    text=teamName,
                    command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2),
                    width=120
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            else:
                team_button = ctk.CTkButton(
                    self.player_bottom_frame,
                    text=teamName,
                    command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2),
                    width=120
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            self.team_button_list.append(team_button)
            
        self.player_top_frame.pack(anchor=tk.NW, side=tk.TOP)
        self.player_bottom_frame.pack(anchor=tk.NW, side=tk.TOP)
        
        
    def save_names_player(self, team_id=-1):
        entries = self.variable_dict.get(f"entries{self.frameplayer}")
        entries2 = self.variable_dict.get(f"entries2{self.frameplayer}")
        entries3 = self.variable_dict.get(f"entries3{self.frameplayer}")

        if team_id == -1:
            team_id = self.selected_team

        if entries:
            
            # Get existing players for the team from the database
            self.cursor.execute("SELECT playerName FROM playerData WHERE teamId = ?", (team_id,))
            existing_players = {row[0] for row in self.cursor.fetchall()}

            # Iterate through the current entries and update or insert as needed
            for entry, entrie2, entrie3 in zip(entries, entries2, entries3):
                #print(entries)
                entry_text = str(entry.get())
                entry_text2 = str(entrie2.get())
                entry_text3 = str(entrie3.get())

                if entry_text:
                    # Update existing player
                    if entry_text in existing_players:
                        update_query = "UPDATE playerData SET playerNumber = ?, goals = ? WHERE playerName = ? AND teamId = ?"
                        self.cursor.execute(update_query, (entry_text2, entry_text3, entry_text, team_id))
                    else:
                        # Add new player
                        try:
                            insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                            self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))
                            existing_players.add(entry_text)
                        except sqlite3.IntegrityError:
                            
                            for i in range(1, 100):
                                if f"{entry_text} {i}" not in existing_players:
                                    entry_text = f"{entry_text} {i}"
                                    break
                            insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                            self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))
                                
            #get all ids from playerData
            self.cursor.execute("SELECT id FROM playerData")
            player_ids = [row[0] for row in self.cursor.fetchall()]
            for i, player_id in enumerate(player_ids):
                if i + 1 != player_id:
                    self.cursor.execute("UPDATE playerData SET id = ? WHERE id = ?", (i+1, player_id))
            

            # Delete players not in the entries
            players_to_delete = existing_players - {entry.get() for entry in entries}
            for player_name in players_to_delete:
                self.cursor.execute("DELETE FROM playerData WHERE playerName = ? AND teamId = ?", (player_name, team_id))

            self.connection.commit()
            
            

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
        label = ctk.CTkLabel(Frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.variable_dict[varentrie1name]), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = ctk.CTkEntry(Frame)  # Increase font size
        
        new_entry2 = ctk.CTkEntry(Frame)  # Increase font size
        
        new_entry3 = ctk.CTkEntry(Frame)  # Increase font size
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

    
    def write_names_into_entry_fields_players(self, teamID, Counter, Frame):
        # Read player names using read_player_stats function
        output = self.read_player_stats(teamID, True)
        player_names = [row[0] for row in output]
        player_numbers = [row[1] for row in output]
        goals = [row[2] for row in output]

        # if the file is empty or no names are read, add an empty entry
        if not player_names:
            self.add_name_entry_player(Frame, Counter)
        else:
            # if names are read, put them into the entry fields
            for player_name, player_number, goal in zip(player_names, player_numbers, goals):
                self.add_name_entry_player(Frame, Counter, player_name, player_number, goal)


    def reload_button_player_command(self):
        
        for button in self.team_button_list:
            button.destroy()
        
        self.selected_team = ""
        self.team_button_list = []
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        teamNames.pop(0)
        #print("teamNames", teamNames, "team_IDs", team_IDs)
        
        for i, teamID in enumerate(team_IDs):
            teamName = teamNames[int(teamID-1)]

            if i < 10:
                team_button = ctk.CTkButton(
                    self.player_top_frame,
                    text=teamName,
                    command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2),
                    width=120
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            else:
                team_button = ctk.CTkButton(
                    self.player_bottom_frame,
                    text=teamName,
                    command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2),
                    width=120
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            self.team_button_list.append(team_button)
    
        
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
    
    
    def select_team(self, teamID, team_button_list, index):
        
        #for button in team_button_list:
        #    button.configure(bg="lightgray")
        self.canvas.yview_moveto(0.0)
        
        team_button = team_button_list[index]
        
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
        
        self.selected_team = teamID
        
        self.variable_dict[varcountname] = 0
        self.variable_dict[varentrie1name] = []
        self.variable_dict[varentrie2name] = []
        self.variable_dict[varentrie3name] = []
        self.variable_dict[varlabelname] = []
        
        
        self.write_names_into_entry_fields_players(teamID, "Player", self.frameplayer)
          
            
    def read_player_stats(self, teamID, readGoals=False, playerID=-1):
        output = []

        if readGoals and playerID == -1:
            getData = """
            SELECT playerName, playerNumber, goals FROM playerData
            WHERE teamId = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID,))

            for row in self.cursor.fetchall():
                output.append(row)

        elif readGoals and playerID != -1:
            #print("readGoals", readGoals, "playerID", playerID, "teamID", teamID)
            getData = """
            SELECT playerName, playerNumber, goals FROM playerData
            WHERE teamId = ? AND id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID, playerID))

            for row in self.cursor.fetchall():
                output.append(row)
                
        elif not readGoals and playerID != -1:
            getData = """
            SELECT playerName, playerNumber FROM playerData
            WHERE teamId = ? AND id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID, playerID))
            
            for row in self.cursor.fetchall():
                output.append(row)
            
        else:
            getData = """
            SELECT playerName, playerNumber FROM playerData
            WHERE teamId = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID,))
            
            for row in self.cursor.fetchall():
                output.append(row)
                

        return output
            
            
    def read_teamNames(self, teams_to_read=-1):
        teamNames = [""]
        
        if teams_to_read != -1:
            for team in teams_to_read:
                if team != None:
                    team = int(team) + 1
                        
                    selectTeam = """
                    SELECT teamName FROM teamData
                    WHERE id = ?
                    ORDER BY id ASC
                    """
                    self.cursor.execute(selectTeam, (team,))
                    result = self.cursor.fetchone()
                    if result is not None:
                        #print(result)
                        teamNames.append(result[0])
          
        else:
            selectTeams = """
            SELECT teamName FROM teamData
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeams)
        
            for team in self.cursor.fetchall():
                teamNames.append(team[0])
        #print("teamNames", teamNames)
        return teamNames
    
    
    def read_teamIds(self):
        teamIds = []
        
        self.cursor.execute("SELECT id FROM teamData")
        
        for id in self.cursor.fetchall():
            teamIds.append(id[0])
        teamIds.sort()

        return teamIds


    def get_team_id_from_team_name(self, team_name):

        self.cursor.execute("SELECT id FROM teamData WHERE teamName = ?", (team_name,))
        
        team_id = self.cursor.fetchone()[0]
        
        return team_id
    
    
    def get_player_id_from_player_name(self, player_name):
        
        self.cursor.execute("SELECT id FROM playerData WHERE playerName = ?", (player_name,))
        
        player_id = self.cursor.fetchone()[0]
        
        return player_id


##############################################################################################
##############################################################################################
##############################################################################################

    def create_SPIEL_elements(self):
        
        # Create elements for the SPIEL frame
        manual_frame = ctk.CTkFrame(self.SPIEL_frame, bg_color='grey17', fg_color='grey17')
        manual_frame.pack(pady=5, anchor=tk.S, side=tk.BOTTOM, padx=5, fill=tk.X)
        
        manual_manual_frame = ctk.CTkFrame(manual_frame, bg_color='grey17', fg_color='grey17')
        manual_manual_frame.pack(pady=0, anchor=tk.SE, side=tk.RIGHT, padx=0)
        
        SPIEL_button = ctk.CTkButton(manual_manual_frame, text="Reload", command=lambda : self.reload_spiel_button_command())
        SPIEL_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.S) 
        
        
        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}

        #print("self.teams_playing", self.teams_playing)
        
        for i, _ in enumerate(self.teams_playing):
            
            #print(self.teams_playing)
            
            team_names = self.read_teamNames()
            if self.teams_playing[i] is not None:
                #print("i" , i, "teamnames", team_names)
                #print(self.teams_playing[i])
                team_name = team_names[self.teams_playing[i]]
                
            else:
                # Handle the case when self.teams_playing[i + 1] is None
                # For example, you can set team_name to an empty string
                break
                
            team_id = self.teams_playing[i]
            
            if i == 0:
                team2_id = self.teams_playing[i + 1]
            elif i == 1:
                team2_id = self.teams_playing[i - 1]

            #print(team)
            
            # Initialize the dictionary for the current team
            self.spiel_buttons[team_id] = {}
                    
            self.for_team_frame = ctk.CTkFrame(self.SPIEL_frame, bg_color='grey17', fg_color='grey17')
            self.for_team_frame.pack(pady=10, anchor=tk.NW, side=tk.TOP, fill="both", padx=10, expand=True)
            
            self.for_team_frame.tk_setPalette(
                background='grey17', 
                bg_color='grey17', 
                fg_color='grey17',
                activeBackground='grey17', 
                activeForeground='grey17', 
                foreground='grey17'
                )
            self.for_team_frame.configure(bg_color="grey17")
            
            # Create global scores buttons, one for up and one for down
            score_button_frame = ctk.CTkFrame(self.for_team_frame, bg_color='grey17', fg_color='grey17')
            score_button_frame.pack(pady=10, anchor=tk.E, side=tk.RIGHT, padx=10)
            
            score_button_up = ctk.CTkButton(score_button_frame, text="UP", command=lambda team=team_id, team2=team2_id: self.global_scored_a_point(team, team2, "UP"))
            score_button_up.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_label_var = tk.StringVar()
            score_label_var.set(self.read_goals_for_match_from_db(team_id, team2_id))
            
            score_label = ctk.CTkLabel(score_button_frame, text="None", font=("Helvetica", 14), textvariable=score_label_var)
            score_label.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_button_down = ctk.CTkButton(score_button_frame, text="DOWN", command=lambda team=team_id, team2=team2_id: self.global_scored_a_point(team, team2, "DOWN"))
            score_button_down.pack(pady=2, anchor=tk.N, side=tk.BOTTOM, expand=True, fill=tk.X)
            
            self.team_label = ctk.CTkLabel(self.for_team_frame, text=team_name, font=("Helvetica", 14))
            self.team_label.pack(side=tk.LEFT, pady=2, anchor=tk.NW)
            
            self.spiel_buttons[team_id]["global"] = (self.for_team_frame, self.team_label, score_button_up, score_label_var, score_button_down)
            
            frame_frame = ctk.CTkFrame(self.for_team_frame, bg_color='grey17', fg_color='grey17')
            frame_frame.pack(side=tk.TOP, pady=0, anchor=tk.N)

            up_frame = ctk.CTkFrame(frame_frame)
            up_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

            down_frame = ctk.CTkFrame(frame_frame)
            down_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
            

            for i, (player_name, player_number, goals) in enumerate(self.read_player_stats(team_id, True)):       
                #print(type(player_name), player_name)
                player_index = i 
                player_id = self.get_player_id_from_player_name(player_name)
                if i < 8:
                    self.group_frame = ctk.CTkFrame(up_frame, bg_color='grey17', fg_color='grey15')
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
                else:
                    self.group_frame = ctk.CTkFrame(down_frame, bg_color='grey17', fg_color='grey15')
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
                
                #self.group_frame = tk.Frame(self.for_team_frame, background="lightcoral")
                #self.group_frame.pack(side=tk.LEFT, padx=10, pady=10)

                playertext1 = ctk.CTkLabel(self.group_frame, text=f"Player {i}", font=("Helvetica", 14))
                playertext1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playertext2_text = f"{player_name} - {player_number}"
                
                playertext2 = ctk.CTkLabel(master=self.group_frame, text=playertext2_text , font=("Helvetica", 14))
                playertext2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playertext3 = ctk.CTkLabel(self.group_frame, text=f"Tore {str(goals)}", font=("Helvetica", 14))
                playertext3.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)

                playerbutton1 = ctk.CTkButton(self.group_frame, text="UP", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index,  "UP"))
                playerbutton1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playerbutton2 = ctk.CTkButton(self.group_frame, text="DOWN", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index, "DOWN"))
                playerbutton2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                
                #print("team", team, "i", i)

                # Save the group_frame, playertext1, and playerbutton in each for loop with the team name as key
                self.spiel_buttons[team_id][i] = (self.group_frame, playertext1, playertext2, playertext3, playerbutton1, playerbutton2)  # Use append for a list
                
                #self.spiel_buttons[team] = (playerbutton)  # Use append for a list

        teams_list = self.read_teamNames()
        teams_list.pop(0)
        #print("teams_list", teams_list)

        self.manual_team_select_1 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", 14), 
            state=tk.DISABLED, 
            command=lambda event: self.on_team_select(event, nr=1)
            )
        self.manual_team_select_1.set("None")
        self.manual_team_select_1.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        #self.manual_team_select_1.bind("<<ComboboxSelected>>", lambda event, nr=1: self.on_team_select(event, nr))
        
        self.manual_team_select_2 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", 14), 
            state=tk.NORMAL, 
            command=lambda event: self.on_team_select(event, nr=0)
            )
        self.manual_team_select_2.set("None")
        self.manual_team_select_2.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        #self.manual_team_select_2.bind("<<ComboboxSelected>>", lambda event, nr=0: self.on_team_select(event, nr))


        self.create_matches_labels(manual_frame)


        if self.teams_playing.count(None) == 0:
            #print(self.teams_playing)
            #print(self.read_teamNames())
            self.manual_team_select_2.configure(state=tk.NORMAL)
            self.manual_team_select_1.configure(state=tk.NORMAL)
            self.manual_team_select_1.set(self.read_teamNames()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
            
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.configure(tk.DISABLED)
            self.manual_team_select_1.set("None")

        
        #print("self.teams_playing", self.teams_playing)
        if self.teams_playing.count(None) == 1:
            #print(self.teams_playing)
            self.manual_team_select_1.configure(state=tk.NORMAL)
            self.manual_team_select_1.set("None")
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])        


    def on_team_select(self, event, nr):
        #print("on_team_select")
        #print(event)
        #selected_team = event.widget.get()
        selected_team = event
        
        # Convert the value to the team index
        team_index = self.read_teamNames().index(selected_team)

        # Ensure self.teams_playing has enough elements
        while len(self.teams_playing) <= nr:
            self.teams_playing.append(None)

        # Assign the team index to the specified position
        self.teams_playing[nr] = team_index
        
        
        if self.teams_playing.count(None) == 0:
            self.manual_team_select_2.configure(state=tk.NORMAL)
            self.manual_team_select_1.configure(state=tk.NORMAL)
            self.manual_team_select_1.set(self.read_teamNames()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
        
        #print("self.teams_playing", self.teams_playing)
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.configure(state=tk.NORMAL)
            self.manual_team_select_1.set("None")
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
        
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.configure(tk.DISABLED)
            self.manual_team_select_1.set("None")
            
        
        self.reload_spiel_button_command()
        
        self.show_frame(self.SPIEL_frame)

        
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


    def delete_frame(self, frame):
        frame.grid_forget()
        frame.pack_forget()
        frame.destroy()
    
    
    def reload_spiel_button_command(self):
        
        self.calculate_points()
                
        # Delete all entry fields
        self.SPIEL_frame.grid_forget()
        self.SPIEL_frame.pack_forget()
        self.SPIEL_frame.destroy()
    
        
        self.SPIEL_frame = ctk.CTkFrame(self)
        

        self.create_SPIEL_elements()

        
    def player_scored_a_point(self, teamID, player_id, player_index, direction="UP"):
        # Get the current score
        #print(self.read_player_stats(teamID, True, player_id)) 
        current_goals = self.read_player_stats(teamID, True, player_id)[0][2]
        
        # Update the score
        if direction == "UP":
            current_goals += 1
        else:
            current_goals -= 1
        
        start_time = time.time()
        
        # Update the score label
        self.spiel_buttons[teamID][player_index][3].configure(text=f"Tore {current_goals}")

        
        
        #print("Write", "teamID", teamID, "player_index", player_id)
        
        updateGoals = """
        UPDATE playerData
        SET goals = ?
        WHERE teamId = ? AND id = ?
        """
        self.cursor.execute(updateGoals, (current_goals, teamID, player_id))
        
        # Commit the changes to the database
        self.connection.commit()
        
        # Close the database self.connection
        
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time in milliseconds
        elapsed_time_ms = (end_time - start_time) * 1000

        # #print the result
        #print(f"Elapsed Time: {elapsed_time_ms:.2f} ms")
        
        ###self.updated_data.update({"SPIEL": {team: self.read_team_names_player(team)}})
    
    
    def create_matches_labels(self, frame):
        matches = self.calculate_matches()
        #print(matches)
        
        spiel_select_frame = ctk.CTkFrame(frame)
        spiel_select_frame.pack(pady=10, padx=10, anchor=tk.SW, side=tk.LEFT)
        
        spiel_select = ctk.CTkComboBox(spiel_select_frame, font=("Helvetica", 14), width=200, values=[""], command=lambda event: self.on_match_select(event, matches))
        spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N)

        #spiel_select.bind("<<ComboboxSelected>>", lambda event: self.on_match_select(event, matches))
    
        # Initialize the values as an empty list
        values_list = []

        for match in matches:
            # Append each match label to the values list
            #print(match)
            #print(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])
            #print("match", match)
            values_list.append(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])

        # Set the values of the Combobox after the loop
        spiel_select.configure(values=values_list)
        
        # get the index of the match that is currently being played and set the Combobox value to that match without using self.match_count - 1
        
        for match in matches:
            match_teams_indexes = [self.read_teamNames().index(match_team) for match_team in match["teams"]]
            if match_teams_indexes == self.teams_playing or match_teams_indexes[::-1] == self.teams_playing:
                se = match["number"]
                self.active_match = int(se.replace("Spiel ", "")) - 1
                #print("self.active_matchcreate_matches_labels", self.active_match)
                #print("got it")
                break
            #print(match["teams"], self.teams_playing, match["number"], match_teams_indexes, match_teams_indexes[::-1])
        else:
            if self.teams_playing.count(None) == 0:
                values_list = []
                values_list.append("No Match found")
                spiel_select["values"] = values_list
                spiel_select.set(values_list[0])
                #print("no match found")
                return
        
        if self.teams_playing.count(None) == 0:
            
            se = int(se.replace("Spiel ", "")) - 1
            current_match_index = se
            spiel_select.set(values_list[current_match_index])
            
            
        next_match_button = ctk.CTkButton(spiel_select_frame, text="Next Match", command=lambda : self.next_previous_match_button(spiel_select, matches))
        next_match_button.pack(pady=10, padx=5, side=tk.RIGHT, anchor=tk.SE)
        
        previous_match_button = ctk.CTkButton(spiel_select_frame, text="Previous Match", command=lambda : self.next_previous_match_button(spiel_select, matches, False))
        previous_match_button.pack(pady=10, padx=5, side=tk.LEFT, anchor=tk.SW)


    def on_match_select(self, event, matches):
        selected_match = event
        #print(selected_match)
        #print(matches)
        # Convert the value to the match index
        match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(selected_match)
        print("match_index", match_index)
        # Get the teams playing in the selected match and if there are none, set teams_playing to None
        team_names = self.read_teamNames()
        
        team1_index = team_names.index(matches[match_index]["teams"][0])
        team2_index = team_names.index(matches[match_index]["teams"][1])

        if team1_index and team2_index:
            self.teams_playing = [team1_index, team2_index]
        else:
            self.teams_playing = [None, None]
            
        self.active_match = match_index
        #print("self.active_matchon_match_select", self.active_match)
        
        self.save_games_played_in_db(match_index)
        
        self.updated_data.update({"Games": get_data_for_website(2)})
        
        self.reload_spiel_button_command()
        
        self.show_frame(self.SPIEL_frame)
        
    
    def next_previous_match_button(self, spiel_select, matches, next_match=True):
        try:
            # Get the current match index
            current_match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(spiel_select.get()) + 1

            # Calculate the new match index
            new_match_index = current_match_index + 1 if next_match else current_match_index - 1

            # Ensure the new index is within bounds
            new_match_index = max(1, min(new_match_index, len(matches)))

            # Get the teams playing in the selected match
            team_names = self.read_teamNames()
            teams_playing = [team_names.index(matches[new_match_index - 1]["teams"][0]), team_names.index(matches[new_match_index - 1]["teams"][1])] if new_match_index > 0 else [None, None]

            # Update the buttons
            self.teams_playing = teams_playing
            self.reload_spiel_button_command()
            self.show_frame(self.SPIEL_frame)
            

        except ValueError:
            # Handle the case where the selected match is not found in the list
            print("Selected match not found in the list.")


    def global_scored_a_point(self, teamID, team2ID, direction="UP"):
        # Get the current score
        current_score = self.read_goals_for_match_from_db(teamID, team2ID)
        
        # Update the score
        if direction == "UP" and current_score != "None":
            current_score += 1
            self.play_mp3(self.read_mp3_path_from_db_for_team(teamID), 100)
            
        elif direction == "DOWN" and current_score != "None":
            current_score -= 1
            
        # Write the score into the database
        
        if self.write_score_for_team_into_db(teamID, team2ID, direction):

            # Update the score label
            self.spiel_buttons[teamID]["global"][3].set(str(current_score))
            self.updated_data.update({"Goals": get_data_for_website(1)})
    
    
    def read_mp3_path_from_db_for_team(self, teamID):
        selectPath = """
        SELECT mp3Path FROM teamData
        WHERE id = ?
        """
        self.cursor.execute(selectPath, (teamID,))
        
        mp3Path = self.cursor.fetchone()[0]
        
        if mp3Path == "":
            return ""
        
        return mp3Path
       
        
    def write_score_for_team_into_db(self, teamID, team2ID, direction="UP"):
        
        goals = self.read_goals_for_match_from_db(teamID, team2ID)
        
        if goals == "None":
            return False
        
        if direction == "UP":
            goals += 1
        else:
            goals -= 1
        
        self.save_goals_for_match_in_db(teamID, team2ID, goals)
        
        self.save_goals_for_teams_in_db(teamID, team2ID, direction)
        
        return True
    
    
    def save_goals_for_teams_in_db(self, teamID, team2ID, direction="UP"):
        
        #first add one goal to the team that scored, which is teamID
        goals = self.read_team_stats(teamID, "score")
        
        if direction == "UP":
            goals += 1
        else:
            goals -= 1
            
        updateGoals = """
        UPDATE teamData
        SET goals = ?
        WHERE id = ?
        """
        self.cursor.execute(updateGoals, (goals, teamID))
        
        #then add one goal to the team that got scored against, which is team2ID
        goalsReceived = self.read_team_stats(team2ID, "goalsReceived")
        
        if direction == "UP":
            goalsReceived += 1
        else:
            goalsReceived -= 1
            
        updateGoals = """
        UPDATE teamData
        SET goalsReceived = ?
        WHERE id = ?
        """
        self.cursor.execute(updateGoals, (goalsReceived, team2ID))
        
        self.connection.commit()
        

    def save_goals_for_match_in_db(self, teamID, team2ID, goals):
        
        get_team1_or_team2 = """
        SELECT 
            CASE 
                WHEN team1Id = ? THEN 'team1Goals'
                WHEN team2Id = ? THEN 'team2Goals'
                ELSE 'Not Found'
            END AS TeamIdColumn
        FROM matchData
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_team1_or_team2, (teamID, teamID, teamID, team2ID, team2ID, teamID))
        
        self.team1_or_team2 = self.cursor.fetchone()[0]
        
        print("self.team1_or_team2", self.team1_or_team2)
        
        
        update_goals_for_match = """
        UPDATE matchData
        SET {column} = ?
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(update_goals_for_match.format(column=self.team1_or_team2), (goals, teamID, team2ID, team2ID, teamID))
        
        self.connection.commit()
        
        
    def read_goals_for_match_from_db(self, teamID, team2ID):
        
        #print("read_goals_for_match_from_db", "teamID", teamID, "team2ID", team2ID)
        
        get_team1_or_team2 = """
        SELECT 
            CASE 
                WHEN team1Id = ? THEN 'team1Goals'
                WHEN team2Id = ? THEN 'team2Goals'
                ELSE 'Not Found'
            END AS TeamIdColumn
        FROM matchData
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_team1_or_team2, (teamID, teamID, teamID, team2ID, team2ID, teamID))
        
        onefetched = self.cursor.fetchone() 
        
        if onefetched == None:
            return "None"
        
        print(onefetched)
        
        self.team1_or_team2 = onefetched[0]
        print("self.team1_or_team2", self.team1_or_team2)
        
        
        get_goals_for_match = """
        SELECT {column} FROM matchData
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_goals_for_match.format(column=self.team1_or_team2), (teamID, team2ID, team2ID, teamID))
        
        goals = self.cursor.fetchone()[0]
        print("goals", goals)
        
        return goals
        
    
    def read_team_stats(self, team_id, stat):
        #print("read_team_stats", "teams_playing", self.teams_playing, "team_id", team_id, "stat", stat)
        
        if stat == "score":
            
            get_score = """
            SELECT goals FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(get_score, (team_id,))
            
            score = self.cursor.fetchone()[0]
            
            return score

        if stat == "goalsReceived":
            
            get_goalsRecived = """
            SELECT goalsReceived FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(get_goalsRecived, (team_id,))
            
            goalsRecived = self.cursor.fetchone()[0]
            
            return goalsRecived
        
    
    def save_games_played_in_db(self, match_index):
        
        teams_ids = self.read_teamIds()
        for teamID in teams_ids:
            
            getPlayed = """
            SELECT matchId FROM matchData
            WHERE (team1Id = ? OR team2Id = ?) AND matchId < ?
            """
            self.cursor.execute(getPlayed, (teamID, teamID, match_index + 2))
            
            played = self.cursor.fetchall()
            
            print("played", played)
            
            played = len(played)
            
            updatePlayed = """
            UPDATE teamData
            SET games = ?
            WHERE id = ?
            """
            
            self.cursor.execute(updatePlayed, (played, teamID))
            
        self.connection.commit()
    
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
        self.reload_spiel_button_command()
        #print(stored_data)
        self.calculate_matches()
        self.show_frame(self.SPIEL_frame)

    ##############################################################################################
            
    def test(self):
        print("test")
        
        
    def delete_updated_data(self):
        #print("delete")
        #print(self.updated_data)
        self.updated_data = {}
        
        
    def play_mp3(self, file_path, volume):
        if file_path == "":
            return
        player = self.media_player_instance.media_player_new()
        media = self.media_player_instance.media_new(file_path)
        player.set_media(media)
        player.audio_set_volume(volume)
        player.play()
        
    ##############################################################################################
    #############################Calculatre########################################################
    ##############################################################################################
    ##############################################################################################
    def calculate_matches(self):
        
        self.match_count = 0

        initial_data = {
        "Teams": self.read_teamNames()
        }
        
        initial_data["Teams"].pop(0)
        
        teams = initial_data["Teams"][:]  # Create a copy of the teams array
        #print("teams", teams)
        
        # If the number of teams is odd, add a "dummy" team
        if len(teams) % 2 != 0:
            teams.append("dummy")

        midpoint = (len(teams) + 1) // 2
        group1 = teams[:midpoint]
        group2 = teams[midpoint:]
        
        print("group1", group1, "group2", group2, "teams", teams, "midpoint", midpoint)

        matches1 = self.calculate_matches_for_group(group1, "Gruppe 1")
        matches2 = self.calculate_matches_for_group(group2, "Gruppe 2")

        matches = self.interleave_matches(matches1, matches2)
        
        #print("matches", matches, "matches1", matches1, "matches2", matches2)
        
        self.match_count = 0

        self.matches = list(map(lambda match: self.add_match_number(match), matches))
        
        #print(self.matches)
        
        self.save_matches_to_db()
        
        return self.matches
    
    
    def interleave_matches(self, matches1, matches2):
        matches = []
        i = j = 0
        while i < len(matches1) or j < len(matches2):
            if i < len(matches1):
                matches.append(matches1[i])
                i += 1
            if j < len(matches2):
                matches.append(matches2[j])
                j += 1
        return matches


    def calculate_matches_for_group(self, teams, group_name):
        rounds = []

        for _ in range(len(teams) - 1):
            rounds.append([])
            for match in range(len(teams) // 2):
                team1 = teams[match]
                team2 = teams[-1 - match]
                rounds[-1].append([team1, team2])
            # Rotate the teams for the next round
            teams[1:1] = [teams.pop()]

        # Remove matches with the "dummy" team
        if "dummy" in teams:
            rounds = list(map(lambda rnd: list(filter(lambda match: "dummy" not in match, rnd)), rounds))

        matches = [match for rnd in rounds for match in rnd]

        matches = list(map(lambda match: {"number": "", "teams": match, "group": group_name}, matches))

        return matches


    def add_match_number(self, match):
         
        self.match_count += 1
        match["number"] = "Spiel " + str(self.match_count)
        return match


    def save_matches_to_db(self):
        
        get_existing_matches = """
        SELECT team1Id, team2Id, groupNumber, matchId, team1Goals, team2Goals, matchTime FROM matchData
        """
        
        self.cursor.execute(get_existing_matches)
        existing_matches = {tuple(row[:4]) for row in self.cursor.fetchall()}
        
        added_matches = []
        
        #print("existing_matches", existing_matches, "self.matches", self.matches)

        for match in self.matches:
            team1 = match["teams"][0]
            team2 = match["teams"][1]
            group = match["group"]
            number = match["number"]

            selectTeam1 = """
            SELECT id FROM teamData
            WHERE teamName = ?
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeam1, (team1,))
            team1ID = self.cursor.fetchone()[0]

            selectTeam2 = """
            SELECT id FROM teamData
            WHERE teamName = ?
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeam2, (team2,))
            team2ID = self.cursor.fetchone()[0]

            match_tuple = (int(team1ID), int(team2ID), int(str(group).replace('Gruppe ','')), int(str(number).replace('Spiel ','')))
            match_tuple2 = (int(team1ID), int(team2ID), int(str(group).replace('Gruppe ','')))
            
            added_matches.append(match_tuple)

            if match_tuple in existing_matches:
                get_existing_match_data = """
                SELECT * FROM matchData
                WHERE team1Id = ? AND team2Id = ? AND groupNumber = ? AND matchId = ?
                """
                self.cursor.execute(get_existing_match_data, match_tuple)
                existing_match_data = self.cursor.fetchone()

                # Copy the existing match data into the new match data
                match_data = existing_match_data

                updateMatch = """
                    UPDATE matchData
                    SET team1Id = ?, team2Id = ?, groupNumber = ?, team1Goals = ?, team2Goals = ?, matchTime = ?
                    WHERE team1Id = ? AND team2Id = ? AND groupNumber = ? AND matchId = ?
                """
                self.cursor.execute(updateMatch, match_data + match_tuple2)
            else:
                insertMatch = """
                    INSERT INTO matchData (team1Id, team2Id, groupNumber, matchId)
                    VALUES (?, ?, ?, ?)
                """
                try:
                    self.cursor.execute(insertMatch, match_tuple)
                except sqlite3.IntegrityError:
                    print(f"matchId {match_tuple[3]} already exists. Skipping insertion.")
        
        teams_to_delete = []
        
        for existing_match in existing_matches:
            if existing_match not in added_matches:
                teams_to_delete.append(existing_match)
                
                
        #print("teams_to_delete", teams_to_delete)
        
        for team_to_delete in teams_to_delete:
            deleteMatch = """
                DELETE FROM matchData
                WHERE team1Id = ? AND team2Id = ? AND groupNumber = ? AND matchId = ?
            """
            self.cursor.execute(deleteMatch, team_to_delete)
            
        # Delete teams that are not in the sorted list of team IDs
        delete_teams = """
        DELETE FROM matchData WHERE matchId NOT IN (SELECT matchId FROM matchData ORDER BY matchId)
        """
        self.cursor.execute(delete_teams)
            
        self.connection.commit()
        
        
    def reset_points_for_all_teams_in_db(self):
        resetPoints = """
        UPDATE teamData
        SET points = 0
        """
        self.cursor.execute(resetPoints)
        self.connection.commit()
        
    
    def add_points_for_team_in_db(self, teamID, points):
        getPoints = """
        SELECT points FROM teamData
        WHERE id = ?
        ORDER BY id ASC
        """
        self.cursor.execute(getPoints, (teamID,))
        
        oldpoints = self.cursor.fetchone()[0]
        
        newpoints = oldpoints + points
        
        updatePoints = """
        UPDATE teamData
        SET points = ?
        WHERE id = ?
        """
        self.cursor.execute(updatePoints, (newpoints, teamID))
        
        self.connection.commit()    
    
        
    def calculate_points(self):
        selectMatches = """
            SELECT team1Id, team2Id, team1Goals, team2Goals
            FROM matchData
        """
        
        self.cursor.execute(selectMatches)
        matches = self.cursor.fetchall()
        
        self.reset_points_for_all_teams_in_db()
        
        for match in matches:
            if match[2] > match[3]:
                self.add_points_for_team_in_db(match[0], 3)
            elif match[2] < match[3]:
                self.add_points_for_team_in_db(match[1], 3)
            elif match[2] != 0 and match[3] != 0:
                self.add_points_for_team_in_db(match[0], 1)
                self.add_points_for_team_in_db(match[1], 1)
                
        self.updated_data.update({"Points": get_data_for_website(3)})    
                
            
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    
def get_data_for_website(which_data=-1):
    
    if which_data == 0:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        getTeams = """
        SELECT teamName FROM teamData
        ORDER BY id ASC
        """
        cursor.execute(getTeams)
        
        teamNames = []
        
        for team in cursor.fetchall():
            teamNames.append(team[0])
        
        #teamNames.pop(0)
            
        cursor.close()
        connection.close()
        
        return teamNames
    
    if which_data == 1:     
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        Tore = []
        
        get_teams = """
        SELECT id FROM teamData
        ORDER BY id ASC
        """
        cursor.execute(get_teams)
        
        for team in cursor.fetchall():
            
            team_score = """
            SELECT goals FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            cursor.execute(team_score, (team[0],))
            
            team_goals = cursor.fetchone()[0]
            
            team_goalsReceived = """
            SELECT goalsReceived FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            cursor.execute(team_goalsReceived, (team[0],))
            
            team_goalsReceived = cursor.fetchone()[0]
            
            Tore.append((team_goals, team_goalsReceived))
        
        cursor.close()
        connection.close()
            
        return Tore
        
    if which_data == 2:
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        get_teams = """
        SELECT id FROM teamData
        ORDER BY id ASC
        """
        
        cursor.execute(get_teams)
        
        games = []
        
        for Team in cursor.fetchall():
            
            getGamesFromTeam = """
            SELECT games FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            
            cursor.execute(getGamesFromTeam, (Team[0],))
            
            games.append(cursor.fetchone()[0])
            
        
        cursor.close()
        connection.close()
        
        return games
    
    if which_data == 3:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        get_points = """
        SELECT points FROM teamData
        ORDER BY id ASC
        """
        
        cursor.execute(get_points)
        
        points = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return points
            
def get_initial_data(template_name):
    global initial_data
    tkapp.test()
    
    
    initial_data = {
        "Teams": get_data_for_website(0),
        "Goals": get_data_for_website(1),
        "Games": get_data_for_website(2),
        "Points": get_data_for_website(3),
        "ZeitIntervall": 10,
        "Startzeit": [9,30],
        "LastUpdate": 0
    }
    return make_response(render_template(template_name, initial_data=initial_data))

@app.route("/")
def home():
    return get_initial_data("websitemain.html")

@app.route("/group")
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
        
        #print("updated_data)  ", updated_data, "last_data_update", last_data_update, "should be updated")
        #print(updated_data.keys())
        #print(updated_data.values())
        for key, value in updated_data.items():
            for key2, value2 in stored_data.items():
                if key in value2.keys():
                    stored_data.pop(key2)
                    break
            
            stored_data.update({time.time()-3:{key:value}})
            print("stored_data", stored_data)
        
        updated_data.update({"LastUpdate": timeatstart})
        
    for key, value in stored_data.items():
        #print("magucken")
        if key >= float(last_data_update):
            #print("key", key, "value", value, "last_data_update", last_data_update, "should be updated")
            updated_data.update(value)
            updated_data.update({"LastUpdate": timeatstart})
            #print("updated_data", updated_data)
            
    
    #print("stored_data", stored_data, "updated_data", updated_data, "last_data_update", last_data_update)
        
    #print("updated_data", updated_data)
    tkapp.delete_updated_data()
    #updated_data = {'Teams': tkapp.read_team_names(), 'Players': {"Player1":"Erik Van Doof","Player2":"Felix Schweigmann"}}  # You can modify this data as needed
    return jsonify(updated_data)

    
global tkapp
global server_thread
global stored_data
global initial_data
global db_path

db_path = "data/data.db"
stored_data = {}
tkapp = Window(True)

if __name__ == "__main__":
    tkapp.mainloop()