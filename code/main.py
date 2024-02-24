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
import datetime
import database_commands.database_commands as db_com


app = Flask(__name__)
#app.secret_key = "Felix.com"

lock = threading.Lock()

debug_mode = True

class Window(ctk.CTk):
    def custom_print(self, *args, **kwargs):
        #print(self.debug_mode.get())
        if self.debug_mode.get() == 1:
            #print("custom_print", *args, **kwargs)
            print(*args, **kwargs)
    
    
    def create_navigation_bar(self):
        navigation_frame = ctk.CTkFrame(self, fg_color='#142324', corner_radius=0)
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        buttons = [
            ("Team Creation", self.show_Team_frame),
            ("Player Selection", self.show_player_frame),
            ("Active Match", self.show_SPIEL_frame),
            ("Settings", self.show_settings_frame),
        ]

        button_width = self.screenwidth / 12.8
        button_height = self.screenheight / 25
        button_font_size = self.screenwidth / 120

        for text, command in buttons:
            button = ctk.CTkButton(navigation_frame, text=text, command=command, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
            button.pack(side=tk.TOP, anchor=tk.N, pady=8, padx=14, fill=tk.X)
            
            
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
        self.active_match = -1
        self.final_match_teams = []
        self.spiel_um_platz_3 = []
        self.matches = []
        
        self.delay_time_label = None
        self.settingsconnection = None
        self.settingscursor = None

        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()
        
        # Set window title
        self.title("Football Tournament Manager")
        self.after(0, lambda:self.state('zoomed'))
        self.configure(fg_color="#0e1718")
        try:
            icon_path = os.path.join('..', 'icon.ico')
            self.iconbitmap(icon_path)
        except:
            icon_path = os.path.join('icon.ico')
            self.iconbitmap(icon_path)
        
        self.tk_setPalette(background='#0e1718', foreground='#0e1718',
               activeBackground='#0e1718', activeForeground='#0e1718')
        
        ctk.set_appearance_mode("dark")
        
        self.init_sqlite_db()
        
        self.load_settings()
        
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
        self.Team_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)
        self.player_frame = ctk.CTkFrame(self, height=10, fg_color='#0e1718', corner_radius=0)
        self.SPIEL_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)
        self.settings_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)

        # Create elements for each frame
        self.create_Team_elements()
        self.create_player_elements()
        self.create_SPIEL_elements()
        self.create_settings_elements()

        # Display the default frame
        self.show_frame(self.Team_frame)
        
        #self.custom_print("finished init")
        
        
        if start_server:
            server_thread = threading.Thread(target=self.start_server)
            server_thread.start()
    
        
    def start_server(self):
        app.run(debug=False, threaded=True, port=5000, host="0.0.0.0", use_reloader=False)
    
    
    def init_sqlite_db(self):
        self.db_path = "data/data.db"
        self.settings_db_path = "data/settings.db"
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        self.settingsconnection = sqlite3.connect(self.settings_db_path)
        self.settingscursor = self.settingsconnection.cursor()
        
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
        
        finalMatchesDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS finalMatchesData (
            matchId INTEGER PRIMARY KEY,
            team1Id INTEGER REFERENCES teamData(id),
            team2Id INTEGER REFERENCES teamData(id),
            team1Goals INTEGER DEFAULT 0,
            team2Goals INTEGER DEFAULT 0,
            matchTime TEXT
        )
        """
        self.cursor.execute(finalMatchesDataTableCreationQuery)
        self.connection.commit()
        
        settingsDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS settingsData (
            id INTEGER PRIMARY KEY,
            roundTime INTEGER DEFAULT 0,
            breakTime INTEGER DEFAULT 0,
            isMatchAktive BOOLEAN DEFAULT 0,
            isBreak BOOLEAN DEFAULT 0,
            volume INTEGER DEFAULT 0,
            activeMode INTEGER DEFAULT 0,
            debugMode INTEGER DEFAULT 0,
            startTime TEXT DEFAULT "",
            timeInterval TEXT DEFAULT "",
            timeIntervalFM TEXT DEFAULT "",
            pauseBeforeFM TEXT DEFAULT "",
            websiteTitle TEXT DEFAULT ""
        )
        """
        self.settingscursor.execute(settingsDataTableCreationQuery)
        self.settingsconnection.commit()

        # Create a first row if there is no row
        self.settingscursor.execute("SELECT * FROM settingsData")
        if self.settingscursor.fetchone() is None:
            insert_query = "INSERT INTO settingsData (id) VALUES (?)"
            self.settingscursor.execute(insert_query, (1,))
        
    
    def load_settings(self):
        # get the settings from the database
        self.settingscursor.execute("SELECT * FROM settingsData")
        settings = self.settingscursor.fetchone()
        
        # create the variables for the settings
        self.volume = tk.IntVar(value=100)
        self.active_mode = tk.IntVar(value=1)
        self.debug_mode = tk.IntVar(value=0)
        self.start_time = tk.StringVar(value="08:00")
        self.time_interval = tk.StringVar(value="10m")
        self.time_intervalFM = tk.StringVar(value="10m")
        self.time_pause_before_FM = tk.StringVar(value="0m") 
        self.website_title = tk.StringVar(value="HHG-Fußballturnier")
        
        # load the settings from the database into the variables
        if settings[5] is not None and settings[5] != "":
            self.volume.set(value=settings[5])
            
        if settings[6] is not None and settings[6] != "" and settings[6] != 0:
            self.custom_print("settings[6]", settings[6])
            self.active_mode.set(value=settings[6])
        
        if settings[7] is not None and settings[7] != "" and settings[7] != 0:
            self.custom_print("settings[7]", settings[7])
            self.debug_mode.set(value=settings[7])
        
        if settings[8] is not None and settings[8] != "" and settings[8] != 0:
            self.start_time.set(value=settings[8])
            
        if settings[9] is not None and settings[9] != "" and settings[9] != 0:
            self.time_interval.set(value=settings[9])
            
        if settings[10] is not None and settings[10] != "" and settings[10] != 0:
            self.time_intervalFM.set(value=settings[10])
            
        if settings[11] is not None and settings[11] != "" and settings[11] != 0:
            self.time_pause_before_FM.set(value=settings[11])
            
        if settings[12] is not None and settings[12] != "" and settings[12] != 0:
            self.website_title.set(value=settings[12])
        
    
##############################################################################################
##############################################################################################
##############################################################################################

    def add_name_entry(self, entry_text="", mp3_path=""):
        team_element_width = self.screenwidth / 10
        team_element_height = self.screenheight / 30
        team_element_font_size = self.screenwidth / 150
        #self.custom_print(entry_text)
        count = len(self.name_entries) + 1
        team_id = count - 1

        # Create a label with "Team 1" and the count
        label_text = f'Team {count}'
        label = ctk.CTkLabel(self.team_entries_frame, text=label_text, font=("Helvetica", team_element_font_size * 1.2, "bold"))  # Increase font size
        label.grid(row=len(self.name_entries), column=0, padx=15, pady=5, sticky='e')
        
        # Create a new entry field
        new_entry = ctk.CTkEntry(self.team_entries_frame, font=("Helvetica", team_element_font_size), width=team_element_width, height=team_element_height)  # Increase font size
        
        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)
        
        new_entry.grid(row=len(self.name_entries), column=1, pady=5, sticky='we')
        
        new_file_dialog = ctk.CTkButton(self.team_entries_frame, text="Select mp3", command=lambda: self.save_mp3_path(new_file_dialog, team_id), width=team_element_width, height=team_element_height, font=("Helvetica", team_element_font_size), fg_color="#34757a", hover_color="#1f4346")
        new_file_dialog.grid(row=len(self.name_entries), column=2, pady=5, sticky='we', padx=12)
        
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

        #self.custom_print(file_path)
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
        old_team_ids = [row[0] for row in self.cursor.execute(get_team_ids).fetchall()]

        self.cursor.execute("SELECT mp3Path FROM teamData")
        entries = self.cursor.fetchall()
        
        existing_teams = []

        for i in enumerate(old_team_ids):
            old_mp3_list.append("")

        for i, entry in enumerate(entries):
            old_mp3_list[i] = entry

        # Drop the table
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

        total_entries = len(name_entries)
        midpoint = total_entries // 2

        new_team_data = []
        for i, entry in enumerate(name_entries):
            entry_text = entry.get().strip()

            group_number = 1 if (i < midpoint) or (total_entries % 2 != 0 and i == midpoint) else 2

            if entry_text:
                # Update existing team
                if entry_text not in existing_teams:
                    new_team_data.append((entry_text, group_number))
                    existing_teams.append(entry_text)
                else:
                    for i in range(1, 100):
                        if f"{entry_text} {i}" not in existing_teams:
                            entry_text = f"{entry_text} {i}"
                            break
                    new_team_data.append((entry_text, group_number))
                    existing_teams.append(entry_text)

        # Insert new data
        insert_query = "INSERT INTO teamData (teamName, groupNumber) VALUES (?, ?)"
        self.cursor.executemany(insert_query, new_team_data)

        # Get all ids from teamData
        self.cursor.execute("SELECT id FROM teamData")
        team_ids = [row[0] for row in self.cursor.fetchall()]

        for team_id in team_ids:
            mp3_entry = self.mp3_list.get(team_id-1, "")
            if mp3_entry.strip() == "" and old_mp3_list is not None and team_id - 1 < len(old_mp3_list) and old_mp3_list[team_id - 1] is not None:
                self.mp3_list[team_id-1] = old_mp3_list[team_id-1][0]

        set_mp3_paths = "UPDATE teamData SET mp3Path = ? WHERE id = ?"
        self.cursor.executemany(set_mp3_paths, [(mp3_path, team_id + 1) for team_id, mp3_path in self.mp3_list.items()])

        self.connection.commit()
        
        self.calculate_matches()
        self.reload_spiel_button_command()
        self.get_teams_for_final_matches()
        
    
    def write_names_into_entry_fields(self):
        selectTeams = """
        SELECT teamName, mp3Path FROM teamData
        ORDER BY id ASC
        """
        self.cursor.execute(selectTeams)
        
        allfetched = self.cursor.fetchall()
        
        if allfetched == []:
            self.add_name_entry()
        
        #self.custom_print("allfetched", allfetched)
        for teamName, mp3_path in allfetched:
            #self.custom_print("teamName", teamName)
            #self.custom_print("mp3_path", mp3_path)
            self.add_name_entry(teamName, mp3_path)
           

    def create_Team_elements(self):
        # Create elements for the Team frame
        canvas = tk.Canvas(self.Team_frame, bg="#0e1718")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ctk.CTkScrollbar(self.Team_frame, orientation='vertical', command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.team_entries_frame = ctk.CTkFrame(canvas, fg_color="#0e1718")
        canvas.create_window((0, 0), window=self.team_entries_frame, anchor="nw")
        
        name_entries = []
        self.write_names_into_entry_fields()

        self.team_entries_frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        button_width = self.screenwidth / 15
        button_height = self.screenheight / 27
        button_font_size = self.screenwidth / 120
        
        self.get_teams_for_final_matches()
        
        team_button_frame = ctk.CTkFrame(self.Team_frame, bg_color='#142324', fg_color='#142324')
        team_button_frame.pack(anchor=tk.NE, side=tk.TOP, pady=10, padx=10)

        # Button to add a new name entry
        add_button = ctk.CTkButton(team_button_frame, text="Add Name", command=self.add_name_entry, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        add_button.pack(pady=8, padx=10)

        # Button to retrieve the entered names
        submit_button = ctk.CTkButton(team_button_frame, text="Submit", command=self.save_team_names_in_db, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        submit_button.pack(pady=8, padx=10)

        reload_button = ctk.CTkButton(team_button_frame, text="Reload", command=self.reload_button_command, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        reload_button.pack(pady=8, padx=10)
        

##############################################################################################
##############################################################################################
##############################################################################################

    def create_player_elements(self):
        # Create elements for the player frame
        #player_button = tk.Button(self.player_frame, text="player Button", command=self.player_button_command)
        #player_button.pack(pady=10)
        # Create elements for the Team frame
        self.canvas = tk.Canvas(self.player_frame)
        self.canvas.pack(fill="both", expand=True, side="bottom", padx=20, pady=10)

        # Create a scrollbar and connect it to the canvas
        scrollbar = ctk.CTkScrollbar(self.player_frame, orientation='vertical', command= self.canvas.yview, height=25, fg_color="#0e1718")
        scrollbar.pack(side=tk.LEFT, fill="y")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.configure(yscrollincrement=6)

        self.frameplayer = ctk.CTkFrame(self.canvas, fg_color="#0e1718")
        self.canvas.create_window((0, 0), window=self.frameplayer, anchor="nw")
        
        self.test_frame = ctk.CTkFrame(self.player_frame, bg_color='#0e1718', fg_color='#0e1718')
        self.test_frame.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.X, padx=10, expand=True)
        
        buttons_frame = ctk.CTkFrame(self.player_frame, fg_color='#142324')
        buttons_frame.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)
        
        
        button_width = self.screenwidth / 15
        button_height = self.screenheight / 27
        button_font_size = self.screenwidth / 120
        
        # Button to add a new name entry
        add_button = ctk.CTkButton(buttons_frame, text="Add Name", command=lambda: self.add_name_entry_player(self.frameplayer, "Player"), width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        add_button.pack(pady=8, padx=10, anchor=tk.NE, side=tk.TOP)    

        # Button to retrieve the entered names
        submit_button = ctk.CTkButton(buttons_frame, text="Submit", command=self.save_names_player, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        submit_button.pack(pady=8, padx=10, anchor=tk.NE, side=tk.TOP)    

        reload_button = ctk.CTkButton(buttons_frame, text="Reload", command=self.reload_button_player_command, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
        reload_button.pack(pady=8, padx=10, anchor=tk.NE, side=tk.TOP)    
        
        self.selected_team_in_player = ""
        self.team_button_list = []
        
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        teamNames.pop(0)
        #self.custom_print("teamNames", teamNames, "team_IDs", team_IDs, "in create_player_elements")
        
        self.player_top_frame = ctk.CTkFrame(self.test_frame, width=1, height=1, fg_color="#0e1718")

        self.player_bottom_frame = ctk.CTkFrame(self.test_frame, width=1, height=1, fg_color="#0e1718")
        
        self.team_button_font_size = self.screenwidth / 150
        self.team_button_width = self.screenwidth / 15
        self.team_button_height = self.screenheight / 30
        
        self.cool_current_team_label = ctk.CTkLabel(self.test_frame, text="", font=("Helvetica", self.team_button_font_size * 1.4, "bold"), fg_color="#0e1718")

        for i, teamID in enumerate(team_IDs):
            try:
                teamName = teamNames[int(teamID-1)]
            except:
                self.custom_print("teamID", teamID)
                self.custom_print("teamNames", teamNames)
                self.custom_print("team_IDs", team_IDs)
                self.custom_print("i", i)

            if i < 8:
                #self.custom_print("created button in upper frame")
                team_button = ctk.CTkButton(
                    self.player_top_frame,
                    text=teamName,
                    command=lambda id=teamID, text=teamName, i2=i: self.select_team(id, self.team_button_list, i2, text),
                    width=self.team_button_width,
                    fg_color="#34757a",
                    hover_color="#1f4346",
                    font=("Helvetica", self.team_button_font_size),
                    height=self.team_button_height,
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            else:
                team_button = ctk.CTkButton(
                    self.player_bottom_frame,
                    text=teamName,
                    command=lambda id=teamID, text=teamName, i2=i: self.select_team(id, self.team_button_list, i2, text),
                    width=self.team_button_width,
                    fg_color="#34757a",
                    hover_color="#1f4346",
                    font=("Helvetica", self.team_button_font_size),
                    height=self.team_button_height,
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            self.team_button_list.append(team_button)
            
        self.player_top_frame.pack(anchor=tk.NW, side=tk.TOP, pady=5, padx=5)
        self.player_bottom_frame.pack(anchor=tk.NW, side=tk.TOP, pady=5, padx=5)
        self.cool_current_team_label.pack(anchor=tk.NW, side=tk.BOTTOM, pady=5, padx=5)

        
    def save_names_player(self, team_id=-1):
        entries = self.variable_dict.get(f"entries{self.frameplayer}")
        entries2 = self.variable_dict.get(f"entries2{self.frameplayer}")
        entries3 = self.variable_dict.get(f"entries3{self.frameplayer}")

        if team_id == -1:
            team_id = self.selected_team_in_player
            
        # Fetch existing player names
        self.cursor.execute("SELECT playerName FROM playerData")
        existing_players = [row[0] for row in self.cursor.fetchall()]

        # Delete all entries related to the specified team ID
        self.cursor.execute("DELETE FROM playerData WHERE teamId = ?", (team_id,))

        if entries:
            # Iterate through the current entries and insert
            for entry, entrie2, entrie3 in zip(entries, entries2, entries3):
                entry_text = str(entry.get())
                entry_text2 = str(entrie2.get())
                entry_text3 = str(entrie3.get())

                if entry_text:
                    # Add new player
                    try:
                        insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                        self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))
                    except sqlite3.IntegrityError:
                        for i in range(1, 100):
                            if f"{entry_text} {i}" not in existing_players:
                                entry_text = f"{entry_text} {i}"
                                existing_players.append(entry_text)
                                break
                        insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                        self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))

            self.connection.commit()

    
    def add_name_entry_player(self, Frame, Counter, entry_text="", entry_text2="", entry_text3=""):
        if self.selected_team_in_player == "":
            return
        
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

        label_font_size = self.screenwidth / 150
        entry_width = self.screenwidth / 10
        entry_height = self.screenheight / 30
        # Create a label with "Team 1" and the count
        label_text = f'{Counter} {count}'
        label = ctk.CTkLabel(Frame, text=label_text, font=("Helvetica", label_font_size * 1.2, "bold"))
        label.grid(row=len(self.variable_dict[varentrie1name]), column=0, padx=10, pady=8, sticky='e')

        # Create a new entry field
        new_entry = ctk.CTkEntry(Frame, font=("Helvetica", label_font_size), height=entry_height, width=entry_width)
        
        new_entry2 = ctk.CTkEntry(Frame, font=("Helvetica", label_font_size), height=entry_height, width=entry_width)
        
        new_entry3 = ctk.CTkEntry(Frame, font=("Helvetica", label_font_size), height=entry_height, width=entry_width)
        #self.custom_print("entry_text", entry_text)
        #self.custom_print("new_entry")

        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)
            
        if entry_text2:
            new_entry2.insert(0, entry_text2)
            
        if entry_text3:
            new_entry3.insert(0, entry_text3)
        else:
            new_entry3.insert(0, "0")
        
        

        new_entry.grid(row=len(self.variable_dict[varentrie1name]), column=1, pady=5, sticky='we', padx=3)
        new_entry2.grid(row=len(self.variable_dict[varentrie1name]), column=2, pady=5, sticky='we', padx=3)
        new_entry3.grid(row=len(self.variable_dict[varentrie1name]), column=3, pady=5, sticky='we', padx=3)
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
        
        self.selected_team_in_player = ""
        self.team_button_list = []
        
        self.cool_current_team_label.configure(text="")
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        teamNames.pop(0)
        #self.custom_print("teamNames", teamNames, "team_IDs", team_IDs)
        
        for i, teamID in enumerate(team_IDs):
            teamName = teamNames[int(teamID-1)]

            if i < 8:
                team_button = ctk.CTkButton(
                    self.player_top_frame,
                    text=teamName,
                    command=lambda id=teamID, text=teamName, i2=i: self.select_team(id, self.team_button_list, i2, text),
                    width=self.team_button_width,
                    fg_color="#34757a",
                    hover_color="#1f4346",
                    font=("Helvetica", self.team_button_font_size),
                    height=self.team_button_height,
                )
                team_button.pack(pady=5, padx=5, anchor=tk.N, side=tk.LEFT)

            else:
                team_button = ctk.CTkButton(
                    self.player_bottom_frame,
                    text=teamName,
                    command=lambda id=teamID, text=teamName, i2=i: self.select_team(id, self.team_button_list, i2, text),
                    width=self.team_button_width,
                    fg_color="#34757a",
                    hover_color="#1f4346",
                    font=("Helvetica", self.team_button_font_size),
                    height=self.team_button_height,
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
    
        self.selected_team_in_player = ""
        self.variable_dict[varcountname] = 0
    
    
    def select_team(self, teamID, team_button_list, index, teamName=""):
        
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
        
        self.selected_team_in_player = teamID
        
        self.variable_dict[varcountname] = 0
        self.variable_dict[varentrie1name] = []
        self.variable_dict[varentrie2name] = []
        self.variable_dict[varentrie3name] = []
        self.variable_dict[varlabelname] = []
        
        #print("teamName", teamName)
        
        self.cool_current_team_label.configure(text=str(teamName))
        #print("teamName", teamName)
        
        self.cool_current_team_label.configure(text=str(teamName))
        
        self.write_names_into_entry_fields_players(teamID, "Player", self.frameplayer)
          
            
    def read_player_stats(self, teamID, readGoals=False, readID=False, playerID=-1):
        output = []

        if readID and playerID != -1:
            raise ValueError("readID and playerID cannot be True at the same time")

        # Determine the columns to select based on readGoals and readID
        columns = "playerName, playerNumber, goals" if readGoals else "playerName, playerNumber"
        columns =  columns + ", id" if readID else columns
        
        print("columns", columns)

        # Determine the condition based on playerID
        condition = "AND id = ?" if playerID != -1 else ""

        # Construct the SQL query
        getData = f"""
        SELECT {columns} FROM playerData
        WHERE teamId = ? {condition}
        ORDER BY id ASC
        """

        # Execute the query with the appropriate parameters
        params = (teamID, playerID) if playerID != -1 else (teamID,)
        self.cursor.execute(getData, params)

        # Fetch all rows and append to output
        output = [row for row in self.cursor.fetchall()]

        return output
            
            
    def read_teamNames(self, teams_to_read=-1):
        teamNames = [""]
        
        #if self.active_mode.get() == 1 or True:
        
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
                        #self.custom_print(result)
                        teamNames.append(result[0])
        
        else:
            selectTeams = """
            SELECT teamName FROM teamData
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeams)
        
            for team in self.cursor.fetchall():
                teamNames.append(team[0])
            #self.custom_print("teamNames", teamNames)
        #elif self.active_mode.get() == 2:
        #    teamNames.append(self.endteam1[1])
        #    teamNames.append(self.endteam2[1])
        #    teamNames.append(self.endteam3[1])
        #    teamNames.append(self.endteam4[1])
            
        
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
        
        button_width = self.screenwidth / 15
        button_height = self.screenheight / 27
        button_font_size = self.screenwidth / 120
        
        # Create elements for the SPIEL frame
        manual_frame = ctk.CTkFrame(self.SPIEL_frame, bg_color='#0e1718', fg_color='#0e1718')
        manual_frame.pack(pady=5, anchor=tk.S, side=tk.BOTTOM, padx=5, fill=tk.X)
        
        manual_manual_frame = ctk.CTkFrame(manual_frame, fg_color='#142324', corner_radius=5)
        manual_manual_frame.pack(anchor=tk.SE, side=tk.RIGHT, padx=10, pady=10, expand=True)
        
        SPIEL_button = ctk.CTkButton(manual_manual_frame, text="Reload", command=lambda : self.reload_spiel_button_command(True), width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")            
        SPIEL_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.S, padx=10) 
        
        
        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}
        
        self.get_teams_for_final_matches()

        self.custom_print("self.teams_playing", self.teams_playing)
        
        for i, _ in enumerate(self.teams_playing):
            
            self.custom_print("kakarcsh",self.teams_playing)
            
            team_names = self.read_teamNames()
            if self.teams_playing[i] is not None:
                self.custom_print("i" , i, "teamnames", team_names)
                #self.custom_print(self.teams_playing[i])
                #try:
                team_name = team_names[self.teams_playing[i]]
                #except IndexError:
                #    self.teams_playing = [None, None]
                #    self.custom_print("IndexError in create_SPIEL_elements")
                #    self.create_SPIEL_elements()
                #    return
                
            else:
                # Handle the case when self.teams_playing[i + 1] is None
                # For example, you can set team_name to an empty string
                break
                
            team_id = self.teams_playing[i]
            
            if i == 0:
                team2_id = self.teams_playing[1]
            else:
                team2_id = self.teams_playing[0]

            
            #self.custom_print(team)
            
            # Initialize the dictionary for the current team
            self.spiel_buttons[team_id] = {}
                    
            self.for_team_frame = ctk.CTkFrame(self.SPIEL_frame, bg_color='#0e1718', fg_color='#0e1718')
            self.for_team_frame.pack(pady=10, anchor=tk.NW, side=tk.TOP, fill="both", padx=10, expand=True)
            
            #self.for_team_frame.tk_setPalette(
            #    background='#0e1718', 
            #    bg_color='#0e1718', 
            #    fg_color='#0e1718',
            #    activeBackground='#0e1718', 
            #    activeForeground='#0e1718', 
            #    foreground='#0e1718'
            #    )
            
            #self.for_team_frame.configure(bg_color="#0e1718")
            
            # Create global scores buttons, one for up and one for down
            score_button_frame = ctk.CTkFrame(self.for_team_frame, bg_color='#142324', fg_color='#142324')
            score_button_frame.pack(pady=10, anchor=tk.E, side=tk.RIGHT, padx=10)
            
            score_button_up = ctk.CTkButton(score_button_frame, text="UP", command=lambda team=team_id, team2=team2_id: self.global_scored_a_point(team, team2, "UP"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
            score_button_up.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_label_var = tk.StringVar()
            #self.custom_print("team_id", team_id, "team2_id", team2_id)
            score_label_var.set(self.read_goals_for_match_from_db(team_id, team2_id))
            
            score_label = ctk.CTkLabel(score_button_frame, text="None", textvariable=score_label_var, font=("Helvetica", self.team_button_font_size * 1.7, "bold"))
            score_label.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_button_down = ctk.CTkButton(score_button_frame, text="DOWN", command=lambda team=team_id, team2=team2_id: self.global_scored_a_point(team, team2, "DOWN"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
            score_button_down.pack(pady=2, anchor=tk.N, side=tk.BOTTOM, expand=True, fill=tk.X)
            
            self.team_label = ctk.CTkLabel(self.for_team_frame, text=team_name, font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.team_label.pack(side=tk.LEFT, pady=2, anchor=tk.NW)
            
            self.spiel_buttons[team_id]["global"] = (self.for_team_frame, self.team_label, score_button_up, score_label_var, score_button_down)
            
            frame_frame = ctk.CTkFrame(self.for_team_frame, bg_color='#0e1718', fg_color='#0e1718')
            frame_frame.pack(side=tk.TOP, pady=0, anchor=tk.N)

            up_frame = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
            up_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

            down_frame = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
            down_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
            

            for i, (player_name, player_number, goals, player_id) in enumerate(self.read_player_stats(team_id, True, True)):  
                print("player_name", player_name, "player_number", player_number, "goals", goals, "player_id", player_id)
                #self.custom_print(type(player_name), player_name)
                player_index = i 
                #player_id = self.get_player_id_from_player_name(player_name)
                print("player_id", self.get_player_id_from_player_name(player_name))
                if i < 8:
                    self.group_frame = ctk.CTkFrame(up_frame, fg_color='#142324', corner_radius=10)
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
                else:
                    self.group_frame = ctk.CTkFrame(down_frame, fg_color='#142324', corner_radius=10)
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
                
                #self.group_frame = tk.Frame(self.for_team_frame, background="lightcoral")
                #self.group_frame.pack(side=tk.LEFT, padx=10, pady=10)

                playertext1 = ctk.CTkLabel(self.group_frame, text=f"Player {i}", font=("Helvetica", self.team_button_font_size))
                playertext1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
                
                playertext2_text = f"{player_name} - {player_number}"
                
                playertext2 = ctk.CTkLabel(master=self.group_frame, text=playertext2_text , font=("Helvetica", self.team_button_font_size, "bold"))
                playertext2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
                
                playertext3 = ctk.CTkLabel(self.group_frame, text=f"Tore {str(goals)}", font=("Helvetica", self.team_button_font_size))
                playertext3.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)

                playerbutton1 = ctk.CTkButton(self.group_frame, text="UP", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index,  "UP"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size), height=self.team_button_height, width=self.team_button_width)  
                playerbutton1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
                
                playerbutton2 = ctk.CTkButton(self.group_frame, text="DOWN", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index, "DOWN"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size), height=self.team_button_height, width=self.team_button_width)
                playerbutton2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
                
                
                #self.custom_print("team", team, "i", i)

                # Save the group_frame, playertext1, and playerbutton in each for loop with the team name as key
                self.spiel_buttons[team_id][i] = (self.group_frame, playertext1, playertext2, playertext3, playerbutton1, playerbutton2)  # Use append for a list
                
                #self.spiel_buttons[team] = (playerbutton)  # Use append for a list

        teams_list = self.read_teamNames()
        teams_list.pop(0)
        #self.custom_print("teams_list", teams_list)

        self.manual_team_select_1 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", self.team_button_font_size), 
            state=tk.DISABLED, 
            command=lambda event: self.on_team_select(event, nr=1),
            )
        self.manual_team_select_1.set("None")
        self.manual_team_select_1.pack(pady=10, side=tk.BOTTOM, anchor=tk.S, padx=10)
        #self.manual_team_select_1.bind("<<ComboboxSelected>>", lambda event, nr=1: self.on_team_select(event, nr))
        
        self.manual_team_select_2 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", self.team_button_font_size), 
            state=tk.NORMAL, 
            command=lambda event: self.on_team_select(event, nr=0),
            )
        self.manual_team_select_2.set("None")
        self.manual_team_select_2.pack(pady=10, side=tk.BOTTOM, anchor=tk.S, padx=10)
        #self.manual_team_select_2.bind("<<ComboboxSelected>>", lambda event, nr=0: self.on_team_select(event, nr))
        
        if self.teams_playing.count(None) == 0:
        
            ######################################################
            #Time Display
            #print(f"Time Display, here are the teams: {self.teams_playing} and the active_match: {self.active_match}")
            # Create a new frame
            time_frame = ctk.CTkFrame(manual_frame, fg_color='#142324', corner_radius=5)
            time_frame.pack(anchor=tk.SE, side=tk.RIGHT, padx=10, pady=10, expand=True)
            
            # Create a new frame for the first row
            time_frame1 = ctk.CTkFrame(time_frame, fg_color='#142324', corner_radius=5)
            time_frame1.pack(anchor=tk.S, side=tk.TOP, padx=10, pady=10, expand=True, fill=tk.X)

            time_current_match, time_next_match = self.get_time_for_current_match(True)

            time_label = ctk.CTkLabel(time_frame1, text=f"Current Match Start: ", font=("Helvetica", self.team_button_font_size * 1.5))
            time_label.pack(side=tk.LEFT, pady=5, padx=10)

            current_time_label = ctk.CTkLabel(time_frame1, text=f"{time_current_match}", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            current_time_label.pack(side=tk.RIGHT, pady=5, fill=tk.X, padx=10)

            # Create a new frame for the second row
            time_frame2 = ctk.CTkFrame(time_frame, fg_color='#142324', corner_radius=5)
            time_frame2.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=10, expand=True, fill=tk.X)

            time_label2 = ctk.CTkLabel(time_frame2, text=f"Next Match Start: ", font=("Helvetica", self.team_button_font_size * 1.5))
            time_label2.pack(side=tk.LEFT, pady=5, padx=10, anchor=tk.S)

            next_time_label = ctk.CTkLabel(time_frame2, text=f"{time_next_match}", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            next_time_label.pack(side=tk.RIGHT, pady=5, padx=10, anchor=tk.SE)
            
            self.delay_label = ctk.CTkLabel(time_frame2, text=f"Delay: ", font=("Helvetica", self.team_button_font_size * 1.5))
            self.delay_label.pack(side=tk.RIGHT, pady=5, padx=10, anchor=tk.SE)
            
            self.delay_time_label = ctk.CTkLabel(time_frame2, text=f"0", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.delay_time_label.pack(side=tk.RIGHT, pady=5, padx=10, anchor=tk.SE)
            
            self.watch_dog_process()
            
            ######################################################

        self.create_matches_labels(manual_frame)


        none_count = self.teams_playing.count(None)
        team_names = self.read_teamNames()

        if none_count == 0 and self.teams_playing:
            self.configure_team_select(self.manual_team_select_2, tk.NORMAL, team_names[self.teams_playing[0]])
            self.configure_team_select(self.manual_team_select_1, tk.NORMAL, team_names[self.teams_playing[1]])
        elif none_count == 2:
            self.configure_team_select(self.manual_team_select_1, tk.DISABLED, "None")
        elif none_count == 1:
            self.configure_team_select(self.manual_team_select_1, tk.NORMAL, "None")
            self.configure_team_select(self.manual_team_select_2, tk.NORMAL, team_names[self.teams_playing[0]])    

    
    def configure_team_select(self, team_select, state, team_name):
        team_select.configure(state=state)
        team_select.set(team_name)
    
    
    def watch_dog_process(self):
        # this process is for updating the self.delay_time_label every second and if the delay is over 0, 
        # it will decrease the delay by 1 and make the self.delay_time_label red and if it is not over 0, 
        # it will make the self.delay_time_label default again 

        # Get the current delay time
        if self.teams_playing.count(None) == 0:
            
            delay_time = self.calculate_delay()

            # If the delay time is over 0
            if delay_time < 0:
                # Decrease the delay time by 1
                delay_time -= 1

                # Format the delay time as 'Min:Sec'
                delay_min, delay_sec = divmod(delay_time, 60)
                delay_time_str = f"{int(delay_min):02d}:{int(delay_sec):02d}"

                # Update the delay time label text
                self.delay_time_label.configure(text=delay_time_str)

                # Change the delay time label color to red
                self.delay_time_label.configure(fg_color="red")
            else:
                delay_time -= 1

                # Format the delay time as 'Min:Sec'
                delay_min, delay_sec = divmod(delay_time, 60)
                delay_time_str = f"{int(delay_min):02d}:{int(delay_sec):02d}"

                # Update the delay time label text
                self.delay_time_label.configure(text=delay_time_str)
                # If the delay time is not over 0, change the delay time label color to default (black)
                self.delay_time_label.configure(fg_color="black")

            # Call this function again after 1 second (1000 milliseconds)
            self.delay_time_label.after(1000, self.watch_dog_process)


    def calculate_delay(self):
        # Get the current time
        current_time = datetime.datetime.now()

        # Get the start time for the next match
        _, next_match_start_time_str = self.get_time_for_current_match(True)
        next_match_start_time = datetime.datetime.strptime(next_match_start_time_str, '%H:%M')

        # Make sure both times are on the same date
        next_match_start_time = next_match_start_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)

        # Calculate the delay in seconds
        delay = (next_match_start_time - current_time).total_seconds()

        # If the delay is negative, that means the next match has already started, so we set the delay to 0
        return delay


    def get_time_for_current_match(self, next_match=False):
        #get the number of entrys in the matchData table
        self.cursor.execute("SELECT COUNT(*) FROM matchData")
        match_count = self.cursor.fetchone()[0]
        
        if self.active_mode.get() == 1:
            # Get the starttime from settings
            starttime_str = str(self.start_time.get())
            starttime = datetime.datetime.strptime(starttime_str, '%H:%M')

            # get the number of the active match
            active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1]) - 1

            # get the time interval from settings
            timeinterval = int(self.time_interval.get().replace("m", ""))

            # calculate the time for the current match
            current_match_time = starttime + datetime.timedelta(minutes=timeinterval * active_match)

            if next_match and active_match <= match_count:
                return current_match_time.strftime('%H:%M'), (current_match_time + datetime.timedelta(minutes=timeinterval)).strftime('%H:%M')
            # return the time in 00:00 format
            return current_match_time.strftime('%H:%M')      
        
        elif self.active_mode.get() == 2:
            # Get the starttime from settings
            starttime_str = str(self.start_time.get())
            starttime = datetime.datetime.strptime(starttime_str, '%H:%M')

            # get the number of the active match
            active_match = self.active_match

            # get the time interval from settings
            timeinterval = int(self.time_interval.get().replace("m", ""))
            
            time_interval_final_matches = int(self.time_intervalFM.get().replace("m", ""))
            
            # get time pause final matches
            pause_between_final_matches = int(self.time_pause_before_FM.get().replace("m", ""))
            
            #print(f"active_match: {active_match}, time_interval_final_matches: {time_interval_final_matches}, timeinterval: {timeinterval}, match_count: {match_count}, pause_between_final_matches: {pause_between_final_matches}")

            # calculate the time for the current match
            current_match_time = starttime + datetime.timedelta(minutes=(time_interval_final_matches * active_match) + (timeinterval * match_count) + pause_between_final_matches)

            if next_match:
                return current_match_time.strftime('%H:%M'), (current_match_time + datetime.timedelta(minutes=timeinterval)).strftime('%H:%M')
            # return the time in 00:00 format
            return current_match_time.strftime('%H:%M')
        
    
    def on_team_select(self, event, nr):
        #self.custom_print("on_team_select")
        #self.custom_print(event)
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
            if self.active_mode.get() == 1:
                self.active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1]) - 1
        
        #self.custom_print("self.teams_playing", self.teams_playing)
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
    
    
    def reload_spiel_button_command(self, show_frame=False):
        
        self.calculate_points()
                
        # Delete all entry fields
        self.SPIEL_frame.grid_forget()
        self.SPIEL_frame.pack_forget()
        self.SPIEL_frame.destroy()
    
        
        self.SPIEL_frame = ctk.CTkFrame(self, fg_color='#0e1718', bg_color='#0e1718')
        
        if show_frame:
            self.show_frame(self.SPIEL_frame)

        self.create_SPIEL_elements()

        
    def player_scored_a_point(self, teamID, player_id, player_index, direction="UP"):
        # Get the current score
        current_goals = self.read_player_stats(teamID, True, False, player_id)[0][2]
        
        # Update the score
        if direction == "UP":
            current_goals += 1
        else:
            current_goals -= 1

        if current_goals < 0:
            current_goals = 0
            return
        
        # Update the score label
        self.spiel_buttons[teamID][player_index][3].configure(text=f"Tore {current_goals}")
        self.update_idletasks()
        
        # Update the database
        self.cursor.execute(
            "UPDATE playerData SET goals = ? WHERE teamId = ? AND id = ?",
            (current_goals, teamID, player_id)
        )
        
        # Commit the changes to the database
        self.connection.commit()
    
    
    def create_matches_labels(self, frame):
        
        matches = self.calculate_matches()
        
        spiel_select_frame = ctk.CTkFrame(frame, fg_color='#142324', corner_radius=5)
        spiel_select_frame.pack(pady=10, padx=10, anchor=tk.SW, side=tk.LEFT)
        
        width = self.screenwidth / 9
        
        spiel_select = ctk.CTkComboBox(spiel_select_frame, font=("Helvetica", self.team_button_font_size * 1.2), width=width, values=[""], command=lambda event: self.on_match_select(event, matches))
        spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N, padx=10)

        if self.active_mode.get() == 1:
            values_list = self.get_values_list_mode1(matches)
            spiel_select.configure(values=values_list)
            #print("active_match in create_matches_labels", self.active_match)
            if self.active_match >= 0:
                spiel_select.set(values_list[self.active_match])
        elif self.active_mode.get() == 2:
            values_list, active_match = self.get_values_list_mode2()
            spiel_select.configure(values=values_list)
            if active_match >= 0:
                spiel_select.set(values_list[active_match])

            
        next_match_button = ctk.CTkButton(spiel_select_frame, text="Next Match", command=lambda : self.next_previous_match_button(spiel_select, matches), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
        next_match_button.pack(pady=10, padx=10, side=tk.RIGHT, anchor=tk.SE)
        previous_match_button = ctk.CTkButton(spiel_select_frame, text="Previous Match", command=lambda : self.next_previous_match_button(spiel_select, matches, False), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
        previous_match_button.pack(pady=10, padx=10, side=tk.LEFT, anchor=tk.SW)

    
    def get_values_list_mode1(self, matches):
        values_list = []
        for match in matches:
            values_list.append(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])
        return values_list


    def get_active_match(self, team1, team2):
        #get the active match by looking in the matches databesa and where these teams play together you get the match number
        getActiveMatch = """
        SELECT matchId FROM matchData
        WHERE team1Id = ? AND team2Id = ?
        """
        self.cursor.execute(getActiveMatch, (team1, team2))
        active_match = self.cursor.fetchone()
        if active_match != None:
            return active_match[0]
        else:
            return -1


    def get_values_list_mode2(self):
        values_list = []
        self.get_teams_for_final_matches()
        values_list.append(f"Spiel 1 Halb: {self.endteam1[1]} vs {self.endteam3[1]}")
        values_list.append(f"Spiel 2 Halb: {self.endteam2[1]} vs {self.endteam4[1]}")
        values_list.append(self.get_spiel_um_platz_3(self.endteam1, self.endteam3, self.endteam2, self.endteam4))
        values_list.append(self.get_final_match(self.endteam1, self.endteam3, self.endteam2, self.endteam4))
        
        active_match = self.active_match
        if self.spiel_um_platz_3 != None and self.final_match_teams != None and self.spiel_um_platz_3 != [] and self.final_match_teams != []:
            self.active_match = 0
            self.save_active_match_in_final_phase(self.endteam1[0], self.endteam3[0])   
            self.active_match = 1
            self.save_active_match_in_final_phase(self.endteam2[0], self.endteam4[0])
            self.active_match = 2
            self.save_active_match_in_final_phase(self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0])
            self.active_match = 3
            self.save_active_match_in_final_phase(self.final_match_teams[0][0], self.final_match_teams[1][0])
        self.active_match = active_match
        
        goles_spiele = []
        
        if self.spiel_um_platz_3 != None and self.final_match_teams != None and self.spiel_um_platz_3 != [] and self.final_match_teams != []:
            goles_spiele.append([self.read_goals_for_match_from_db(self.endteam1[0], self.endteam3[0]), self.read_goals_for_match_from_db(self.endteam3[0], self.endteam1[0])])
            goles_spiele.append([self.read_goals_for_match_from_db(self.endteam2[0], self.endteam4[0]), self.read_goals_for_match_from_db(self.endteam4[0], self.endteam2[0])])
            goles_spiele.append([self.read_goals_for_match_from_db(self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0]), self.read_goals_for_match_from_db(self.spiel_um_platz_3[1][0], self.spiel_um_platz_3[0][0])])
            goles_spiele.append([self.read_goals_for_match_from_db(self.final_match_teams[0][0], self.final_match_teams[1][0]), self.read_goals_for_match_from_db(self.final_match_teams[1][0], self.final_match_teams[0][0])])

            if self.active_mode.get() == 2:
                self.updated_data.update({"finalMatches": [[self.endteam1[1], self.endteam3[1], goles_spiele[0]], [self.endteam2[1], self.endteam4[1], goles_spiele[1]], [self.spiel_um_platz_3[0][1], self.spiel_um_platz_3[1][1], goles_spiele[2]], [self.final_match_teams[0][1], self.final_match_teams[1][1], goles_spiele[3]]]})
            else:
                #only send nones in the same structure
                self.updated_data.update({"finalMatches": [[None, None, [None, None]], [None, None, [None, None]], [None, None, [None, None]], [None, None, [None, None]]]})
        return values_list, self.active_match
    
    
    def get_teams_for_final_matches(self):
        #get the best two teams from the database(with most points)
        getTeams = """
        SELECT id, teamName FROM teamData
        WHERE groupNumber = 1
        ORDER BY points DESC
        LIMIT 2
        """
        self.cursor.execute(getTeams)
        
        #get the two best teams
        teams1 = self.cursor.fetchall()
        #self.custom_print("teams1", teams1)
        
        getTeams2 = """
        SELECT id, teamName FROM teamData
        WHERE groupNumber = 2
        ORDER BY points DESC
        LIMIT 2 
        """
        self.cursor.execute(getTeams2)
        
        #get the two best teams
        teams2 = self.cursor.fetchall()
        
        values_list = []
        
        if teams1 != [] and teams2 != []:
        
            self.endteam1 = teams1[0]
            self.endteam2 = teams1[1]
            self.endteam3 = teams2[0]
            self.endteam4 = teams2[1]
        

    def get_spiel_um_platz_3(self, team1, team2, team3, team4):
        #get the best two teams from the database(with most points)
        getGoles1 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 1
        """
        
        getGoles2 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 2
        """
        self.cursor.execute(getGoles1)
        goles1 = self.cursor.fetchone()
        self.cursor.execute(getGoles2)
        goles2 = self.cursor.fetchone()
        
        self.spiel_um_platz_3 = []
        
        if goles1 != None and goles2 != None:

            if goles1[0] < goles1[1]:
                self.spiel_um_platz_3.append(team1)
            else:
                self.spiel_um_platz_3.append(team2)
                
            if goles2[0] < goles2[1]:
                self.spiel_um_platz_3.append(team3)
            else:
                self.spiel_um_platz_3.append(team4)
        
        #self.custom_print everything
        self.custom_print("self.spiel_um_platz_3", self.spiel_um_platz_3, "team1", team1, "team2", team2, "team3", team3, "team4", team4, "goles1", goles1, "goles2", goles2)
        
        if self.spiel_um_platz_3 != []:
            return f"Spiel um Platz 3: {self.spiel_um_platz_3[0][1]} vs {self.spiel_um_platz_3[1][1]}"
        else:
            return "Spiel um Platz 3: None vs None"
        
    
    def get_final_match(self, team1, team2, team3, team4):
        #get the best two teams from the database(with most points)
        getGoles1 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 1
        """
        
        getGoles2 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 2
        """
        
        self.final_match_teams = []
        
        self.cursor.execute(getGoles1)
        goles1 = self.cursor.fetchone()
        self.cursor.execute(getGoles2)
        goles2 = self.cursor.fetchone()
        
        if goles1 != None and goles2 != None:

            if goles1[0] > goles1[1]:
                self.final_match_teams.append(team1)
            else:
                self.final_match_teams.append(team2)
                
            if goles2[0] > goles2[1]:
                self.final_match_teams.append(team3)
            else:
                self.final_match_teams.append(team4)
            
        if self.final_match_teams != []:
            return f"Finale: {self.final_match_teams[0][1]} vs {self.final_match_teams[1][1]}"
        else:
            return "Finale: None vs None"
    
           
    def save_active_match_in_final_phase(self, team1id, team2id):
        
        self.custom_print("ichkanneinfachnurnochmehr self.custom_printen", "team1id", team1id, "team2id", team2id, "self.active_match", self.active_match)
        active_match_id = self.active_match + 1

        # Try to insert a new row
        insertActiveMatch = """
        INSERT OR IGNORE INTO finalMatchesData (matchId, team1Id, team2Id)
        VALUES (?, ?, ?)
        """
        self.cursor.execute(insertActiveMatch, (active_match_id, team1id, team2id))

        # If insertion failed due to a unique constraint, update the existing row
        updateActiveMatch = """
        UPDATE finalMatchesData
        SET team1Id = ?, team2Id = ?
        WHERE matchId = ?
        """
        self.cursor.execute(updateActiveMatch, (team1id, team2id, active_match_id))

        self.connection.commit()
        
    
    def on_match_select(self, event, matches):
        selected_match = event
        self.custom_print("on_match_select", "selected_match", selected_match, "matches", matches)
        #self.custom_print(selected_match)
        #self.custom_print(matches)
        if self.active_mode.get() == 1:
            match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(selected_match)
            #self.custom_print("match_index", match_index)
            # Get the teams playing in the selected match and if there are none, set teams_playing to None
            team_names = self.read_teamNames()
            
            team1_index = team_names.index(matches[match_index]["teams"][0])
            team2_index = team_names.index(matches[match_index]["teams"][1])

            if team1_index and team2_index:
                self.teams_playing = [team1_index, team2_index]
            else:
                self.teams_playing = [None, None]
                
            self.active_match = match_index
            #print("self.active_match###################################", self.active_match)
            #self.custom_print("self.active_matchon_match_select", self.active_match)
            
            self.save_games_played_in_db(match_index)
            
            self.updated_data.update({"Games": get_data_for_website(2)})
            self.updated_data.update({"activeMatchNumber": self.active_match})
            
        elif self.active_mode.get() == 2:
            #self.custom_print("self.spiel_um_platz_3", self.spiel_um_platz_3)
            #self.custom_print("self.final_match_teams", self.final_match_teams)
            if selected_match == "Spiel 1 Halb: " + self.endteam1[1] + " vs " + self.endteam3[1]:
                self.teams_playing = [self.endteam1[0], self.endteam3[0]]
                self.active_match = 0
                self.save_active_match_in_final_phase(self.endteam1[0], self.endteam3[0])
            elif selected_match == "Spiel 2 Halb: " + self.endteam2[1] + " vs " + self.endteam4[1]:
                self.teams_playing = [self.endteam2[0], self.endteam4[0]]
                self.active_match = 1 
                self.save_active_match_in_final_phase(self.endteam2[0], self.endteam4[0])
            elif selected_match == self.get_spiel_um_platz_3(self.endteam1, self.endteam3, self.endteam2, self.endteam4) and self.spiel_um_platz_3 != []:
                if self.spiel_um_platz_3[0][0] != None and self.spiel_um_platz_3[1][0] != None:
                    self.teams_playing = [self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0]]
                    self.active_match = 2
                    self.save_active_match_in_final_phase(self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0])
                else:
                    self.teams_playing = [None, None]
                    self.active_match = 2
                    self.save_active_match_in_final_phase(None, None)
                
            elif selected_match == self.get_final_match(self.endteam1, self.endteam3, self.endteam2, self.endteam4):
                if self.final_match_teams == []:
                    self.teams_playing = [None, None]
                    self.active_match = 3
                    self.save_active_match_in_final_phase(None, None)
                
                elif self.final_match_teams[0][0] != None and self.final_match_teams[1][0] != None:
                    self.teams_playing = [self.final_match_teams[0][0], self.final_match_teams[1][0]]
                    self.active_match = 3
                    self.save_active_match_in_final_phase(self.final_match_teams[0][0], self.final_match_teams[1][0])
                    
            else:
                self.teams_playing = [None, None]
                self.active_match = -1
            #self.custom_print("self.active_matchon_match_select", self.active_match)
            
            #self.save_games_played_in_db(self.active_match)
            
            self.updated_data.update({"Games": get_data_for_website(2)})
            self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
        
        self.reload_spiel_button_command()
        
        self.show_frame(self.SPIEL_frame)
        
    
    def next_previous_match_button(self, spiel_select, matches, next_match=True):
        if self.active_mode.get() == 1:
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
                
                self.active_match = new_match_index - 1

                # Update the buttons
                self.teams_playing = teams_playing
                self.reload_spiel_button_command()
                self.show_frame(self.SPIEL_frame)
                
                self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
                self.updated_data.update({"Games": get_data_for_website(2)})
                

                # Print statements
                print("current_match_index:", current_match_index)
                print("new_match_index:", new_match_index)
                print("teams_playing:", teams_playing)
                

            except ValueError:
                # Handle the case where the selected match is not found in the list
                print("Selected match not found in the list.")
        elif self.active_mode.get() == 2:
            if next_match:
                self.active_match += 1
            else:
                self.active_match -= 1
            self.reload_spiel_button_command()
            self.show_frame(self.SPIEL_frame)
            
            self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
            
            #self.custom_print("self.active_match", self.active_match)
            
            #self.save_games_played_in_db(self.active_match)
            
            self.updated_data.update({"Games": get_data_for_website(2)})


    def global_scored_a_point(self, teamID, team2ID, direction="UP"):
        # Get the current score
        self.custom_print("global_scored_a_point", "teamID", teamID, "team2ID", team2ID, "direction", direction)
        current_score = self.read_goals_for_match_from_db(teamID, team2ID)
        old_goals = current_score
        
        # Update the score
        if direction == "UP" and current_score != "None":
            current_score += 1
            self.play_mp3(self.read_mp3_path_from_db_for_team(teamID))
            
        elif direction == "DOWN" and current_score != "None":
            current_score -= 1
        
        if current_score < 0:
            current_score = 0
            return
            
        # Write the score into the database
        
        if self.write_score_for_team_into_db(teamID, team2ID, old_goals, direction):
            # Update the score label
            self.spiel_buttons[teamID]["global"][3].set(str(current_score))
            self.updated_data.update({"Goals": get_data_for_website(1)})
            self.updated_data.update({"Matches": get_data_for_website(4)})
    
    
    def read_mp3_path_from_db_for_team(self, teamID):
        selectPath = """
        SELECT mp3Path FROM teamData
        WHERE id = ?
        """
        self.cursor.execute(selectPath, (teamID,))
        
        mp3Path = self.cursor.fetchone()[0]
        
        return mp3Path or ""
       
        
    def write_score_for_team_into_db(self, teamID, team2ID, goals, direction="UP"):
        
        if goals == "None":
            return False

        goals += 1 if direction == "UP" else -1

        self.save_goals_for_match_in_db(teamID, team2ID, goals)
        
        if self.active_mode.get() == 1:
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
        table_name = 'matchData' if self.active_mode.get() == 1 else 'finalMatchesData'

        get_team1_or_team2 = f"""
        SELECT 
            CASE 
                WHEN team1Id = ? THEN 'team1Goals'
                WHEN team2Id = ? THEN 'team2Goals'
                ELSE 'Not Found'
            END AS TeamIdColumn
        FROM {table_name}
        WHERE (team1Id = ? AND team2ID = ?) OR (team1Id = ? AND team2ID = ?);
        """
        self.cursor.execute(get_team1_or_team2, (teamID, teamID, teamID, team2ID, team2ID, teamID))
        
        self.team1_or_team2 = self.cursor.fetchone()[0]
        
        update_goals_for_match = f"""
        UPDATE {table_name}
        SET {self.team1_or_team2} = ?
        WHERE (team1Id = ? AND team2ID = ?) OR (team1Id = ? AND team2ID = ?);
        """
        self.cursor.execute(update_goals_for_match, (goals, teamID, team2ID, team2ID, teamID))
        
        self.connection.commit()
        
        
    def read_goals_for_match_from_db(self, teamID, team2ID):
        table_name = 'matchData' if self.active_mode.get() == 1 else 'finalMatchesData'

        get_team1_or_team2 = f"""
        SELECT 
            CASE 
                WHEN team1Id = ? THEN 'team1Goals'
                WHEN team2Id = ? THEN 'team2Goals'
                ELSE 'Not Found'
            END AS TeamIdColumn
        FROM {table_name}
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_team1_or_team2, (teamID, teamID, teamID, team2ID, team2ID, teamID))
        
        onefetched = self.cursor.fetchone() 
        
        if onefetched is None:
            return "None"
        
        self.team1_or_team2 = onefetched[0]
        
        get_goals_for_match = f"""
        SELECT {self.team1_or_team2} FROM {table_name}
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_goals_for_match, (teamID, team2ID, team2ID, teamID))
        
        goals = self.cursor.fetchone()[0]

        return goals
        
    
    def read_team_stats(self, team_id, stat):
        #self.custom_print("read_team_stats", "teams_playing", self.teams_playing, "team_id", team_id, "stat", stat)
        
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
            #self.custom_print("accsed matchData in save_games_played_in_db")
            
            getPlayed = """
            SELECT matchId FROM matchData
            WHERE (team1Id = ? OR team2Id = ?) AND matchId < ?
            """
            self.cursor.execute(getPlayed, (teamID, teamID, match_index + 2))
            
            played = self.cursor.fetchall()
            
            #self.custom_print("played", played)
            
            played = len(played)
            
            updatePlayed = """
            UPDATE teamData
            SET games = ?
            WHERE id = ?
            """
            
            self.cursor.execute(updatePlayed, (played, teamID))
            
        self.connection.commit()

    ###########################################################################################################
    ###########################################################################################################
    ###########################################################################################################
    ###########################################################################################################   

    def create_settings_elements(self):
        
        # Create elements for the Contact frame
        option_frame = ctk.CTkFrame(self.settings_frame, bg_color='#0e1718', fg_color='#0e1718')
        option_frame.pack(pady=10, anchor=tk.NW, side=tk.LEFT, padx=10)
        
        
        volume_label = ctk.CTkLabel(option_frame, text="Volume", font=("Helvetica", 19))
        volume_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        volume_value_label = ctk.CTkLabel(option_frame, textvariable=self.volume, font=("Helvetica", 17))
        volume_value_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        volume_slider = ctk.CTkSlider(
            option_frame, 
            orientation=tk.HORIZONTAL, 
            from_=0, 
            to=100, 
            variable=self.volume, 
            command=lambda event: self.on_volume_change(event), 
            width=200, 
            height=30)
        volume_slider.pack(pady=10, padx=10, side=tk.TOP, anchor=tk.NW)
        
        option_label = ctk.CTkLabel(option_frame, text="Spiel Modi", font=("Helvetica", 19))
        option_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        
        radio_button_1 = ctk.CTkRadioButton(option_frame, text="Gruppenphase", variable=self.active_mode, value=1, font=("Helvetica", 17), command=self.on_radio_button_change)
        radio_button_1.pack(side=tk.TOP, pady=2, padx = 5, anchor=tk.NW)

        radio_button_2 = ctk.CTkRadioButton(option_frame, text="Final Phase", variable=self.active_mode, value=2, font=("Helvetica", 17), command=self.on_radio_button_change)
        radio_button_2.pack(side=tk.TOP, pady=2, padx = 5, anchor=tk.NW)
        
        debug_label = ctk.CTkLabel(option_frame, text="Debug Mode", font=("Helvetica", 19))
        debug_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)

        radio_button_3 = ctk.CTkRadioButton(option_frame, text="Debug", variable=self.debug_mode, value=1, font=("Helvetica", 17), command=self.on_radio_debug_button_change)
        radio_button_3.pack(side=tk.TOP, pady=5, padx = 5, anchor=tk.NW)
        
        radio_button_4 = ctk.CTkRadioButton(option_frame, text="Debug Off", variable=self.debug_mode, value=0, font=("Helvetica", 17), command=self.on_radio_debug_button_change)
        radio_button_4.pack(side=tk.TOP, pady=5, padx = 5, anchor=tk.NW)
        
        
        # start time for matches
        start_time_label = ctk.CTkLabel(option_frame, text="Start Time", font=("Helvetica", 19))
        start_time_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        start_time_entry = ctk.CTkEntry(option_frame, textvariable=self.start_time, font=("Helvetica", 17))
        start_time_entry.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        start_time_entry.bind("<KeyRelease>", lambda event: self.on_start_time_change(event))
        
        
        # time interval for matches
        time_interval_label = ctk.CTkLabel(option_frame, text="Time Interval", font=("Helvetica", 19))
        time_interval_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        time_interval_entry = ctk.CTkEntry(option_frame, textvariable=self.time_interval, font=("Helvetica", 17))
        time_interval_entry.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        time_interval_entry.bind("<KeyRelease>", lambda event: self.on_time_interval_change(event))
        
        
        # time interval for final matches
        time_intervalFM_label = ctk.CTkLabel(option_frame, text="Time Interval Final Matches", font=("Helvetica", 19))
        time_intervalFM_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        time_intervalFM_entry = ctk.CTkEntry(option_frame, textvariable=self.time_intervalFM, font=("Helvetica", 17))
        time_intervalFM_entry.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        time_intervalFM_entry.bind("<KeyRelease>", lambda event: self.on_time_intervalFM_change(event))
        
        
        # pause time before final matches
        time_pause_before_FM_label = ctk.CTkLabel(option_frame, text="Time Pause Final Matches", font=("Helvetica", 19))
        time_pause_before_FM_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        time_pause_before_FM_entry = ctk.CTkEntry(option_frame, textvariable=self.time_pause_before_FM, font=("Helvetica", 17))
        time_pause_before_FM_entry.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        time_pause_before_FM_entry.bind("<KeyRelease>", lambda event: self.on_time_pause_before_FM_change(event))
        
        
        # website title
        website_title_label = ctk.CTkLabel(option_frame, text="Website Title", font=("Helvetica", 19))
        website_title_label.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        
        website_title_entry = ctk.CTkEntry(option_frame, textvariable=self.website_title, font=("Helvetica", 17))
        website_title_entry.pack(side=tk.TOP, pady=5, padx=5, anchor=tk.NW)
        website_title_entry.bind("<KeyRelease>", lambda event: self.on_website_title_change(event))
        
        
    def on_volume_change(self, event):
        saveVolumeInDB = """
        UPDATE settingsData
        SET volume = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveVolumeInDB, (event,))
        self.settingsconnection.commit()
       
        
    def on_radio_button_change(self):
        selected_value = self.active_mode.get()
        saveModeInDB = """
        UPDATE settingsData
        SET activeMode = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()
        
        self.teams_playing = [None, None]
        self.active_match = -1
        if stored_data.get("finalMatches") != None:
            del stored_data["finalMatches"]
        if self.updated_data.get("finalMatches") != None:
            del self.updated_data["finalMatches"]
        self.reload_spiel_button_command()
        
        
    def on_radio_debug_button_change(self):
        selected_value = self.debug_mode.get()
        saveModeInDB = """
        UPDATE settingsData
        SET debugMode = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()

        self.reload_spiel_button_command()
        
        
    def is_valid_time(self, time_str):
        if ":" in time_str:
            time_parts = time_str.split(":")
            if len(time_parts) != 2:
                return False
            hour, minute = time_parts
            if not hour.isdigit() or not minute.isdigit():
                return False
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                return False
            if len(minute) != 2:
                return False
            return True
        else:
            return False


    def on_start_time_change(self, event):
        if self.start_time.get() == "":
            return
        if not self.is_valid_time(str(self.start_time.get())):
            self.custom_print("Invalid time format. Please enter time in HH:MM format.")
            return

        saveStartTimeInDB = """
        UPDATE settingsData
        SET startTime = ?
        WHERE id = 1
        """
        self.custom_print("on_start_time_change", self.start_time.get())
        self.settingscursor.execute(saveStartTimeInDB, (self.start_time.get(),))
        self.settingsconnection.commit()

        self.updated_data.update({"startTime": get_data_for_website(7)})
        
        
    def on_time_interval_change(self, event):
        if self.time_interval.get() == "":
            return
        if self.time_interval.get()[-1] not in "0123456789m" or not "m" in self.time_interval.get() or len(self.time_interval.get()) < 1:
            return
        saveTimeIntervalInDB = """
        UPDATE settingsData
        SET timeInterval = ?
        WHERE id = 1
        """
        print("on_time_interval_change", self.time_interval.get())
        self.settingscursor.execute(saveTimeIntervalInDB, (self.time_interval.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"timeInterval": self.time_interval.get().replace("m", "")})
        

    def on_time_intervalFM_change(self, event):
        if self.time_intervalFM.get() == "":
            return
        if self.time_intervalFM.get()[-1] not in "0123456789m" or not "m" in self.time_intervalFM.get() or len(self.time_intervalFM.get()) < 1:
            return
        saveTimeIntervalFMInDB = """
        UPDATE settingsData
        SET timeIntervalFM = ?
        WHERE id = 1
        """
        print("on_time_intervalFM_change", self.time_intervalFM.get())
        self.settingscursor.execute(saveTimeIntervalFMInDB, (self.time_intervalFM.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"timeIntervalFM": self.time_intervalFM.get().replace("m", "")})
        
        
    def on_time_pause_before_FM_change(self, event):
        if self.time_pause_before_FM.get() == "":
            return
        if self.time_pause_before_FM.get()[-1] not in "0123456789m" or not "m" in self.time_pause_before_FM.get() or len(self.time_pause_before_FM.get()) < 1:
            return
        saveTimePauseBeforeFMInDB = """
        UPDATE settingsData
        SET pauseBeforeFM = ?
        WHERE id = 1
        """
        print("on_time_pause_before_FM_change", self.time_pause_before_FM.get())
        self.settingscursor.execute(saveTimePauseBeforeFMInDB, (self.time_pause_before_FM.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"pauseBeforeFM": self.time_pause_before_FM.get().replace("m", "")})
        
        
    def on_website_title_change(self, event):
        if self.website_title.get() == "":
            return
        saveWebsiteTitleInDB = """
        UPDATE settingsData
        SET websiteTitle = ?
        WHERE id = 1
        """
        print("on_website_title_change", self.website_title.get())
        self.settingscursor.execute(saveWebsiteTitleInDB, (self.website_title.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"websiteTitle": self.website_title.get()})
   
            
##############################################################################################
##############################################################################################
##############################################################################################

    def show_frame(self, frame):
        # Hide all frames and pack the selected frame
        for frm in [self.Team_frame, self.player_frame, self.SPIEL_frame, self.settings_frame]: # self.settings_frame
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)


    def show_Team_frame(self):
        self.reload_button_command()
        self.show_frame(self.Team_frame)


    def show_player_frame(self):
        self.reload_button_player_command()
        self.show_frame(self.player_frame)


    def show_SPIEL_frame(self):
        if self.teams_playing.count(None) == 0:
            self.reload_spiel_button_command()
            
        #self.custom_print(stored_data)
        self.calculate_matches()
        self.show_frame(self.SPIEL_frame)

        
    def show_settings_frame(self):
        self.show_frame(self.settings_frame)


##############################################################################################
##############################################################################################
##############################################################################################
            
    def test(self):
        self.custom_print("test")
        
        
    def delete_updated_data(self):
        #self.custom_print("delete")
        #self.custom_print(self.updated_data)
        self.updated_data = {}
        
        
    def play_mp3(self, file_path, volume=""):
        if file_path == "":
            return
        if volume == "":
            volume = self.volume
        player = self.media_player_instance.media_player_new()
        media = self.media_player_instance.media_new(file_path)
        player.set_media(media)
        player.audio_set_volume(int(volume.get()))
        player.play()
        #self.custom_print("play_mp3", file_path, "volume", volume.get(), "self.volume", self.volume.get(), "player", player,"media", media)
   
        
##############################################################################################
#############################Calculate########################################################
##############################################################################################
##############################################################################################

    def calculate_matches(self):
        self.match_count = 0  # Reset matchCount to 0

        #if self.active_mode.get() == 1 or True:
        initial_data = {
            "Teams": self.read_teamNames()
        }

        initial_data["Teams"].pop(0)

        teams = initial_data["Teams"][:]  # Create a copy of the teams array
        
        teams.sort()
        
        #print("calculate_matches: teams", teams)

        # If the number of teams is odd, add a "dummy" team
        #if len(teams) % 2 != 0:
        #    print("calculate_matches: uneven number of teams, appending dummy team")
        #    teams.append("dummy")

        midpoint = (len(teams) + 1) // 2
        group1 = teams[:midpoint]
        group2 = teams[midpoint:]

        matches1 = self.calculate_matches_for_group(group1, "Gruppe 1")
        matches2 = self.calculate_matches_for_group(group2, "Gruppe 2")
        
        matches = self.interleave_matches(matches1, matches2)

        self.match_count = 0  # Reset matchCount to 0

        self.matches = list(map(lambda match: self.add_match_number(match), matches))
        
        #self.custom_print("self.matches", self.matches)
        
        self.save_matches_to_db()
        
        self.updated_data.update({"Matches": get_data_for_website(4)})
    
        return self.matches


    def calculate_matches_for_group(self, teams, group_name):
        n = len(teams)
        matches = []

        # If the number of teams is odd, add a "dummy" team
        dummy = False
        if n % 2 != 0:
            #print("calculate_matches_for_group: uneven number of teams, appending dummy team", "teams", teams)
            teams.append("dummy")
            n += 1
            dummy = True

        for round in range(n - 1):
            for i in range(n // 2):
                team1 = teams[i]
                team2 = teams[n - 1 - i]
                # Skip matches involving the "dummy" team
                if dummy and (team1 == "dummy" or team2 == "dummy"):
                    continue
                matches.append([team1, team2])
            # Rotate the teams for the next round
            teams.insert(1, teams.pop())

        matches = list(map(lambda match_index: {"number": "Spiel " + str(match_index[0] + 1), "teams": match_index[1], "group": group_name}, enumerate(matches)))

        #print("calculate_matches_for_group: matches", matches)
        
        return matches


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

        # Fetch all team IDs at once
        select_teams = """
        SELECT id, teamName FROM teamData
        ORDER BY id ASC
        """
        self.cursor.execute(select_teams)
        teams = {row[1]: row[0] for row in self.cursor.fetchall()}

        match_tuples = []
        for match in self.matches:
            team1 = match["teams"][0]
            team2 = match["teams"][1]
            group = match["group"]
            number = match["number"]

            team1ID = teams.get(team1)
            team2ID = teams.get(team2)

            if team1ID is None or team2ID is None or team2 == "dummy":
                continue

            match_tuple = (int(team1ID), int(team2ID), int(str(group).replace('Gruppe ','')), int(str(number).replace('Spiel ','')))
            match_tuples.append(match_tuple)

        # Use executemany() for bulk insert
        insert_match_query = """
            INSERT OR IGNORE INTO matchData (team1Id, team2Id, groupNumber, matchId)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.executemany(insert_match_query, match_tuples)

        # Use executemany() for bulk update
        update_match_query = """
            UPDATE matchData
            SET team1Id = ?, team2Id = ?, groupNumber = ?
            WHERE matchId = ?
        """
        self.cursor.executemany(update_match_query, match_tuples)

        # Commit the transaction
        self.connection.commit()

        # Find matches to delete
        teams_to_delete = [match for match in existing_matches if match not in match_tuples]
                
                
        #self.custom_print("teams_to_delete", teams_to_delete)
        
        #self.custom_print("accsed matchData in save_matches_to_db")
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
    
    if which_data == 4:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        get_all_matches = """
        SELECT team1Id, team2Id, team1Goals, team2Goals, groupNumber FROM matchData
        ORDER BY matchId ASC
        """
        
        cursor.execute(get_all_matches)
        
        #get the team names instead of the team ids, remove the team id after the name for that team has been found
        all_matches = []
        
        for match in cursor.fetchall():
                
            get_team1_name = """
            SELECT teamName FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            cursor.execute(get_team1_name, (match[0],))
            team1_name = cursor.fetchone()[0]
            
            get_team2_name = """
            SELECT teamName FROM teamData
            WHERE id = ?
            ORDER BY id ASC
            """
            cursor.execute(get_team2_name, (match[1],))
            team2_name = cursor.fetchone()[0]
            
            all_matches.append((team1_name, team2_name, match[2], match[3], match[4]))
            # self.custom_print every var
            #self.custom_print("team1_name", team1_name, "team2_name", team2_name, "match[2]", match[2], "match[3]", match[3])
        
        cursor.close()
        connection.close()
        
        #self.custom_print("all_matches", all_matches)
        return all_matches
    
    if which_data == 5:
        
        a_m = tkapp.active_match
        
        if tkapp.active_mode.get() == 2:
            a_m += 1
            a_m *= -1
        
        return a_m
    
    if which_data == 6 and tkapp.active_mode.get() == 2:
          
        final_goles = []
        
        if tkapp.endteam1 and tkapp.endteam3:
            final_goles.append([ich_kann_nicht_mehr(tkapp.endteam1[0], tkapp.endteam3[0]), ich_kann_nicht_mehr(tkapp.endteam3[0], tkapp.endteam1[0])])
        else:
            final_goles.append([None, None])
            
        if tkapp.endteam2 and tkapp.endteam4:
            final_goles.append([ich_kann_nicht_mehr(tkapp.endteam2[0], tkapp.endteam4[0]), ich_kann_nicht_mehr(tkapp.endteam4[0], tkapp.endteam2[0])])
        else:
            final_goles.append([None, None])
            
        if tkapp.spiel_um_platz_3:
            final_goles.append([ich_kann_nicht_mehr(tkapp.spiel_um_platz_3[0][0], tkapp.spiel_um_platz_3[1][0]), ich_kann_nicht_mehr(tkapp.spiel_um_platz_3[1][0], tkapp.spiel_um_platz_3[0][0])])
        else:
            final_goles.append([None, None])
            
        if tkapp.final_match_teams:
            final_goles.append([ich_kann_nicht_mehr(tkapp.final_match_teams[0][0], tkapp.final_match_teams[1][0]), ich_kann_nicht_mehr(tkapp.final_match_teams[1][0], tkapp.final_match_teams[0][0])])
        else:
            final_goles.append([None, None])

        v = [
            [tkapp.endteam1[1] if tkapp.endteam1 else None, tkapp.endteam3[1] if tkapp.endteam3 else None, final_goles[0]], 
            [tkapp.endteam2[1] if tkapp.endteam2 else None, tkapp.endteam4[1] if tkapp.endteam4 else None, final_goles[1]], 
            [tkapp.spiel_um_platz_3[0][1] if tkapp.spiel_um_platz_3 else None, tkapp.spiel_um_platz_3[1][1] if tkapp.spiel_um_platz_3 else None, final_goles[2]], 
            [tkapp.final_match_teams[0][1] if tkapp.final_match_teams else None, tkapp.final_match_teams[1][1] if tkapp.final_match_teams else None, final_goles[3]]
        ]
        return v
    
    if which_data == 7:
        start_time = tkapp.start_time.get()
        a, b = start_time.split(":")
        return [int(a), int(b)]


def ich_kann_nicht_mehr(teamID, team2ID):
      
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
        
    get_team1_or_team2 = """
    SELECT 
        CASE 
            WHEN team1Id = ? THEN 'team1Goals'
            WHEN team2Id = ? THEN 'team2Goals'
            ELSE 'Not Found'
        END AS TeamIdColumn
    FROM finalMatchesData
    WHERE (team1Id = ? OR team2Id = ?) AND (team1Id = ? OR team2Id = ?);
    """
    cursor.execute(get_team1_or_team2, (teamID, teamID, teamID, teamID, team2ID, team2ID))
    
    onefetched = cursor.fetchone()
    
    if onefetched is None:
        return None
            
    team1_or_team2 = onefetched[0]

    get_goals_for_match = """
    SELECT {column} FROM finalMatchesData
    WHERE (team1Id = ? OR team2Id = ?) AND (team1Id = ? OR team2Id = ?);
    """
    cursor.execute(get_goals_for_match.format(column=team1_or_team2), (teamID, teamID, team2ID, team2ID))
    
    goals = cursor.fetchone()[0]
    
    cursor.close()
    connection.close()
    
    return goals
        
  
def get_initial_data(template_name):
    global initial_data
    tkapp.test()
    
    initial_data = {
        "Teams": get_data_for_website(0),
        "Goals": get_data_for_website(1),
        "Games": get_data_for_website(2),
        "Points": get_data_for_website(3),
        "Matches": get_data_for_website(4),
        "activeMatchNumber": get_data_for_website(5),
        "finalMatches": get_data_for_website(6),
        "timeInterval": tkapp.time_interval.get().replace("m", ""),
        "timeIntervalFM": tkapp.time_intervalFM.get().replace("m", ""),
        "pauseBeforeFM": tkapp.time_pause_before_FM.get().replace("m", ""),
        "startTime": get_data_for_website(7),
        "websiteTitle": tkapp.website_title.get(),
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
    #self.custom_print("last_data_update", last_data_update)
    
    updated_data = tkapp.updated_data
    
    
    if updated_data != {}:
        
        #self.custom_print("updated_data)  ", updated_data, "last_data_update", last_data_update, "should be updated")
        #self.custom_print(updated_data.keys())
        #self.custom_print(updated_data.values())
        for key, value in updated_data.items():
            for key2, value2 in stored_data.items():
                if key in value2.keys():
                    stored_data.pop(key2)
                    break
            
            stored_data.update({time.time()-3:{key:value}})
            #self.custom_print("stored_data", stored_data)
        
        updated_data.update({"LastUpdate": timeatstart})
        
    for key, value in stored_data.items():
        #self.custom_print("magucken")
        if key >= float(last_data_update):
            #self.custom_print("key", key, "value", value, "last_data_update", last_data_update, "should be updated")
            updated_data.update(value)
            updated_data.update({"LastUpdate": timeatstart})
            #self.custom_print("updated_data", updated_data)
            
    
    #self.custom_print("stored_data", stored_data, "updated_data", updated_data, "last_data_update", last_data_update)
        
    #self.custom_print("updated_data", updated_data)

    tkapp.delete_updated_data()
    
    #updated_data = {'Players': {"Player1":"Erik Van Doof","Player2":"Felix Schweigmann"}}  # You can modify this data as needed
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