import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox
import customtkinter as ctk
import threading
import requests
import os
import time
from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import vlc
import datetime
import glob
import ast
import logging
import sys
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import pathlib
import functools
import platform
import subprocess
import json
import traceback

def get_key():
    return session.get('email', 'anonymous')

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_key,  # use get_key function for rate limiting
    default_limits=["20 per minute"],
    storage_uri="memory://"
)
app.secret_key = "Felix.com"
lock = threading.Lock()

class Window(ctk.CTk):
    
    def create_navigation_bar(self):
        navigation_frame = ctk.CTkFrame(self, fg_color='#142324', corner_radius=0)
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        buttons = [
            ("Team Creation", self.show_Team_frame),
            ("Player Selection", self.show_player_frame),
            ("Active Match", self.show_SPIEL_frame),
            ("Tipping", self.show_tipping_frame),
            ("Settings", self.show_settings_frame),
        ]

        button_width = self.screenwidth / 12.8
        button_height = self.screenheight / 25
        button_font_size = self.screenwidth / 120

        for text, command in buttons:
            button = ctk.CTkButton(navigation_frame, text=text, command=command, width=button_width, height=button_height, font=("Helvetica", button_font_size, "bold"), fg_color="#34757a", hover_color="#1f4346")
            if text == "Settings":
                button.pack(side=tk.BOTTOM, anchor=tk.S, pady=8, padx=14, fill=tk.X)
            else:
                button.pack(side=tk.TOP, anchor=tk.N, pady=8, padx=14, fill=tk.X)
            
            
    def __init__(self, start_server):
        super().__init__()
        # Create 
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
        self.tippers_list_frame = None
        self.media_player_instance_save = None
        
        self.delay_time_label = None
        self.delay_time_save_for_blinking = 0
        
        self.watch_dog_process_can_be_active = False
        
        self.save_delay_time = 2
        self.settingsconnection = None
        self.settingscursor = None
        
        # helping, saving variables
        self.reload_requried_on_click_SPIEL = False
        self.manual_select_active = False
        self.manual_select_active_sure = False
        
        # Cache for the website
        self.cache = {}
        
        # Cachevariables
        self.cache_vars = {
            "points_changed_using_active_match": -1,
            "getmatches_changed_using_var": True,
            "getgames_changed_using_var": True,
            "getgoals_changed_using_var": True,
            "getteams_changed_using_var": True,
            "getfinalmatches_changed_using_var": True,
            "getteams_changed_using_var": True,
            "getbestscorer_changed_using_var": True,
            "getkomatches_changed_using_var": True,
        }

        # Get the screen size
        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()
        
        # setup logging
        logging.basicConfig(filename="log.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

        # Create a StreamHandler to log to the console
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.ERROR)
        self.console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.console_handler.setFormatter(self.console_formatter)

        # Add the StreamHandler to the logger
        logging.getLogger().addHandler(self.console_handler)

        logging.debug("Started logging")
        
        
        # Set window title
        self.title("Football Tournament Manager")
        if platform.system() == 'Windows':
            self.after(0, lambda:self.state('zoomed'))
        self.configure(fg_color="#0e1718")
        if platform.system() == 'Windows':
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
        if platform.system() == 'Windows':
            self.media_player_instance = vlc.Instance()
            self.media_player_instance.log_unset()
        

        # Create and pack the navigation bar
        self.create_navigation_bar()

        # Create frames for different sets of elements
        self.Team_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)
        self.player_frame = ctk.CTkFrame(self, height=10, fg_color='#0e1718', corner_radius=0)
        self.SPIEL_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)
        self.tipping_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)
        self.settings_frame = ctk.CTkFrame(self, fg_color='#0e1718', corner_radius=0)

        # Create elements for each frame
        self.create_Team_elements()
        self.create_player_elements()
        self.create_SPIEL_elements()
        self.create_tipping_elements()
        self.create_settings_elements()

        if start_server:
            server_thread = threading.Thread(target=self.start_server, daemon=True)
            server_thread.start()
            
            
        # Display the default frame
        self.show_frame(self.Team_frame)
        
        #logging.debug("finished init")
        
        
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
        
        KOMatchesDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS KOMatchesData (
            matchId INTEGER PRIMARY KEY,
            team1Id INTEGER REFERENCES teamData(id),
            team2Id INTEGER REFERENCES teamData(id),
            team1Goals INTEGER DEFAULT 0,
            team2Goals INTEGER DEFAULT 0,
            matchTime TEXT
        )
        """
        self.cursor.execute(KOMatchesDataTableCreationQuery)
        self.connection.commit()
        
        playerPerMatchDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchData (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES matchData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataTableCreationQuery)
        self.connection.commit()
        
        playerPerMatchDataFinalTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchDataFinal (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES finalMatchesData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataFinalTableCreationQuery)
        self.connection.commit()
        
        playerPerMatchDataKOTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchDataKO (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES matchData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataKOTableCreationQuery)
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
            websiteTitle TEXT DEFAULT "",
            teams_playing INTEGER DEFAULT 0,
            activeMatch INTEGER DEFAULT 0,
            pauseMode BOOLEAN DEFAULT 0,
            timeIntervalForOnlyTheFinalMatch TEXT DEFAULT "",
            bestScorerActive BOOLEAN DEFAULT 0,
            thereAreKOMatches BOOLEAN DEFAULT 0,
            timeIntervalKO TEXT DEFAULT "",
            timeBeforeTheFinalMatch TEXT DEFAULT "",
            pauseBeforeKO TEXT DEFAULT "",
            halfTimePause TEXT DEFAULT ""
        )
        """
        self.settingscursor.execute(settingsDataTableCreationQuery)
        self.settingsconnection.commit()
        
        tippingTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS tippingData (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES matchData(matchId),
            team1Goals INTEGER DEFAULT 0,
            team2Goals INTEGER DEFAULT 0,
            googleId TEXT REFERENCES userData(googleId),
            points INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(tippingTableCreationQuery)
        self.connection.commit()
        
        userDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS userData (
            id INTEGER PRIMARY KEY,
            googleId TEXT,
            userName TEXT
        )
        """
        self.cursor.execute(userDataTableCreationQuery)
        self.connection.commit()
        
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
        self.volume = tk.IntVar(value=50)
        self.active_mode = tk.IntVar(value=-1)
        self.debug_mode = tk.IntVar(value=0)
        self.start_time = tk.StringVar(value="08:00")
        self.time_interval = tk.StringVar(value="10m")
        self.time_intervalFM = tk.StringVar(value="10m")
        self.time_intervalKO = tk.StringVar(value="10m")
        self.time_pause_before_FM = tk.StringVar(value="0m") 
        self.website_title = tk.StringVar(value="HHG-Fußballturnier")
        self.pause_mode = tk.IntVar(value=0)
        self.time_interval_for_only_the_final_match = tk.StringVar(value="10m")
        self.best_scorer_active = tk.BooleanVar(value=False)
        self.there_is_an_ko_phase = tk.BooleanVar(value=False)
        self.time_before_the_final_match = tk.StringVar(value="0m")
        self.time_pause_before_KO = tk.StringVar(value="0m")
        self.half_time_pause = tk.StringVar(value="0m")
        
        # load the settings from the database into the variables
        if settings[5] is not None and settings[5] != "" and settings[5] != 0:
            self.volume.set(value=settings[5])
            
        if settings[6] is not None and settings[6] != "" and settings[6] != 0:
            logging.debug(f"settings[6]: {settings[6]}")
            self.active_mode.set(value=settings[6])
        
        if settings[7] is not None and settings[7] != "" and settings[7] != 0:
            logging.debug(f"settings[7]: {settings[7]}")
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
        
        if settings[13] is not None and settings[13] != "" and settings[13] != 0:

            self.teams_playing = ast.literal_eval(settings[13])
            logging.debug(f"self.teams_playing: {self.teams_playing[0]}")
            logging.debug(f"settings[13]: {settings[13]}")
            logging.debug(f"Type of self.teams_playing: {type(self.teams_playing)}")
        
        if settings[14] is not None:
            self.active_match = settings[14]
            
        if settings[15] is not None and settings[15] != "" and settings[15] != 0:
            self.pause_mode.set(value=settings[15])
        
        if settings[16] is not None and settings[16] != "" and settings[16] != 0:
            self.time_interval_for_only_the_final_match.set(value=settings[16])
            
        if settings[17] is not None and settings[17] != "" and settings[17] != 0:
            self.best_scorer_active.set(value=settings[17])

        if settings[18] is not None and settings[18] != "" and settings[18] != 0:
            self.there_is_an_ko_phase.set(value=settings[18])

        if settings[19] is not None and settings[19] != "" and settings[19] != 0:
            self.time_intervalKO.set(value=settings[19])

        if settings[20] is not None and settings[20] != "" and settings[20] != 0:
            self.time_before_the_final_match.set(value=settings[20])

        if settings[21] is not None and settings[21] != "" and settings[21] != 0:
            self.time_pause_before_KO.set(value=settings[21])

        if settings[22] is not None and settings[22] != "" and settings[22] != 0:
            self.half_time_pause.set(value=settings[22])
            
        if self.debug_mode.get() == 1:
            self.console_handler.setLevel(logging.DEBUG)
        elif self.debug_mode.get() == 0:
            self.console_handler.setLevel(logging.ERROR)
    
    
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    
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


    def write_names_into_entry_fields(self):
        selectTeams = """
        SELECT teamName, mp3Path FROM teamData
        ORDER BY id ASC
        """
        self.cursor.execute(selectTeams)
        
        allfetched = self.cursor.fetchall()
        
        if not allfetched:
            self.add_name_entry()
        
        for teamName, mp3_path in allfetched:
            self.add_name_entry(teamName, mp3_path)


    def add_name_entry(self, entry_text="", mp3_path=""):
        if not hasattr(self, 'team_element_width'):
            self.team_element_width = self.screenwidth / 10
            self.team_element_height = self.screenheight / 30
            self.team_element_font_size = self.screenwidth / 150

        count = len(self.name_entries) + 1
        team_id = count - 1

        label_text = f'Team {count}'
        label = ctk.CTkLabel(self.team_entries_frame, text=label_text, font=("Helvetica", self.team_element_font_size * 1.2, "bold"))
        label.grid(row=team_id, column=0, padx=15, pady=5, sticky='e')
        
        new_entry = ctk.CTkEntry(self.team_entries_frame, font=("Helvetica", self.team_element_font_size), width=self.team_element_width, height=self.team_element_height)
        
        if entry_text:
            new_entry.insert(0, entry_text)
        
        new_entry.grid(row=team_id, column=1, pady=5, sticky='we')
        
        new_file_dialog = ctk.CTkButton(self.team_entries_frame, text="Select mp3", command=lambda: self.save_mp3_path(new_file_dialog, team_id), width=self.team_element_width, height=self.team_element_height, font=("Helvetica", self.team_element_font_size), fg_color="#34757a", hover_color="#1f4346")
        new_file_dialog.grid(row=team_id, column=2, pady=5, sticky='we', padx=12)
        
        if mp3_path:
            self.mp3_list[team_id] = mp3_path
            new_file_dialog.configure(text=os.path.basename(mp3_path))
        
        self.file_dialog_list.append(new_file_dialog)
        self.name_entries.append(new_entry)
        self.label_list.append(label)


    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    
    def save_mp3_path(self, new_file_dialog, team_id):
        file_path = filedialog.askopenfilename(title="Select mp3 file", filetypes=(("mp3 files", "*.mp3"), ("all files", "*.*")))
        
        if file_path:
            self.mp3_list[team_id] = file_path
            new_file_dialog.configure(text=os.path.basename(file_path))

        #logging.debug(file_path)
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
        with self.connection:
            self.create_backup_of_db()

            old_mp3_list = [row[0] if row else "" for row in self.cursor.execute("SELECT mp3Path FROM teamData").fetchall()]

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

            existing_teams = set()
            new_team_data = []
            total_entries = len(self.name_entries)
            midpoint = total_entries // 2

            for i, entry in enumerate(self.name_entries):
                entry_text = entry.get().strip()
                group_number = 1 if (i < midpoint) or (total_entries % 2 != 0 and i == midpoint) else 2

                if entry_text:
                    if entry_text not in existing_teams:
                        new_team_data.append((entry_text, group_number))
                        existing_teams.add(entry_text)
                    else:
                        for i in range(1, 100):
                            new_entry_text = f"{entry_text} {i}"
                            if new_entry_text not in existing_teams:
                                new_team_data.append((new_entry_text, group_number))
                                existing_teams.add(new_entry_text)
                                break

            self.cursor.executemany("INSERT INTO teamData (teamName, groupNumber) VALUES (?, ?)", new_team_data)
            self.connection.commit()

            team_ids = [row[0] for row in self.cursor.execute("SELECT id FROM teamData").fetchall()]

            for team_id in team_ids:
                mp3_entry = self.mp3_list.get(team_id-1, "")
                if not mp3_entry.strip() and team_id - 1 < len(old_mp3_list) and old_mp3_list[team_id - 1]:
                    self.mp3_list[team_id-1] = old_mp3_list[team_id-1]

            self.cursor.executemany("UPDATE teamData SET mp3Path = ? WHERE id = ?", [(mp3_path, team_id + 1) for team_id, mp3_path in self.mp3_list.items()])
            self.connection.commit()

            self.calculate_matches()
            self.get_teams_for_final_matches()
            self.reset_player_stats()
            self.reset_player_per_match_data()

            self.reset_match_datas()

            self.active_mode.set(1)
            self.pause_mode.set(0)

            self.save_active_mode_in_db()

            self.on_pause_switch_change()

            self.reload_requried_on_click_SPIEL = True

            self.cache_vars = {
                "points_changed_using_active_match": -1,
                "getmatches_changed_using_var": True,
                "getgames_changed_using_var": True,
                "getgoals_changed_using_var": True,
                "getteams_changed_using_var": True,
                "getfinalmatches_changed_using_var": True,
                "getteams_changed_using_var": True,
                "getbestscorer_changed_using_var": True,
                "getkomatches_changed_using_var": True,
            }
            
            self.updated_data.update({"Teams": get_data_for_website(0)})
            self.updated_data.update({"Matches": get_data_for_website(4)})
            self.updated_data.update({"finalMatches": get_data_for_website(6)})
    

    def create_backup_of_db(self):
        backup_dir = "data/backups/"
        os.makedirs(backup_dir, exist_ok=True)  # Ensure the directory exists

        # Get list of existing backups
        existing_backups = glob.glob(backup_dir + "*.db")

        # If there are more than 5 backups, delete the oldest one
        if len(existing_backups) > 10:
            oldest_backup = min(existing_backups, key=os.path.getctime)
            os.remove(oldest_backup)

        # Create new backup with a unique name
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir + "backup_" + timestamp + ".db"

        connection = sqlite3.connect(self.db_path)
        with sqlite3.connect(backup_path) as backup_conn:
            connection.backup(backup_conn)
        logging.debug("Backup created")



        connection.commit()

        connection.close()

        return backup_path


    def reset_match_datas(self):
            self.cursor.execute("UPDATE matchData SET team1Goals = 0, team2Goals = 0, matchTime = ''")
            self.cursor.execute("DROP TABLE finalMatchesData")

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

            self.cursor.execute("DROP TABLE KOMatchesData")

            KOMatchesDataTableCreationQuery = """
            CREATE TABLE IF NOT EXISTS KOMatchesData (
                matchId INTEGER PRIMARY KEY,
                team1Id INTEGER REFERENCES teamData(id),
                team2Id INTEGER REFERENCES teamData(id),
                team1Goals INTEGER DEFAULT 0,
                team2Goals INTEGER DEFAULT 0,
                matchTime TEXT
            )
            """
            self.cursor.execute(KOMatchesDataTableCreationQuery)
            self.connection.commit()

            self.cursor.execute("DROP TABLE tippingData")

            tippingTableCreationQuery = """
            CREATE TABLE IF NOT EXISTS tippingData (
                id INTEGER PRIMARY KEY,
                matchId INTEGER REFERENCES matchData(matchId),
                team1Goals INTEGER DEFAULT 0,
                team2Goals INTEGER DEFAULT 0,
                googleId TEXT REFERENCES userData(googleId),
                points INTEGER DEFAULT 0
            )
            """
            self.cursor.execute(tippingTableCreationQuery)
            self.connection.commit()
            

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
                logging.exception("teamID: " + str(teamID))
                logging.exception("teamNames: " + str(teamNames))
                logging.exception("team_IDs: " + str(team_IDs))
                logging.exception("i: " + str(i))

            if i < 8:
                #logging.debug("created button in upper frame")
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
        
        self.cache_vars["getteams_changed_using_var"] = True
        
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

        varnames = [f"{var}{Frame}" for var in ["count", "entries", "entries2", "entries3", "label"]]

        # Initialize variables in the dictionary
        for varname in varnames:
            if varname not in self.variable_dict:
                self.variable_dict[varname] = 0 if varname.startswith("count") else []

        # Now you can access the count using the dynamic variable name
        count = self.variable_dict[varnames[0]] + 1

        # Update the count in the dictionary
        self.variable_dict[varnames[0]] = count

        label_font_size = self.screenwidth / 150
        entry_width = self.screenwidth / 10
        entry_height = self.screenheight / 30
        # Create a label with "Team 1" and the count
        label_text = f'{Counter} {count}'
        label = ctk.CTkLabel(Frame, text=label_text, font=("Helvetica", label_font_size * 1.2, "bold"))
        label.grid(row=len(self.variable_dict[varnames[1]]), column=0, padx=10, pady=8, sticky='e')

        # Create new entry fields
        entries = [ctk.CTkEntry(Frame, font=("Helvetica", label_font_size), height=entry_height, width=entry_width) for _ in range(3)]
        entry_texts = [entry_text, entry_text2, entry_text3 if entry_text3 else "0"]

        # Write entry_text to the entry fields if they are not empty
        for entry, text in zip(entries, entry_texts):
            entry.insert(0, text)
            entry.grid(row=len(self.variable_dict[varnames[1]]), column=entries.index(entry)+1, pady=5, sticky='we', padx=3)

        # Append new entries and label to the dictionary
        for i in range(1, 5):
            self.variable_dict[varnames[i]].append(entries[i-1] if i < 4 else label)

    
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
        #logging.debug("teamNames", teamNames, "team_IDs", team_IDs)
        
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
        self.canvas.yview_moveto(0.0)
        team_button = team_button_list[index]

        varnames = [f"{var}{self.frameplayer}" for var in ["entries", "entries2", "entries3", "label"]]

        # Check if the key exists in the dictionary and delete the widgets
        for varname in varnames:
            if self.variable_dict.get(varname):
                for widget in self.variable_dict[varname]:
                    widget.destroy()
                self.variable_dict[varname] = []

        self.selected_team_in_player = teamID

        self.variable_dict[f"count{self.frameplayer}"] = 0

        self.cool_current_team_label.configure(text=str(teamName))

        self.write_names_into_entry_fields_players(teamID, "Player", self.frameplayer)
          
            
    def read_player_stats(self, teamID, readGoals=False, readID=False, playerID=-1):
        output = []

        if readID and playerID != -1:
            raise ValueError("readID and playerID cannot be True at the same time")

        # Determine the columns to select based on readGoals and readID
        columns = "playerName, playerNumber, goals" if readGoals else "playerName, playerNumber"
        columns =  columns + ", id" if readID else columns
        
        #logging.debug("columns", columns)

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

        if teams_to_read != -1:
            # Convert teams_to_read to a list of integers and increment each by 1
            teams_to_read = [int(team) + 1 for team in teams_to_read if team is not None]

            # Create a string of question marks for the IN clause
            placeholders = ', '.join('?' for _ in teams_to_read)

            # Create the SQL query
            selectTeam = f"""
            SELECT teamName FROM teamData
            WHERE id IN ({placeholders})
            ORDER BY id ASC
            """

            # Execute the query and fetch all results
            self.cursor.execute(selectTeam, teams_to_read)
            results = self.cursor.fetchall()

            # Append the team names to teamNames
            teamNames.extend(result[0] for result in results)

        else:
            selectTeams = """
            SELECT teamName FROM teamData
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeams)

            # Append the team names to teamNames
            teamNames.extend(team[0] for team in self.cursor.fetchall())

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


    def reset_player_stats(self):
        self.cursor.execute("UPDATE playerData SET goals = 0")
        self.connection.commit()


    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    def create_SPIEL_elements(self):
        
        self.manual_select_active_sure = False
        
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

        if self.pause_mode.get() == 1:
            #pause_mode_active_label = ctk.CTkLabel(manual_frame, text="Pause Mode Active", font=("Helvetica", button_font_size * 1.5, "bold"), fg_color="red")
            #pause_mode_active_label.place(relx=0.7, rely=0.4)
            #Replace the label with a button
            self.pause_mode_active_button = ctk.CTkButton(manual_frame, text="Pause Mode Active", command=self.on_pause_button_change, fg_color="red", hover_color="#801818", font=("Helvetica", button_font_size * 1.5, "bold"), height=button_height)
            self.pause_mode_active_button.place(relx=0.7, rely=0.3)
        
        if self.best_scorer_active.get() == 1:
            #best_scorer_active_label = ctk.CTkLabel(manual_frame, text="Best Scorer Active", font=("Helvetica", button_font_size * 1.5, "bold"), fg_color="red")
            #best_scorer_active_label.place(relx=0.7, rely=0.1)
            #Replace the label with a button
            self.best_scorer_active_button = ctk.CTkButton(manual_frame, text="Best Scorer Active", command=self.on_best_scorer_button_change, fg_color="red", hover_color="#801818", font=("Helvetica", button_font_size * 1.5, "bold"), height=button_height)
            self.best_scorer_active_button.place(relx=0.7, rely=0.1)
        
        if self.there_is_an_ko_phase.get() == 1:
            ko_phase_active_label = ctk.CTkLabel(manual_frame, text="KO Phase Active", font=("Helvetica", button_font_size * 1.5, "bold"), text_color="green")
            ko_phase_active_label.place(relx=0.7, rely=0.6)

        if self.active_mode.get() == 1:
            active_mode_label = ctk.CTkLabel(manual_frame, text=f"Active Mode: Group Phase ({self.active_mode.get()})", font=("Helvetica", button_font_size * 1.5, "bold"), text_color="green")
            active_mode_label.place(relx=0.7, rely=0.8)
        elif self.active_mode.get() == 3:
            active_mode_label = ctk.CTkLabel(manual_frame, text=f"Active Mode: KO Phase ({self.active_mode.get()})", font=("Helvetica", button_font_size * 1.5, "bold"), text_color="green")
            active_mode_label.place(relx=0.7, rely=0.8)
        elif self.active_mode.get() == 2:
            active_mode_label = ctk.CTkLabel(manual_frame, text=f"Active Mode: Final Matches ({self.active_mode.get()})", font=("Helvetica", button_font_size * 1.5, "bold"), text_color="green")
            active_mode_label.place(relx=0.7, rely=0.8)

        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}
        
        self.get_teams_for_final_matches()

        logging.debug(f"self.teams_playing: {self.teams_playing}")
        
        team_names = self.read_teamNames()
        
        
        for i, _ in enumerate(self.teams_playing):
            
            if self.teams_playing[i] is not None:
                #logging.debug(self.teams_playing[i])
                try:
                    team_name = team_names[self.teams_playing[i]]
                except IndexError:
                    
                    logging.debug("IndexError in create_SPIEL_elements")
                    
                    self.teams_playing = [None, None]
                    
                    no_match_active_label = ctk.CTkLabel(self.SPIEL_frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                    no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)#

                    if self.active_mode.get() == 1:
                        start_button = ctk.CTkButton(self.SPIEL_frame, text="Start", command=lambda : self.start_match_in_first_game_in_group_phase(), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), height=self.team_button_height)
                        start_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
                        self.updated_data.update({"activeMatchNumber": -1})
                    
                    return
                
            else:
                # Handle the case when self.teams_playing[i + 1] is None
                # For example, you can set team_name to an empty string
                
                self.teams_playing = [None, None]
                
                no_match_active_label = ctk.CTkLabel(self.SPIEL_frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                if self.active_mode.get() == 1:
                    start_button = ctk.CTkButton(self.SPIEL_frame, text="Start", command=lambda : self.start_match_in_first_game_in_group_phase(), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), height=self.team_button_height)
                    start_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
                    self.updated_data.update({"activeMatchNumber": -1})

                break
                
            self.team_id = self.teams_playing[i]
            
            if i == 0:
                team2_id = self.teams_playing[1]
            else:
                team2_id = self.teams_playing[0]

            self.setup_player_goals_per_match(self.team_id)
            
            # Initialize the dictionary for the current team
            self.spiel_buttons[self.team_id] = {}
                    
            self.for_team_frame = ctk.CTkFrame(self.SPIEL_frame, bg_color='#0e1718', fg_color='#0e1718')
            self.for_team_frame.pack(pady=10, anchor=tk.NW, side=tk.TOP, fill="both", padx=10, expand=True)
            
            # Create global scores buttons, one for up and one for down
            score_button_frame = ctk.CTkFrame(self.for_team_frame, bg_color='#142324', fg_color='#142324')
            score_button_frame.pack(pady=10, anchor=tk.E, side=tk.RIGHT, padx=10)
            
            score_button_up = ctk.CTkButton(score_button_frame, text="UP", command=lambda team=self.team_id, team2=team2_id: self.global_scored_a_point(team, team2, "UP"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
            score_button_up.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_label_var = tk.StringVar()
            #logging.debug("self.team_id", self.team_id, "team2_id", team2_id)
            score_label_var.set(self.read_goals_for_match_from_db(self.team_id, team2_id))
            
            score_label = ctk.CTkLabel(score_button_frame, text="None", textvariable=score_label_var, font=("Helvetica", self.team_button_font_size * 1.7, "bold"))
            score_label.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_button_down = ctk.CTkButton(score_button_frame, text="DOWN", command=lambda team=self.team_id, team2=team2_id: self.global_scored_a_point(team, team2, "DOWN"), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
            score_button_down.pack(pady=2, anchor=tk.N, side=tk.BOTTOM, expand=True, fill=tk.X)
            
            self.team_label = ctk.CTkLabel(self.for_team_frame, text=team_name, font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.team_label.pack(side=tk.LEFT, pady=2, anchor=tk.NW)
            
            self.spiel_buttons[self.team_id]["global"] = (self.for_team_frame, self.team_label, score_button_up, score_label_var, score_button_down)
            
            frame_frame = ctk.CTkFrame(self.for_team_frame, bg_color='#0e1718', fg_color='#0e1718')
            frame_frame.pack(side=tk.TOP, pady=0, anchor=tk.N)
            
            if i == 0:
                self.up_frame1 = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
                self.up_frame1.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

                self.down_frame1 = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
                self.down_frame1.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
            elif i == 1:
                self.up_frame2 = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
                self.up_frame2.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

                self.down_frame2 = ctk.CTkFrame(frame_frame, bg_color='#0e1718', fg_color='#0e1718')
                self.down_frame2.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
            
            
            if self.active_match == -1 and self.manual_select_active == False:
                continue
            
            joined_data = self.read_player_goals_per_match(self.team_id)
            
            #logging.debug("joined_data " + str(joined_data))
            
            if not joined_data or joined_data == ([], []):
                continue
            
            self.create_widgets_after_delay(joined_data, 0, i)

        
        teams_list = self.read_teamNames()
        teams_list.pop(0)
        #logging.debug("teams_list", teams_list)

        self.manual_team_select_1 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", self.team_button_font_size), 
            state=tk.DISABLED, 
            command=lambda event: self.on_team_select(event, 1, True),
            )
        self.manual_team_select_1.set("None")
        self.manual_team_select_1.pack(pady=10, side=tk.BOTTOM, anchor=tk.S, padx=10)
        #self.manual_team_select_1.bind("<<ComboboxSelected>>", lambda event, nr=1: self.on_team_select(event, nr))
        
        self.manual_team_select_2 = ctk.CTkComboBox(
            manual_manual_frame, 
            values=teams_list, 
            font=("Helvetica", self.team_button_font_size), 
            state=tk.NORMAL, 
            command=lambda event: self.on_team_select(event, 0, True),
            )
        self.manual_team_select_2.set("None")
        self.manual_team_select_2.pack(pady=10, side=tk.BOTTOM, anchor=tk.S, padx=10)
        #self.manual_team_select_2.bind("<<ComboboxSelected>>", lambda event, nr=0: self.on_team_select(event, nr))
        
        none_count = self.teams_playing.count(None)
        
        if none_count == 0 and self.teams_playing:
        
            ######################################################
            #Time Display
            #logging.debug(f"Time Display, here are the teams: {self.teams_playing} and the active_match: {self.active_match}")
            # Create a new frame
            time_frame = ctk.CTkFrame(manual_frame, fg_color='#142324', corner_radius=5)
            time_frame.pack(anchor=tk.SE, side=tk.RIGHT, padx=10, pady=10, expand=True)
            
            # Create a new frame for the first row
            time_frame1 = ctk.CTkFrame(time_frame, fg_color='#142324', corner_radius=5)
            time_frame1.pack(anchor=tk.S, side=tk.TOP, padx=10, pady=3, expand=True, fill=tk.X)

            time_current_match, time_next_match, _ = self.get_time_for_current_match(True)

            time_label = ctk.CTkLabel(time_frame1, text=f"Current Match Start: ", font=("Helvetica", self.team_button_font_size * 1.5))
            time_label.pack(side=tk.LEFT, pady=2, padx=10)

            self.current_time_label_wd = ctk.CTkLabel(time_frame1, text=f"{time_current_match}", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.current_time_label_wd.pack(side=tk.RIGHT, pady=2, fill=tk.X, padx=10)

            time_delay_frame = ctk.CTkFrame(time_frame, fg_color='#142324', corner_radius=5)
            time_delay_frame.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=3, expand=True, fill=tk.X)
            
            self.delay_label = ctk.CTkLabel(time_delay_frame, text=f"Delay: ", font=("Helvetica", self.team_button_font_size * 1.5))
            self.delay_label.pack(side=tk.LEFT, pady=2, padx=10, anchor=tk.S)
            
            self.delay_time_label = ctk.CTkLabel(time_delay_frame, text=f"0", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.delay_time_label.pack(side=tk.RIGHT, pady=2, padx=10, anchor=tk.SE)

            self.save_delay_time = 1
            
            self.delay_time_label.configure(font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
            
            # Create a new frame for the second row
            time_frame2 = ctk.CTkFrame(time_frame, fg_color='#142324', corner_radius=5)
            time_frame2.pack(anchor=tk.S, side=tk.BOTTOM, padx=10, pady=3, expand=True, fill=tk.X)

            time_label2 = ctk.CTkLabel(time_frame2, text=f"Next Match Start: ", font=("Helvetica", self.team_button_font_size * 1.5))
            time_label2.pack(side=tk.LEFT, pady=2, padx=10, anchor=tk.S)

            self.next_time_label_wd = ctk.CTkLabel(time_frame2, text=f"{time_next_match}", font=("Helvetica", self.team_button_font_size * 1.5, "bold"))
            self.next_time_label_wd.pack(side=tk.RIGHT, pady=2, padx=10, anchor=tk.SE)
            
            if self.active_match == 3 and self.active_mode.get() == 2:
                self.next_time_label_wd.configure(text="Disabled", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
                self.delay_time_label.configure(text="Disabled", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
            else:   
                self.watch_dog_process()

            ######################################################

        self.save_teams_playing_and_active_match()
        
        self.create_matches_labels(manual_frame)

        if none_count == 0 and self.teams_playing:
            self.configure_team_select(self.manual_team_select_2, tk.NORMAL, team_names[self.teams_playing[0]])
            self.configure_team_select(self.manual_team_select_1, tk.NORMAL, team_names[self.teams_playing[1]])
        elif none_count == 2:
            self.configure_team_select(self.manual_team_select_1, tk.DISABLED, "None")
        elif none_count == 1:
            self.configure_team_select(self.manual_team_select_1, tk.NORMAL, "None")
            self.configure_team_select(self.manual_team_select_2, tk.NORMAL, team_names[self.teams_playing[0]])    
    

    def create_widgets_after_delay(self, joined_data, index, team_i):
        if index < len(joined_data):
            player_info = joined_data[index]
            self.create_player_widgets(player_info, index, team_i)
            # Schedule the next iteration with after
            self.after(10, self.create_widgets_after_delay, joined_data, index + 1, team_i)
        else:
            # All widgets created, now update the layout
            self.update_idletasks()

    
    def create_player_widgets(self, player_info, i, team_i):
        player_name, player_number, goals, player_id, player_goals_per_match = player_info
        player_index = i 
        
        #player_id = self.get_player_id_from_player_name(player_name)
        #logging.debug("player_id", self.get_player_id_from_player_name(player_name))
        if team_i == 0:
            if i < 7:
                self.group_frame = ctk.CTkFrame(self.up_frame1, fg_color='#142324', corner_radius=10)
                self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
            else:
                self.group_frame = ctk.CTkFrame(self.down_frame1, fg_color='#142324', corner_radius=10)
                self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
        else:
            if i < 7:
                self.group_frame = ctk.CTkFrame(self.up_frame2, fg_color='#142324', corner_radius=10)
                self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
            else:
                self.group_frame = ctk.CTkFrame(self.down_frame2, fg_color='#142324', corner_radius=10)
                self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
        
        #self.group_frame = tk.Frame(self.for_team_frame, background="lightcoral")
        #self.group_frame.pack(side=tk.LEFT, padx=10, pady=10)

        playertext1 = ctk.CTkLabel(self.group_frame, text=f"Player {i}", font=("Helvetica", self.team_button_font_size))
        playertext1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
        
        playertext2_text = f"{player_name} - {player_number}"
        
        playertext2 = ctk.CTkLabel(master=self.group_frame, text=playertext2_text , font=("Helvetica", self.team_button_font_size, "bold"))
        playertext2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
        
        playertext3 = ctk.CTkLabel(self.group_frame, text=f"Tore {str(player_goals_per_match)}", font=("Helvetica", self.team_button_font_size))
        playertext3.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)

        playerbutton1 = ctk.CTkButton(self.group_frame, text="UP", command=lambda team=self.teams_playing[team_i], player_id1=player_id, player_index = player_index, player_name = player_name: self.player_scored_a_point(team, player_id1, player_index,  "UP", player_name), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size), height=self.team_button_height, width=self.team_button_width)  
        playerbutton1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
        
        playerbutton2 = ctk.CTkButton(self.group_frame, text="DOWN", command=lambda team=self.teams_playing[team_i], player_id1=player_id, player_index = player_index, player_name = player_name: self.player_scored_a_point(team, player_id1, player_index, "DOWN", player_name), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size), height=self.team_button_height, width=self.team_button_width)
        playerbutton2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X, padx=5)
    
    
        #logging.debug("team", team, "i", i)

        # Save the group_frame, playertext1, and playerbutton in each for loop with the team name as key
        self.spiel_buttons[self.teams_playing[team_i]][i] = (self.group_frame, playertext1, playertext2, playertext3, playerbutton1, playerbutton2)  # Use append for a list
        
        
    def setup_player_goals_per_match(self, team_id):
        active_match = self.active_match
        team_id = team_id
        #logging.debug(f"active_match: {active_match}, self.active_mode: {self.active_mode.get()}, self.teams_playing: {self.teams_playing}")

        if active_match == -1:
            #logging.exception("active_match is -1 in setup_player_goals_per_match")
            return

        if self.active_mode.get() == 1:
            colum = "playerPerMatchData"
        elif self.active_mode.get() == 2:
            colum = "playerPerMatchDataFinal"
        elif self.active_mode.get() == 3:
            colum = "playerPerMatchDataKO"

        # get the player names for the current team
        self.cursor.execute("SELECT playerName FROM playerData WHERE teamId = ? ORDER BY id ASC", (team_id,))
        player_names = set(row[0] for row in self.cursor.fetchall())

        # get the player names that exist in the playerPerMatchData table for the current match
        self.cursor.execute(f"SELECT playerName FROM {colum} WHERE matchId = ? ORDER BY id ASC", (active_match,))
        existing_player_names = set(str(row[0]) for row in self.cursor.fetchall())

        # find the player names that need to be inserted
        player_names_to_insert = player_names - existing_player_names

        # check if the player is in the {colum} table and if not, add it
        for player_name in player_names_to_insert:
            self.cursor.execute(f"INSERT INTO {colum} (playerName, matchId) VALUES (?, ?)", (player_name, active_match))
        self.connection.commit()
        
        
    def read_player_goals_per_match(self, team_id):
        active_match = self.active_match
        
        if active_match == -1:
            #logging.exception("active_match is -1 in setup_player_goals_per_match")
            return

        if self.active_mode.get() == 1:
            colum = "playerPerMatchData"
        elif self.active_mode.get() == 2:
            colum = "playerPerMatchDataFinal"
        elif self.active_mode.get() == 3:
            colum = "playerPerMatchDataKO"
            
            
        selectingQuery = f"""
            SELECT playerData.playerName, playerData.playerNumber, playerData.goals, playerData.id, {colum}.playerGoals 
            FROM playerData, {colum} 
            WHERE playerData.playerName = {colum}.playerName 
            AND {colum}.matchId = ? AND playerData.teamId = ?
            ORDER BY playerData.id ASC
        """
        
        playerData = self.cursor.execute(selectingQuery, (active_match, team_id)).fetchall()
        
        return playerData
   
    
    def read_player_goals_per_match_per_player(self, player_name):
        active_match = self.active_match
        
        if active_match == -1:
            #logging.exception("active_match is -1 in setup_player_goals_per_match")
            return

        if self.active_mode.get() == 1:
            colum = "playerPerMatchData"
        elif self.active_mode.get() == 2:
            colum = "playerPerMatchDataFinal"
        elif self.active_mode.get() == 3:
            colum = "playerPerMatchDataKO"
            
        selectingQuery = f"""
            SELECT playerGoals 
            FROM {colum} 
            WHERE playerName = ? AND matchId = ?
        """
        
        playerData = self.cursor.execute(selectingQuery, (player_name, active_match)).fetchone()
        
        if playerData is None:
            return 0
        
        return playerData[0]
    
    
    def save_fake_goals_for_match_for_player(self, player_name, goals):
        active_match = self.active_match
        
        if active_match == -1:
            #logging.exception("active_match is -1 in save_fake_goals_for_match_for_player")
            return

        if self.active_mode.get() == 1:
            colum = "playerPerMatchData"
        elif self.active_mode.get() == 2:
            colum = "playerPerMatchDataFinal"
        elif self.active_mode.get() == 3:
            colum = "playerPerMatchDataKO"
            
        updateQuery = f"""
            UPDATE {colum} 
            SET playerGoals = ? 
            WHERE playerName = ? AND matchId = ?
        """
        
        self.cursor.execute(updateQuery, (goals, player_name, active_match))
        self.connection.commit()
        
        
    def reset_player_per_match_data(self):
        # Drop the table
        self.cursor.execute("DROP TABLE IF EXISTS playerPerMatchData")
        self.connection.commit()

        # Recreate the table
        playerPerMatchDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchData (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES matchData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataTableCreationQuery)
        self.connection.commit()   
        
        self.cursor.execute("DROP TABLE IF EXISTS playerPerMatchDataFinal")
        self.connection.commit()
        
        playerPerMatchDataFinalTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchDataFinal (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES finalMatchesData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataFinalTableCreationQuery)
        self.connection.commit()

        self.cursor.execute("DROP TABLE IF EXISTS playerPerMatchDataKO")

        playerPerMatchDataKOTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerPerMatchDataKO (
            id INTEGER PRIMARY KEY,
            matchId INTEGER REFERENCES matchData(matchId),
            playerName INTEGER REFERENCES playerData(playerName),
            playerGoals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerPerMatchDataKOTableCreationQuery)
        self.connection.commit()

    
    def configure_team_select(self, team_select, state, team_name):
        team_select.configure(state=state)
        team_select.set(team_name)
    
    
    def watch_dog_process(self):
        if self.teams_playing.count(None) == 0 and self.watch_dog_process_can_be_active:
            delay_time = self.calculate_delay()
            if self.manual_select_active_sure == False and self.manual_select_active == False:
                if delay_time < 0:
                    if self.save_delay_time != 0 or self.save_delay_time == 2:
                        self.save_delay_time = 0
                        self.delay_time_save_for_blinking = 1
                        # Change the delay time label color to red
                        self.delay_time_label.configure(font=("Helvetica", self.team_button_font_size * 1.6, "bold"), text_color="red", fg_color="orange")
                        
                        #self.after(1000, self.change_back_label_color, self.delay_time_label, "#142324")
                        if not self.blink_label(self.delay_time_label, "#142324", "orange", 6):
                            logging.info("Ended blinking because of save_delay_time")
                            return
                        
                    elif abs(round(delay_time)) % 30 == 0 and self.delay_time_save_for_blinking == 1:
                        self.delay_time_save_for_blinking = 0
                        if not self.blink_label(self.delay_time_label, "#142324", "orange", 6):
                            logging.info("Ended blinking because of delay_time_save_for_blinking")
                            return

                        
                    else:
                        self.delay_time_save_for_blinking = 1
                        
                    #logging.debug("delay_time", delay_time, "abs(delay_time) % 30", abs(round(delay_time)) % 30)
                        
                else:
                    if self.save_delay_time != 1 or self.save_delay_time == 2:
                        self.save_delay_time = 1
                        
                        self.delay_time_label.configure(font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
                
                # If the delay time is over 0
                if delay_time < 0:
                    
                    delay_time = abs(delay_time)
                    
                    # Format the delay time as 'Min:Sec'
                    delay_min, delay_sec = divmod(delay_time, 60)
                    delay_time_str = f"{int(delay_min):02d}:{int(delay_sec):02d}"

                    # Update the delay time label text
                    self.delay_time_label.configure(text=delay_time_str)

                else:
                    
                    delay_time = abs(delay_time)
                    
                    # Format the delay time as 'Min:Sec'
                    delay_min, delay_sec = divmod(delay_time, 60)
                    delay_time_str = f"- {int(delay_min):02d}:{int(delay_sec):02d}"

                    # Update the delay time label text
                    self.delay_time_label.configure(text=delay_time_str)

                # Call this function again after 1 second (1000 milliseconds)
                
            else:
                self.delay_time_label.configure(text="Disabled", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
                self.current_time_label_wd.configure(text="Disabled", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
                self.next_time_label_wd.configure(text="Disabled", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), text_color="#21a621")
                self.watch_dog_process_can_be_active = False
            
            
            self.delay_time_label.after(1000, self.watch_dog_process)


    def blink_label(self, label, original_color, blink_color="orange", blink_times=5):
        if blink_times > 0 and self.manual_select_active_sure == False and self.manual_select_active == False:
            try:
                label.configure(fg_color=blink_color if blink_times % 2 == 0 else original_color)
            except:
                return False
            self.after(1000, self.blink_label, label, original_color, blink_color, blink_times-1)
            return True
        else:
            try:
                label.configure(fg_color=original_color)
            except:
                return False
            return True
            
            
    def change_back_label_color(self, label, label_color):
        label.configure(fg_color=label_color)


    def calculate_delay(self):
        # Get the current time
        current_time = datetime.datetime.now()

        # Get the start time for the next match
        _, next_match_start_time_str, day_change = self.get_time_for_current_match(True)
        # logging.debug("day_change", day_change)
        next_match_start_time = datetime.datetime.strptime(next_match_start_time_str, '%H:%M')

        # Make sure both times are on the same date
        next_match_start_time = next_match_start_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)

        # If the match is on the next day, add one day to next_match_start_time
        if day_change:
            next_match_start_time += datetime.timedelta(days=1)

        # Calculate the delay in seconds
        delay = (next_match_start_time - current_time).total_seconds()

        #logging.debug("delay in calculate_delay", delay)
        return delay


    def get_time_for_current_match(self, next_match=False):
        #get the number of entrys in the matchData table
        self.cursor.execute("SELECT COUNT(*) FROM matchData")
        match_count = self.cursor.fetchone()[0]
        timeinterval = int(self.time_interval.get().replace("m", ""))
        
        if self.active_mode.get() == 1:
            # Get the starttime from settings
            starttime_str = str(self.start_time.get())
            starttime = datetime.datetime.strptime(starttime_str, '%H:%M')

            # get the number of the active match
            active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1])
            
            if active_match < 0:
                if next_match:
                    return "00:00", "00:00", False
                return "00:00"

            # calculate the time for the current match
            current_match_time = starttime + datetime.timedelta(minutes=timeinterval * active_match)

            next_match_start_time = current_match_time + datetime.timedelta(minutes=timeinterval)

            #logging.debug("next_match_start_time", next_match_start_time, "current_match_time", current_match_time, "next_match_start_time.day", next_match_start_time.day, "current_match_time.day", current_match_time.day)

            if next_match and active_match <= match_count:
                if next_match_start_time.day != starttime.day:
                    return current_match_time.strftime('%H:%M'), next_match_start_time.strftime('%H:%M'), True
                return current_match_time.strftime('%H:%M'), (current_match_time + datetime.timedelta(minutes=timeinterval)).strftime('%H:%M'), False
            # return the time in 00:00 format
            return current_match_time.strftime('%H:%M')      
        
        elif self.active_mode.get() == 2:
            # Get the starttime from settings
            starttime_str = str(self.start_time.get())
            starttime = datetime.datetime.strptime(starttime_str, '%H:%M')

            final_match_active = 0
            
            # get the number of the active match
            active_match = self.active_match
            
            active_match += 1
            
            if active_match > 3:
                active_match = 3
                final_match_active = 1

            # get the interval for the final matches
            time_interval_final_matches = int(self.time_intervalFM.get().replace("m", ""))
            
            # get time pause final matches
            pause_between_final_matches = int(self.time_pause_before_FM.get().replace("m", ""))
            
            # calculate the time for the current match
            time_interval_for_only_the_final_match = int(self.time_interval_for_only_the_final_match.get().replace("m", ""))

            timeIntervalKO = int(self.time_intervalKO.get().replace("m", ""))
            
            #logging.debug(f"active_match: {active_match}, time_interval_final_matches: {time_interval_final_matches}, timeinterval: {timeinterval}, match_count: {match_count}, pause_between_final_matches: {pause_between_final_matches}")

            # calculate the time for the current match
            if self.there_is_an_ko_phase.get() == 0:
                current_match_time = starttime + datetime.timedelta(minutes=(final_match_active * time_interval_for_only_the_final_match) + (time_interval_final_matches * active_match) + (timeinterval * match_count) + pause_between_final_matches)
            else:
                self.cursor.execute("SELECT COUNT(*) FROM KOMatchesData")
                ko_match_count = self.cursor.fetchone()[0]
                
                current_match_time = starttime + datetime.timedelta(minutes=(final_match_active * time_interval_for_only_the_final_match) + (time_interval_final_matches * active_match) + (timeinterval * match_count) + (timeIntervalKO * ko_match_count) + pause_between_final_matches)
    

            if next_match:
                next_match_start_time = current_match_time + datetime.timedelta(minutes=time_interval_final_matches)                
                if next_match_start_time.day != starttime.day:
                    return current_match_time.strftime('%H:%M'), next_match_start_time.strftime('%H:%M'), True
                return current_match_time.strftime('%H:%M'), next_match_start_time.strftime('%H:%M'), False
            # return the time in 00:00 format
            return current_match_time.strftime('%H:%M')
    
        elif self.active_mode.get() == 3:
            # Get the starttime from settings
            starttime_str = str(self.start_time.get())
            starttime = datetime.datetime.strptime(starttime_str, '%H:%M')

            # get the number of the active match
            active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1])
            
            if active_match < 0:
                if next_match:
                    return "00:00", "00:00", False
                return "00:00"

            # get the time interval from settings
            timeIntervalKO = int(self.time_intervalKO.get().replace("m", ""))

            # calculate the time for the current match
            current_match_time = starttime + datetime.timedelta(minutes=timeIntervalKO * active_match + timeinterval * match_count) 

            next_match_start_time = current_match_time + datetime.timedelta(minutes=timeIntervalKO)

            #logging.debug("next_match_start_time", next_match_start_time, "current_match_time", current_match_time, "next_match_start_time.day", next_match_start_time.day, "current_match_time.day", current_match_time.day)

            if next_match and active_match <= match_count:
                if next_match_start_time.day != starttime.day:
                    return current_match_time.strftime('%H:%M'), next_match_start_time.strftime('%H:%M'), True
                return current_match_time.strftime('%H:%M'), (current_match_time + datetime.timedelta(minutes=timeinterval)).strftime('%H:%M'), False
            
            # return the time in 00:00 format
            return current_match_time.strftime('%H:%M')
        
    
    def on_team_select(self, event, nr, manual_select=False):
        #logging.debug("on_team_select")
        #logging.debug(event)
        #selected_team = event.widget.get()
        selected_team = event
        
        if manual_select:
            self.manual_select_active = True
        
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
            if self.active_mode.get() == 1 or self.active_mode.get() == 2 or self.active_mode.get() == 3:
                self.active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1])
        
        #logging.debug("self.teams_playing", self.teams_playing)
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.configure(state=tk.NORMAL)
            self.manual_team_select_1.set("None")
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
            self.active_match = -1
        
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.configure(tk.DISABLED)
            self.manual_team_select_1.set("None")
            self.manual_team_select_2.set("None")
            self.active_match = -1
        
        
        self.reload_spiel_button_command(True)
        
        
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
        self.SPIEL_frame.destroy()
        #self.SPIEL_frame.grid_forget()
        #self.SPIEL_frame.pack_forget()
        self.SPIEL_frame = ctk.CTkFrame(self, fg_color='#0e1718', bg_color='#0e1718')
        
        if show_frame:
            self.show_frame(self.SPIEL_frame)
        self.watch_dog_process_can_be_active = True
        
        self.create_SPIEL_elements()

        
    def player_scored_a_point(self, teamID, player_id, player_index, direction="UP", player_name=""):
        
        self.cache_vars["getbestscorer_changed_using_var"] = True
        
        # Get the current score
        current_goals = self.read_player_stats(teamID, True, False, player_id)[0][2]
        
        fake_current_goals = self.read_player_goals_per_match_per_player(player_name)
        
        # Update the score
        if direction == "UP":
            current_goals += 1
            fake_current_goals += 1
        else:
            current_goals -= 1
            fake_current_goals -= 1

        if current_goals < 0:
            current_goals = 0
            return
        
        # Update the score label
        self.spiel_buttons[teamID][player_index][3].configure(text=f"Tore {fake_current_goals}")
        self.update_idletasks()
        
        # Update the database
        self.cursor.execute(
            "UPDATE playerData SET goals = ? WHERE teamId = ? AND id = ?",
            (current_goals, teamID, player_id)
        )
        
        self.save_fake_goals_for_match_for_player(player_name, fake_current_goals)
        
        # Commit the changes to the database
        self.connection.commit()
        

    def create_matches_labels(self, frame):
        
        self.manual_select_active_sure = False
        
        matches = self.calculate_matches()
        
        self.spiel_select_frame = ctk.CTkFrame(frame, fg_color='#142324', corner_radius=5)
        self.spiel_select_frame.pack(pady=10, padx=10, anchor=tk.SW, side=tk.LEFT)
        
        width = self.screenwidth / 9
        
        
        self.cursor.execute("SELECT COUNT(*) FROM matchData")
        match_count = self.cursor.fetchone()[0]
        
        if self.active_match >= match_count:
            self.active_match = -1
            self.teams_playing = [None, None]

        if self.active_mode.get() == 1:
            self.spiel_select = ctk.CTkComboBox(self.spiel_select_frame, font=("Helvetica", self.team_button_font_size * 1.2), width=width, values=[""], command=lambda event: self.on_match_select(event, matches))
            self.spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N, padx=10)

            values_list = self.get_values_list_mode1(matches)
            self.spiel_select.configure(values=values_list)
            #logging.debug("active_match in create_matches_labels", self.active_match)
            self.active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1])
                
            if self.active_match >= 0:
                self.spiel_select.set(values_list[self.active_match])
                self.manual_select_active = False
                #print("Case 1", "self.active_match", self.active_match, "values_list", values_list)

            elif (values_list != [] and self.teams_playing.count(None) != 0) or (values_list != [] and self.manual_select_active == False and self.active_match != -1):
                #print("Case 2", "self.active_match", self.active_match, "values_list", values_list)
                return

            elif self.manual_select_active == False:
                #print("Case 3", "self.active_match", self.active_match, "values_list", values_list)
                self.active_match = -1
                self.teams_playing = [None, None]

                self.updated_data.update({"activeMatchNumber": -1})
                
                if match_count > 0:
                    self.reload_spiel_button_command()
                
                self.updated_data.update({"activeMatchNumber": -1})
                
                try:
                # Create an red label on the frame to show that no match is active

                    #no_match_active_label = ctk.CTkLabel(frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                    #no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                    #start_button = ctk.CTkButton(self.frame, text="Start", command=lambda : self.start_match_in_first_game_in_group_phase(), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), height=self.team_button_height)
                    #start_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
                    self.updated_data.update({"activeMatchNumber": -1})

                except:
                    pass
                
            else:
                #print("Case 4", "self.active_match", self.active_match, "values_list", values_list)
                self.active_match = -1
                logging.info("Manual Select Active")
                
                manual_select_label = ctk.CTkLabel(frame, text="Manual Select Active", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), fg_color="red")
                manual_select_label.place(relx=0.32, rely=0.9, anchor=tk.CENTER)
                
                self.manual_select_active_sure = True
            
        elif self.active_mode.get() == 2:
            self.spiel_select = ctk.CTkComboBox(self.spiel_select_frame, font=("Helvetica", self.team_button_font_size * 1.2), width=width, values=[""], command=lambda event: self.on_match_select(event, matches))
            self.spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N, padx=10)

            values_list, active_match = self.get_values_list_mode2()
            self.spiel_select.configure(values=values_list)
            if active_match >= 0:
                if len(values_list) > active_match:
                    self.spiel_select.set(values_list[active_match])
                    self.manual_select_active = False
                else:
                    self.active_match = -1
                    self.teams_playing = [None, None]
                    # Create an red label on the frame to show that no match is active
                    no_match_active_label = ctk.CTkLabel(frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                    no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            elif (values_list != [] and self.teams_playing.count(None) != 0) or (values_list != [] and self.manual_select_active == False):
                self.on_match_select(values_list[0], matches)
                self.manual_select_active = False
                return
            elif self.manual_select_active == False:
                self.active_match = -1
                self.teams_playing = [None, None]
                
                # Create an red label on the frame to show that no match is active
                no_match_active_label = ctk.CTkLabel(frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
            else:
                self.active_match = -1
                logging.info("Manual Select Active")
                
                manual_select_label = ctk.CTkLabel(frame, text="Manual Select Active", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), fg_color="red")
                manual_select_label.place(relx=0.32, rely=0.9, anchor=tk.CENTER)
                
                self.manual_select_active_sure = True

        elif self.active_mode.get() == 3:
            values_list, pairedKoMatches = self.get_values_list_mode3()

            self.spiel_select = ctk.CTkComboBox(self.spiel_select_frame, font=("Helvetica", self.team_button_font_size * 1.2), width=width, values=[""], command=lambda event: self.on_match_select(event, pairedKoMatches))
            self.spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N, padx=10)
            self.spiel_select.configure(values=values_list)

            self.active_match = self.get_active_match(self.teams_playing[0], self.teams_playing[1])
                
            if self.active_match >= 0:
                self.spiel_select.set(values_list[self.active_match])
                self.manual_select_active = False
            elif (values_list != [] and self.teams_playing.count(None) != 0) or (values_list != [] and self.manual_select_active == False):
                self.on_match_select(values_list[0], pairedKoMatches)
                self.manual_select_active = False
                return
            elif self.manual_select_active == False:
                self.active_match = -1
                self.teams_playing = [None, None]
                
                if match_count > 0:
                    self.reload_spiel_button_command()
                
                # Create an red label on the frame to show that no match is active
                no_match_active_label = ctk.CTkLabel(frame, text="No Match Active", font=("Helvetica", self.team_button_font_size * 2, "bold"), fg_color="red")
                no_match_active_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
            else:
                self.active_match = -1
                logging.info("Manual Select Active")
                
                manual_select_label = ctk.CTkLabel(frame, text="Manual Select Active", font=("Helvetica", self.team_button_font_size * 1.5, "bold"), fg_color="red")
                manual_select_label.place(relx=0.32, rely=0.9, anchor=tk.CENTER)
                
                self.manual_select_active_sure = True
            
        next_match_button = ctk.CTkButton(self.spiel_select_frame, text="Next Match", command=lambda : self.next_previous_match_button(self.spiel_select, matches), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
        next_match_button.pack(pady=10, padx=10, side=tk.RIGHT, anchor=tk.SE)
        previous_match_button = ctk.CTkButton(self.spiel_select_frame, text="Previous Match", command=lambda : self.next_previous_match_button(self.spiel_select, matches, False), fg_color="#34757a", hover_color="#1f4346", font=("Helvetica", self.team_button_font_size * 1.2, "bold"), height=self.team_button_height, width=self.team_button_width)
        previous_match_button.pack(pady=10, padx=10, side=tk.LEFT, anchor=tk.SW)

        self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})

        self.save_teams_playing_and_active_match()


    def start_match_in_first_game_in_group_phase(self):
        if self.active_mode.get() == 1:
            values_list = self.get_values_list_mode1(self.calculate_matches())
            self.on_match_select(values_list[0], self.calculate_matches())
            self.manual_select_active = False
            self.show_frame(self.SPIEL_frame) # Fix for player doubleing
        else:
            logging.error("The active mode is not 1")

    
    def get_values_list_mode1(self, matches):
        values_list = []
        for match in matches:
            values_list.append(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])
        return values_list
    

    def get_values_list_mode2(self):
        self.cache_vars["getfinalmatches_changed_using_var"] = True
        
        values_list = []
        self.get_teams_for_final_matches()
        endteam1 = getattr(self, 'endteam1', [None, None])
        endteam2 = getattr(self, 'endteam2', [None, None])
        endteam3 = getattr(self, 'endteam3', [None, None])
        endteam4 = getattr(self, 'endteam4', [None, None])
        values_list.append(f"Spiel 1 Halb: {endteam1[1]} vs {endteam3[1]}")
        values_list.append(f"Spiel 2 Halb: {endteam2[1]} vs {endteam4[1]}")
        values_list.append(self.get_spiel_um_platz_3(endteam1, endteam3, endteam2, endteam4))
        values_list.append(self.get_final_match(endteam1, endteam3, endteam2, endteam4))
        
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
            goles_spiele.append([self.read_goals_for_match_from_db(self.endteam1[0], self.endteam3[0], 2), self.read_goals_for_match_from_db(self.endteam3[0], self.endteam1[0], 2)])
            goles_spiele.append([self.read_goals_for_match_from_db(self.endteam2[0], self.endteam4[0], 2), self.read_goals_for_match_from_db(self.endteam4[0], self.endteam2[0], 2)])
            goles_spiele.append([self.read_goals_for_match_from_db(self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0], 2), self.read_goals_for_match_from_db(self.spiel_um_platz_3[1][0], self.spiel_um_platz_3[0][0], 2)])
            goles_spiele.append([self.read_goals_for_match_from_db(self.final_match_teams[0][0], self.final_match_teams[1][0], 2), self.read_goals_for_match_from_db(self.final_match_teams[1][0], self.final_match_teams[0][0], 2)])

            if self.active_mode.get() == 2:
                try:
                    self.updated_data.update("finalMatches", get_data_for_website(6))
                except:
                    pass
            else:
                #only send nones in the same structure
                self.updated_data.update({
                    "finalMatches": [
                        [None, None, None, None, [None, None, None, None]],
                        [None, None, None, None, [None, None, None, None]],
                        [None, None, None, None, [None, None, None, None]],
                        [None, None, None, None, [None, None, None, None]]
                    ]
                })
        return values_list, self.active_match
    

    def get_values_list_mode3(self):
        #self.cache_vars["getfinalmatches_changed_using_var"] = True
        values_list = []
        pairedKOmatches = self.get_teams_for_KO_matches()
        for i, match in enumerate(pairedKOmatches):
            values_list.append(f" {i+1}: {match[0][1]} vs {match[1][1]}")
        
        self.save_KO_matches_in_DB(pairedKOmatches)

        return values_list, pairedKOmatches


    def get_active_match(self, team1, team2):
        #get the active match by looking in the matches databesa and where these teams play together you get the match number
        
        if self.active_mode.get() == 1:
            getActiveMatch = """
            SELECT matchId FROM matchData
            WHERE team1Id = ? AND team2Id = ?
            """
            self.cursor.execute(getActiveMatch, (team1, team2))
            active_match = self.cursor.fetchone()
            if active_match != None:
                return active_match[0] -1
            else:
                return -1
        elif self.active_mode.get() == 2:
            getActiveMatch = """
            SELECT matchId FROM finalMatchesData
            WHERE team1Id = ? AND team2Id = ?
            """
            self.cursor.execute(getActiveMatch, (team1, team2))
            active_match = self.cursor.fetchone()
            if active_match != None:
                return active_match[0] -1
            else:
                return -1
        
        elif self.active_mode.get() == 3:
            getActiveMatch = """
            SELECT matchId FROM KOMatchesData
            WHERE team1Id = ? AND team2Id = ?
            """
            self.cursor.execute(getActiveMatch, (team1, team2))
            active_match = self.cursor.fetchone()
            if active_match != None:
                return active_match[0] -1
            else:
                return -1
    
    
    def get_teams_for_KO_matches(self):
        getAllTeamsByPointsAndGoalDifferenceDesc = """
        SELECT id, teamName, goals, goalsReceived, (goals - goalsReceived) as goalDifference FROM teamData
        WHERE groupNumber = 1
        ORDER BY points DESC, goalDifference DESC, id ASC
        """
        getAllTeamsByPointsAndGoalDifferenceAsc = """
        SELECT id, teamName, goals, goalsReceived, (goals - goalsReceived) as goalDifference FROM teamData
        WHERE groupNumber = 2
        ORDER BY points ASC, goalDifference ASC, id DESC
        """

        self.cursor.execute(getAllTeamsByPointsAndGoalDifferenceDesc)
        teamsDesc = self.cursor.fetchall()

        self.cursor.execute(getAllTeamsByPointsAndGoalDifferenceAsc)
        teamsAsc = self.cursor.fetchall()

        # Pair the teams together and flatten the list
        paired_teams = [pair for pair in zip(teamsDesc, teamsAsc)]

        while len(paired_teams) < 4:
            paired_teams.append((0, 'No Team', 0, 0, 0))

        return paired_teams
            

    def get_top_two_teams(self, group_number):
        query = """
        SELECT id, teamName, goals, goalsReceived, (goals - goalsReceived) as goalDifference FROM teamData
        WHERE groupNumber = ?
        ORDER BY points DESC, goalDifference DESC, id ASC
        LIMIT 2
        """
        self.cursor.execute(query, (group_number,))
        result = self.cursor.fetchall()

        # Check if the result has less than 2 teams
        while len(result) < 2:
            # Append a zero tuple
            result.append((0, 'No Team', 0, 0, 0))

        return result


    def get_teams_for_final_matches(self):
        teams1 = self.get_top_two_teams(1)
        teams2 = self.get_top_two_teams(2)

        if teams1 and teams2:
            self.endteam1, self.endteam2 = teams1
            self.endteam4, self.endteam3 = teams2
             

    def get_spiel_um_platz_3(self, team1, team2, team3, team4):
        #get the best two teams from the database(with most points)
        getGoles1 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 1
        ORDER BY matchId ASC
        """
        
        getGoles2 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 2
        ORDER BY matchId ASC
        """
        self.cursor.execute(getGoles1)
        goles1 = self.cursor.fetchone()
        self.cursor.execute(getGoles2)
        goles2 = self.cursor.fetchone()
        
        self.spiel_um_platz_3 = []
        
        if goles1 != None and goles2 != None:

            if goles1[1] <= goles1[0]:
                self.spiel_um_platz_3.append(team2)
            else:
                self.spiel_um_platz_3.append(team1)
                
            if goles2[1] <= goles2[0]:
                self.spiel_um_platz_3.append(team4)
            else:
                self.spiel_um_platz_3.append(team3)
        
        #logging.debug everything
        logging.debug(f"self.spiel_um_platz_3: {self.spiel_um_platz_3}, team1: {team1}, team2: {team2}, team3: {team3}, team4: {team4}, goles1: {goles1}, goles2: {goles2}")
        if self.spiel_um_platz_3 != []:
            return f"Spiel um Platz 3: {self.spiel_um_platz_3[0][1]} vs {self.spiel_um_platz_3[1][1]}"
        else:
            return "Spiel um Platz 3: None vs None"
        
        
    def get_final_match(self, team1, team2, team3, team4):
        #get the best two teams from the database(with most points)
        getGoles1 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 1
        ORDER BY matchId ASC
        """
        
        getGoles2 = """
        SELECT team1Goals, team2Goals FROM finalMatchesData
        WHERE matchId = 2
        ORDER BY matchId ASC
        """
        
        self.final_match_teams = []
        
        self.cursor.execute(getGoles1)
        goles1 = self.cursor.fetchone()
        self.cursor.execute(getGoles2)
        goles2 = self.cursor.fetchone()
        
        if goles1 != None and goles2 != None:

            if goles1[0] >= goles1[1]:
                self.final_match_teams.append(team1)
            else:
                self.final_match_teams.append(team2)
                
            if goles2[0] >= goles2[1]:
                self.final_match_teams.append(team3)
            else:
                self.final_match_teams.append(team4)
            
        if self.final_match_teams != []:
            return f"Finale: {self.final_match_teams[0][1]} vs {self.final_match_teams[1][1]}"
        else:
            return "Finale: None vs None"
        
        
    def save_active_match_in_final_phase(self, team1id, team2id):

        #logging.debug(f"team1id: {team1id}, team2id: {team2id}, self.active_match: {self.active_match}")
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


    def save_KO_matches_in_DB(self, pairedKOmatches):
        insertKOmatch = """
        INSERT OR IGNORE INTO KOMatchesData (matchId, team1Id, team2Id)
        VALUES (?, ?, ?)
        """
        updateKOmatch = """
        UPDATE KOMatchesData
        SET team1Id = ?, team2Id = ?
        WHERE matchId = ?
        """
        insert_data = [(i+1, match[0][0], match[1][0]) for i, match in enumerate(pairedKOmatches)]
        update_data = [(match[0][0], match[1][0], i+1) for i, match in enumerate(pairedKOmatches)]
        
        self.cursor.executemany(insertKOmatch, insert_data)
        self.cursor.executemany(updateKOmatch, update_data)
        self.connection.commit()
        
    
    def on_match_select(self, event, matches=[]):
        selected_match = event
        logging.debug(f"on_match_select selected_match: {selected_match}, matches: {matches}")
        logging.debug(f"selected_match: {selected_match}, matches: {matches}")
        if self.active_mode.get() == 1 and matches != []:
            match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(selected_match)
            #logging.debug("match_index", match_index)
            # Get the teams playing in the selected match and if there are none, set teams_playing to None
            team_names = self.read_teamNames()
            
            team1_index = team_names.index(matches[match_index]["teams"][0])
            team2_index = team_names.index(matches[match_index]["teams"][1])

            if team1_index and team2_index:
                self.teams_playing = [team1_index, team2_index]
            else:
                self.teams_playing = [None, None]
                
            self.active_match = match_index
            
            self.save_games_played_in_db(match_index)

            self.cache_vars["getgames_changed_using_var"] = True

            self.updated_data.update({"Games": get_data_for_website(2)})
            self.updated_data.update({"activeMatchNumber": self.active_match})
            
        elif self.active_mode.get() == 2:
            #logging.debug("self.spiel_um_platz_3", self.spiel_um_platz_3)
            #logging.debug("self.final_match_teams", self.final_match_teams)
            if selected_match == "Spiel 1 Halb: " + self.endteam1[1] + " vs " + self.endteam3[1]:
                self.teams_playing = [self.endteam1[0], self.endteam3[0]]
                self.active_match = 0
                self.save_active_match_in_final_phase(self.endteam1[0], self.endteam3[0])
            elif selected_match == "Spiel 2 Halb: " + self.endteam2[1] + " vs " + self.endteam4[1]:
                self.teams_playing = [self.endteam2[0], self.endteam4[0]]
                self.active_match = 1 
                self.save_active_match_in_final_phase(self.endteam2[0], self.endteam4[0])
            elif selected_match.startswith("Spiel um Platz 3: ") and self.spiel_um_platz_3 != []:
                self.get_spiel_um_platz_3(self.endteam1, self.endteam3, self.endteam2, self.endteam4)
                if self.spiel_um_platz_3[0][0] != None and self.spiel_um_platz_3[1][0] != None:
                    self.teams_playing = [self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0]]
                    self.active_match = 2
                    self.save_active_match_in_final_phase(self.spiel_um_platz_3[0][0], self.spiel_um_platz_3[1][0])
                else:
                    self.teams_playing = [None, None]
                    self.active_match = 2
                    self.save_active_match_in_final_phase(None, None)
                
            elif selected_match.startswith("Finale: ") and self.final_match_teams != []:
                self.get_final_match(self.endteam1, self.endteam3, self.endteam2, self.endteam4)
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
            #logging.debug("self.active_matchon_match_select", self.active_match)
            
            #self.save_games_played_in_db(self.active_match)
            
            self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
        
        elif self.active_mode.get() == 3:
            match_index = int(selected_match.split(":")[0]) - 1
            #logging.debug("match_index", match_index)
            # Get the teams playing in the selected match and if there are none, set teams_playing to None
            team_names = self.read_teamNames()

            team1_index = team_names.index(matches[match_index][0][1])
            team2_index = team_names.index(matches[match_index][1][1])

            if team1_index and team2_index:
                self.teams_playing = [team1_index, team2_index]
            else:
                self.teams_playing = [None, None]
                
            self.active_match = match_index
            
            
            #self.updated_data.update({"Games": get_data_for_website(2)})
            #self.updated_data.update({"activeMatchNumber": self.active_match})
        
        self.reload_spiel_button_command()
        
        self.show_frame(self.SPIEL_frame)
        
    
    def next_previous_match_button(self, spiel_select, matches, next_match=True):
        self.cache_vars["getfinalmatches_changed_using_var"] = True
        if self.active_mode.get() == 1:
            try:
                # Get the current match index
                current_match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(spiel_select.get()) + 1

                
                # Calculate the new match index
                new_match_index = current_match_index + 1 if next_match else current_match_index - 1
                if new_match_index > len(matches):
                    if self.there_is_an_ko_phase.get() == 0:
                        result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the end of the matches. Do you want activate the pause and the final matches?")
                        if result:
                            self.pause_mode.set(1)
                            self.on_pause_switch_change()
                            self.active_mode.set(2)
                            self.save_active_mode_in_db()
                            values_list, active_match = self.get_values_list_mode2()
                            self.on_match_select(values_list[0])
                            self.update_idletasks()
                            self.update()
                            self.cache_vars["getkomatches_changed_using_var"] = True
                            self.updated_data.update({"KOMatches": get_data_for_website(8)})
                            
                            self.cache_vars["getfinalmatches_changed_using_var"] = True
                            self.updated_data.update({"finalMatches": get_data_for_website(6)})
                            return
                        else:
                            return
                    elif self.there_is_an_ko_phase.get() == 1:
                        result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the end of the matches. Do you want to select the first KO match?")
                        if result:
                            self.active_mode.set(3)
                            self.save_active_mode_in_db()
                            values_list, pairedKoMatches = self.get_values_list_mode3()
                            self.on_match_select(values_list[0], pairedKoMatches)
                            self.save_teams_playing_and_active_match()
                            #self.reload_spiel_button_command()
                            self.show_frame(self.SPIEL_frame)
                            new_match_index = max(1, min(new_match_index, len(matches)))
                            self.save_games_played_in_db(new_match_index - 1)
                            self.cache_vars["getkomatches_changed_using_var"] = True
                            self.updated_data.update({"KOMatches": get_data_for_website(8)})

                            return
                        else:
                            return
                    
                if new_match_index == 0 and next_match == False and self.active_mode.get() == 1:
                    result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the beginning of the matches. Do you want to select no match?")
                    if result:
                        self.active_match = -1
                        self.teams_playing = [None, None]
                        self.save_teams_playing_and_active_match()
                        self.reload_spiel_button_command()
                        self.show_frame(self.SPIEL_frame)
                        return
                    else:
                        return


                # Ensure the new index is within bounds
                new_match_index = max(1, min(new_match_index, len(matches)))
                self.save_games_played_in_db(new_match_index - 1)

                # Get the teams playing in the selected match
                team_names = self.read_teamNames()
                teams_playing = [team_names.index(matches[new_match_index - 1]["teams"][0]), team_names.index(matches[new_match_index - 1]["teams"][1])] if new_match_index > 0 else [None, None]
                
                self.active_match = new_match_index - 1

                # Update the buttons
                self.teams_playing = teams_playing
                self.reload_spiel_button_command()
                self.show_frame(self.SPIEL_frame)

                self.cache_vars["getgames_changed_using_var"] = True
                
                self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
                self.updated_data.update({"Games": get_data_for_website(2)})
                

                # logging.debug statements
                logging.debug(f"current_match_index: {current_match_index}")
                logging.debug(f"new_match_index: {new_match_index}")
                logging.debug(f"teams_playing: {teams_playing}")
                
            except ValueError:
                # Handle the case where the selected match is not found in the list
                logging.debug("Selected match not found in the list.")
                
                values_list = self.get_values_list_mode1(matches)
                
                self.on_match_select(values_list[0], matches)
                
        elif self.active_mode.get() == 2:
            if next_match:
                if self.active_match < 3:
                    self.active_match += 1
            else:
                if self.active_match > 0:
                    self.active_match -= 1
                else:
                    if self.there_is_an_ko_phase.get() == 0:
                        result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the beginning of the final matches. Do you want to select the last match of the group phase?")
                        if result:
                            self.active_mode.set(1)
                            self.save_active_mode_in_db()
                            values_list = self.get_values_list_mode1(matches)
                            self.on_match_select(values_list[-1], matches)
                            self.save_teams_playing_and_active_match()
                            self.show_frame(self.SPIEL_frame)
                            self.cache_vars["getkomatches_changed_using_var"] = True
                            self.updated_data.update({"KOMatches": get_data_for_website(8)})
                            
                            self.cache_vars["getfinalmatches_changed_using_var"] = True
                            self.updated_data.update({"finalMatches": get_data_for_website(6)})
                            return
                        else:
                            return

                    elif self.there_is_an_ko_phase.get() == 1:
                        result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached end of the final matches. Do you want to select the last KO match?")
                        if result:
                            self.active_mode.set(3)
                            self.save_active_mode_in_db()
                            values_list, pairedKoMatches = self.get_values_list_mode3()
                            self.on_match_select(values_list[-1], pairedKoMatches)
                            self.save_teams_playing_and_active_match()
                            self.show_frame(self.SPIEL_frame)
                            self.cache_vars["getkomatches_changed_using_var"] = True
                            self.updated_data.update({"KOMatches": get_data_for_website(8)})
                            
                            self.cache_vars["getfinalmatches_changed_using_var"] = True
                            self.updated_data.update({"finalMatches": get_data_for_website(6)})
                            return
                        else:
                            return
            
            # self.reload_spiel_button_command()
              
            values_list, active_match = self.get_values_list_mode2()
            
            self.on_match_select(values_list[active_match])
                
            #logging.debug("self.active_match", self.active_match)
            
            self.save_games_played_in_db(self.active_match)
            
            self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
            
            self.updated_data.update({"Games": get_data_for_website(2)})
        
        elif self.active_mode.get() == 3:
            try:
                # Get the current match index
                current_match_index = int(spiel_select.get().split(":")[0])

                values_list, pairedKoMatches = self.get_values_list_mode3()

                # Calculate the new match index
                new_match_index = current_match_index + 1 if next_match else current_match_index - 1
                
                if new_match_index > len(pairedKoMatches):
                    result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the end of the matches. Do you want activate the pause and the final matches?")
                    if result:
                        self.pause_mode.set(1)
                        self.on_pause_switch_change()
                        self.active_mode.set(2)
                        self.save_active_mode_in_db()
                        values_list, _ = self.get_values_list_mode2()
                        self.on_match_select(values_list[0])
                        self.update_idletasks()
                        self.update()
                        self.cache_vars["getkomatches_changed_using_var"] = True
                        self.updated_data.update({"KOMatches": get_data_for_website(8)})
                        
                        self.cache_vars["getfinalmatches_changed_using_var"] = True
                        self.updated_data.update({"finalMatches": get_data_for_website(6)})
                        return
                    else:
                        return
                    
                if new_match_index == 0 and next_match == False and self.active_mode.get() == 3:
                    result = tkinter.messagebox.askyesno("Selecting Helper", "You have reached the beginning of the KO matches. Do you want to select the last match of the group phase?")
                    if result:
                        self.active_mode.set(1)
                        self.save_active_mode_in_db()
                        values_list = self.get_values_list_mode1(matches)
                        self.on_match_select(values_list[-1], matches)
                        self.save_teams_playing_and_active_match()
                        self.show_frame(self.SPIEL_frame)
                        self.cache_vars["getkomatches_changed_using_var"] = True
                        self.updated_data.update({"KOMatches": get_data_for_website(8)})
                        return
                    else:
                        return
                # Ensure the new index is within bounds
                new_match_index = max(1, min(new_match_index, len(matches)))

                self.save_games_played_in_db(new_match_index - 1)

                # Get the teams playing in the selected match
                team_names = self.read_teamNames()
                teams_playing = [team_names.index(pairedKoMatches[new_match_index - 1][0][1]), team_names.index(pairedKoMatches[new_match_index - 1][1][1])] if new_match_index > 0 else [None, None]
                
                self.active_match = new_match_index - 1

                # Update the buttons
                self.teams_playing = teams_playing
                self.reload_spiel_button_command()
                self.show_frame(self.SPIEL_frame)
                
                self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
                self.updated_data.update({"Games": get_data_for_website(2)})
                

                # logging.debug statements
                logging.debug(f"current_match_index: {current_match_index}")
                logging.debug(f"new_match_index: {new_match_index}")
                logging.debug(f"teams_playing: {teams_playing}")
                
            except ValueError:
                # Handle the case where the selected match is not found in the list
                logging.debug("Selected match not found in the list.")
                
                values_list, pairedKoMatches = self.get_values_list_mode3()

                self.on_match_select(values_list[0], pairedKoMatches)


    def global_scored_a_point(self, teamID, team2ID, direction="UP"):
        # Get the current score
        self.cache_vars["getgoals_changed_using_var"] = True
        self.cache_vars["getmatches_changed_using_var"] = True
        self.cache_vars["getfinalmatches_changed_using_var"] = True
        logging.debug(f"global_scored_a_point teamID: {teamID}, team2ID: {team2ID}, direction: {direction}")
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
            if self.active_mode.get() == 2:
                self.updated_data.update({"finalMatches": get_data_for_website(6)})
    
    
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
       
        
    def save_goals_for_match_in_db(self, teamID, team2ID, goals, fromWhichMode=-1):
        if fromWhichMode == -1:
            table_name = 'matchData' if self.active_mode.get() == 1 else 'finalMatchesData' if self.active_mode.get() == 2 else 'KOMatchesData'
        else:
            table_name = 'matchData' if fromWhichMode == 1 else 'finalMatchesData' if fromWhichMode == 2 else 'KOMatchesData'

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
        
        
    def read_goals_for_match_from_db(self, teamID, team2ID, fromWhichMode=-1):
        if fromWhichMode == -1:
            table_name = 'matchData' if self.active_mode.get() == 1 else 'finalMatchesData' if self.active_mode.get() == 2 else 'KOMatchesData'
        else:
            table_name = 'matchData' if fromWhichMode == 1 else 'finalMatchesData' if fromWhichMode == 2 else 'KOMatchesData'

        get_goals_for_match = f"""
        SELECT 
            CASE 
                WHEN team1Id = ? THEN team1Goals
                WHEN team2Id = ? THEN team2Goals
                ELSE 'Not Found'
            END AS Goals
        FROM {table_name}
        WHERE (team1Id = ? AND team2Id = ?) OR (team1Id = ? AND team2Id = ?);
        """
        self.cursor.execute(get_goals_for_match, (teamID, teamID, teamID, team2ID, team2ID, teamID))
        
        goals = self.cursor.fetchone()

        return goals[0] if goals else None
        
    
    def read_team_stats(self, team_id, stat):
        #logging.debug("read_team_stats", "teams_playing", self.teams_playing, "team_id", team_id, "stat", stat)
        
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
        
        self.cache_vars["getgames_changed_using_var"] = True

        if self.active_mode.get() == 1:
        
            teams_ids = self.read_teamIds()
            for teamID in teams_ids:
                #logging.debug("accsed matchData in save_games_played_in_db")
                
                getPlayed = """
                SELECT matchId FROM matchData
                WHERE (team1Id = ? OR team2Id = ?) AND matchId < ?
                """
                self.cursor.execute(getPlayed, (teamID, teamID, match_index + 1))
                
                played = self.cursor.fetchall()
                
                #logging.debug("played", played)
                
                played = len(played)
                
                updatePlayed = """
                UPDATE teamData
                SET games = ?
                WHERE id = ?
                """
                
                self.cursor.execute(updatePlayed, (played, teamID))
        elif self.active_mode.get() == 2:
            teams_ids = self.read_teamIds()
            for teamID in teams_ids:
                #logging.debug("accsed finalMatchesData in save_games_played_in_db")
                
                getPlayed = """
                SELECT matchId FROM finalMatchesData
                WHERE (team1Id = ? OR team2Id = ?) AND matchId < ?
                """
                self.cursor.execute(getPlayed, (teamID, teamID, match_index + 1))
                
                played = self.cursor.fetchall()
                
                #get the matches from phase 1 using sql count
                getPlayedPhase1 = """
                SELECT COUNT(matchId) FROM matchData
                WHERE (team1Id = ? OR team2Id = ?)
                """
                self.cursor.execute(getPlayedPhase1, (teamID, teamID))

                playedPhase1 = self.cursor.fetchone()[0]

                played = playedPhase1


                updatePlayed = """
                UPDATE teamData
                SET games = ?
                WHERE id = ?
                """

                self.cursor.execute(updatePlayed, (played, teamID))
        elif self.active_mode.get() == 3:
            teams_ids = self.read_teamIds()
            for teamID in teams_ids:
                #logging.debug("accsed KOMatchesData in save_games_played_in_db")
                
                getPlayed = """
                SELECT matchId FROM KOMatchesData
                WHERE (team1Id = ? OR team2Id = ?) AND matchId < ?
                """
                self.cursor.execute(getPlayed, (teamID, teamID, match_index + 1))
                
                played = self.cursor.fetchall()
                
                #get the matches from phase 1 using sql count
                getPlayedPhase1 = """
                SELECT COUNT(matchId) FROM matchData
                WHERE (team1Id = ? OR team2Id = ?)
                """
                self.cursor.execute(getPlayedPhase1, (teamID, teamID))

                playedPhase1 = self.cursor.fetchone()[0]

                played = playedPhase1

                updatePlayed = """
                UPDATE teamData
                SET games = ?
                WHERE id = ?
                """

                self.cursor.execute(updatePlayed, (played, teamID))

        
        self.connection.commit()
        self.updated_data.update({"Games": get_data_for_website(2)})
        
        
    def save_teams_playing_and_active_match(self):
        if self.teams_playing[0] != None and self.teams_playing[1] != None or self.active_match == -1:
            updateTeamsPlaying = """
            UPDATE settingsData
            SET teams_playing = ?, activeMatch = ?
            WHERE id = 1
            """
            self.settingscursor.execute(updateTeamsPlaying, (str(self.teams_playing), self.active_match))
            self.settingsconnection.commit()


    def save_active_mode_in_db(self):
        updateActiveMode = """
        UPDATE settingsData
        SET activeMode = ?
        WHERE id = 1
        """
        self.settingscursor.execute(updateActiveMode, (self.active_mode.get(),))
        self.settingsconnection.commit()
    

    ###########################################################################################################
    ###########################################################################################################
    ###########################################################################################################
    ###########################################################################################################  
    
    def create_tipping_elements(self):
        # Create elements for the Contact frame
        self.delete_tipping_frame = ctk.CTkFrame(self.tipping_frame, bg_color='#0e1718', fg_color='#0e1718')
        self.delete_tipping_frame.pack(pady=7, anchor=tk.NW, side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)

        self.tipping_tab_view = ctk.CTkTabview(self.delete_tipping_frame, bg_color='#0e1718', fg_color='#0e1718', command=self.on_tipping_tab_change)
        self.tipping_tab_view.pack(pady=0, anchor=tk.NW, side=tk.TOP, padx=0, fill=tk.BOTH, expand=True)

        self.tipping_tab_list = self.tipping_tab_view.add("Tippers List")
        self.tipping_tab_view.set("Tippers List")
        #self.tipping_tab_winners = self.tipping_tab_view.add("Winners")

        self.create_tippers_list_elements()


    def create_tippers_list_elements(self):
        self.calculate_points_for_tippers_using_db()

        getTippers = """
        SELECT t.googleId, u.userName, MAX(t.points) as total_points FROM tippingData t, userData u
        WHERE t.googleId = u.googleId
        GROUP BY t.googleId, u.userName
        ORDER BY total_points DESC, u.userName ASC
        """
        self.cursor.execute(getTippers)
        tippers = self.cursor.fetchall()

        self.tippers_list_frame = ttk.Frame(self.tipping_tab_list)
        self.tippers_list_frame.pack(fill=tk.BOTH, expand=True)  # Change grid to pack


        # Create a style
        style = ttk.Style()
        
        style.theme_use("clam")

        
        # Configure the Treeview heading
        style.configure("Treeview.Heading",
                        foreground='white',  # Set font color
                        font=('Helvetica', int(self.team_button_font_size*1.4), 'bold'),  # Set font size and style
                        background='#0e1718',
                        fieldbackground='#0e1718')

        # Configure the Treeview content
        style.configure("Treeview",
                        rowheight=30,  # Increase row height
                        foreground='white',  # Set font color
                        font=('Helvetica', int(self.team_button_font_size*1.4)),
                        background='#0e1718',
                        fieldbackground='#0e1718')

        # Create the treeview widget
        tree = ttk.Treeview(self.tippers_list_frame, columns=('Tipper', 'Points'), show='headings')

        # Configure column widths (optional)
        tree.column('Tipper', width=100)
        tree.column('Points', width=100)

        # Create column headings
        tree.heading('Tipper', text='Tipper')
        tree.heading('Points', text='Points')

        # Insert data into the treeview
        for tipper in tippers:
            tree.insert('', 'end', values=(tipper[1], tipper[2]))

        tree.pack(fill=tk.BOTH, expand=True)  # Change grid to pack
            
            
    def on_tipping_tab_change(self):
        current_tab = self.tipping_tab_view.get()
        print("current_tab", current_tab)
        
        if current_tab == "Tippers List":
            if self.tippers_list_frame:
                self.tippers_list_frame.grid_forget()
                self.tippers_list_frame.destroy()
            self.create_tippers_list_elements()
            
        
    def calculate_points_for_tippers_using_db(self):
        getTippersAndMatches = """
        SELECT t.googleId, t.team1Goals, t.team2Goals, m.matchId, m.team1Id, m.team2Id, m.team1Goals, m.team2Goals 
        FROM tippingData t
        INNER JOIN matchData m ON t.matchId = m.matchId
        ORDER BY m.matchId ASC
        """
        self.cursor.execute(getTippersAndMatches)
        tippers_and_matches = self.cursor.fetchall()

        #print("tippers_and_matches", tippers_and_matches)
        
        update_points = {}

        for row in tippers_and_matches:
            googleId, tipper_team1Goals, tipper_team2Goals, matchId, team1Id, team2Id, team1Goals, team2Goals = row

            goal_difference = team1Goals - team2Goals
            team1won = team1Goals > team2Goals
            team2won = team1Goals < team2Goals
            
            if tipper_team1Goals == team1Goals and tipper_team2Goals == team2Goals:
                points = 4
            elif (tipper_team1Goals - tipper_team2Goals) == goal_difference:
                points = 3
            elif (tipper_team1Goals > tipper_team2Goals and team1won) or (tipper_team1Goals < tipper_team2Goals and team2won):
                points = 2    
            else:
                points = 0
            
            #print("googleId", googleId, "points", points)

            update_points[googleId] = update_points.get(googleId, 0) + points
            
            
        for googleId, points in update_points.items():
            updatePoints = """
            UPDATE tippingData
            SET points = ?
            WHERE googleId = ?
            """
            self.cursor.execute(updatePoints, (points, googleId))
        
        self.connection.commit()


    def reload_tipping_page(self):
        #if there is an self.delete_tipping_frame  frame created, delete it
        if self.delete_tipping_frame:
            self.delete_tipping_frame.forget()
            self.delete_tipping_frame.destroy()
        self.tipping_tab_view.forget()
        self.tipping_tab_view.forget()
        self.create_tipping_elements()
        self.show_frame(self.tipping_frame)

    
    ###########################################################################################################
    ###########################################################################################################
    ###########################################################################################################
    ########################################################################################################### 

    def create_settings_elements(self):
        
        # Create elements for the Contact frame
        option_frame = ctk.CTkFrame(self.settings_frame, bg_color='#0e1718', fg_color='#0e1718')
        option_frame.pack(pady=7, anchor=tk.NW, side=tk.LEFT, padx=15)
        
        all_option_frame = ctk.CTkFrame(option_frame, bg_color='#0e1718', fg_color='#0e1718', width=self.screenwidth/3)
        all_option_frame.pack(pady=0, anchor=tk.NW, side=tk.TOP, padx=0)
        
        utility_frame = ctk.CTkFrame(all_option_frame, bg_color='#0e1718', fg_color='#0e1718')
        utility_frame.pack(pady=0, anchor=tk.N, side=tk.TOP, padx=5, expand=True, fill=tk.X)
        
        # phase switcher
        all_switcher_frame = ctk.CTkFrame(utility_frame, bg_color='#0e1718', fg_color='#0e1718')
        all_switcher_frame.pack(pady=0, side=tk.LEFT, padx=10, anchor=tk.NW, expand=False)
        
        # volume slider
        volume_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        volume_frame.pack(pady=10, anchor=tk.N, side=tk.TOP, padx=0)
        
        volume_label = ctk.CTkLabel(volume_frame, text="Volume", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        volume_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        volume_value_label = ctk.CTkLabel(volume_frame, textvariable=self.volume, font=("Helvetica", self.team_button_font_size*1.3))
        volume_value_label.pack(side=tk.RIGHT, pady=0, padx=0, anchor=tk.NE, expand=True)
        
        volume_slider = ctk.CTkSlider(
            volume_frame, 
            orientation=tk.HORIZONTAL, 
            from_=0, 
            to=100, 
            variable=self.volume, 
            command=lambda event: self.on_volume_change(event), 
            height=30)
        volume_slider.pack(pady=0, padx=5, side=tk.LEFT, anchor=tk.NW, expand=True, fill=tk.X)
        
        phase_switcher_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        phase_switcher_frame.pack(pady=7, anchor=tk.NW, side=tk.TOP, padx=5)
        
        option_label = ctk.CTkLabel(phase_switcher_frame, text="Phase Switcher", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        option_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)
        radio_button_1 = ctk.CTkRadioButton(phase_switcher_frame, text="Group Phase", variable=self.active_mode, value=1, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_radio_button_change)
        radio_button_1.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)
        radio_buttone_3 = ctk.CTkRadioButton(phase_switcher_frame, text="KO Phase", variable=self.active_mode, value=3, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_radio_button_change)
        radio_buttone_3.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)
        radio_button_2 = ctk.CTkRadioButton(phase_switcher_frame, text="Final Phase", variable=self.active_mode, value=2, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_radio_button_change)
        radio_button_2.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)
        
        ############################################################################################################

        #self.pause_switcher_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        #self.pause_switcher_frame.pack(pady=7, anchor=tk.NW, side=tk.TOP, padx=5)
        
        #self.pause_switch = ctk.CTkSwitch(self.pause_switcher_frame, text="Pause", variable=self.pause_mode, command=self.on_pause_switch_change, font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        #self.pause_switch.pack(side=tk.TOP, pady=2, padx=0, anchor=tk.N)

        pause_radio_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        pause_radio_frame.pack(pady=7, anchor=tk.NW, side=tk.TOP, padx=5)

        pause_label = ctk.CTkLabel(pause_radio_frame, text="Pause Modes Switcher", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        pause_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)

        pause_radio_button_1 = ctk.CTkRadioButton(pause_radio_frame, text="Off", variable=self.pause_mode, value=0, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_pause_switch_change)
        pause_radio_button_1.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)

        pause_radio_button_4 = ctk.CTkRadioButton(pause_radio_frame, text="Before KO Matches", variable=self.pause_mode, value=1, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_pause_switch_change)
        pause_radio_button_4.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)

        pause_radio_button_3 = ctk.CTkRadioButton(pause_radio_frame, text="Before Final Matches", variable=self.pause_mode, value=2, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_pause_switch_change)
        pause_radio_button_3.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)

        pause_radio_button_2 = ctk.CTkRadioButton(pause_radio_frame, text="Before The Final Match", variable=self.pause_mode, value=3, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_pause_switch_change)
        pause_radio_button_2.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)

        ############################################################################################################
        
        self.there_is_an_ko_phase_switcher_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        self.there_is_an_ko_phase_switcher_frame.pack(pady=7, anchor=tk.NW, side=tk.TOP, padx=5)

        self.there_is_an_ko_phase_switch = ctk.CTkSwitch(self.there_is_an_ko_phase_switcher_frame, text="There is an KO Phase", variable=self.there_is_an_ko_phase, command=self.on_there_is_an_ko_phase_switch_change, font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        self.there_is_an_ko_phase_switch.pack(side=tk.TOP, pady=2, padx=0, anchor=tk.N)

        best_scorer_active_switch_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        best_scorer_active_switch_frame.pack(pady=5, anchor=tk.NW, side=tk.TOP, padx=5)
        
        best_scorer_active_switch = ctk.CTkSwitch(best_scorer_active_switch_frame, text="Best Scorer Active", variable=self.best_scorer_active, command=self.on_best_scorer_active_switch_change, font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        best_scorer_active_switch.pack(side=tk.TOP, pady=2, padx=0, anchor=tk.N)

        # debug mode switcher
        debug_frame = ctk.CTkFrame(all_switcher_frame, bg_color='#0e1718', fg_color='#0e1718')
        debug_frame.pack(pady=5, anchor=tk.NW, side=tk.TOP, padx=5)
        
        debug_label = ctk.CTkLabel(debug_frame, text="Debug Mode", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        debug_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)
        
        radio_button_3 = ctk.CTkRadioButton(debug_frame, text="Debug", variable=self.debug_mode, value=1, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_radio_debug_button_change)
        radio_button_3.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)
        radio_button_4 = ctk.CTkRadioButton(debug_frame, text="Debug Off", variable=self.debug_mode, value=0, font=("Helvetica", self.team_button_font_size*1.3), command=self.on_radio_debug_button_change)
        radio_button_4.pack(side=tk.TOP, pady=2, padx = 0, anchor=tk.NW)
        
        ############################################################################################################

        entry_frame1 = ctk.CTkFrame(utility_frame, bg_color='#0e1718', fg_color='#0e1718')
        entry_frame1.pack(pady=7, anchor=tk.NW, side=tk.LEFT, padx=10)

        entry_frame1_label = ctk.CTkLabel(entry_frame1, text="General Settings", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        entry_frame1_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)
        
        # start time for matches
        start_time_frame = ctk.CTkFrame(entry_frame1, bg_color='#0e1718', fg_color='#0e1718')
        start_time_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        start_time_label = ctk.CTkLabel(start_time_frame, text="Start Time", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        start_time_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        start_time_entry = ctk.CTkEntry(start_time_frame, textvariable=self.start_time, font=("Helvetica", self.team_button_font_size*1.3))
        start_time_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        start_time_entry.bind("<KeyRelease>", lambda event: self.on_start_time_change(event))

        # website title
        website_title_frame = ctk.CTkFrame(entry_frame1, bg_color='#0e1718', fg_color='#0e1718')
        website_title_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        website_title_label = ctk.CTkLabel(website_title_frame, text="Website Title", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        website_title_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        website_title_entry = ctk.CTkEntry(website_title_frame, textvariable=self.website_title, font=("Helvetica", self.team_button_font_size*1.3), width=self.team_button_width*2)
        website_title_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        website_title_entry.bind("<KeyRelease>", lambda event: self.on_website_title_change(event))

        entry_frame2 = ctk.CTkFrame(utility_frame, bg_color='#0e1718', fg_color='#0e1718')
        entry_frame2.pack(pady=7, anchor=tk.NW, side=tk.LEFT, padx=10)

        entry_frame2_label = ctk.CTkLabel(entry_frame2, text="Time Interval Settings", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        entry_frame2_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)

        # time interval for matches
        time_interval_frame = ctk.CTkFrame(entry_frame2, bg_color='#0e1718', fg_color='#0e1718')
        time_interval_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        time_interval_label = ctk.CTkLabel(time_interval_frame, text="Time Interval for Group Phase", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_interval_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        time_interval_entry = ctk.CTkEntry(time_interval_frame, textvariable=self.time_interval, font=("Helvetica", self.team_button_font_size*1.3))
        time_interval_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_interval_entry.bind("<KeyRelease>", lambda event: self.on_time_interval_change(event))
        
        #time interval for ko phase
        time_intervalKO_frame = ctk.CTkFrame(entry_frame2, bg_color='#0e1718', fg_color='#0e1718')
        time_intervalKO_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        time_intervalKO_label = ctk.CTkLabel(time_intervalKO_frame, text="Time Interval for KO Phase", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_intervalKO_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        time_intervalKO_entry = ctk.CTkEntry(time_intervalKO_frame, textvariable=self.time_intervalKO, font=("Helvetica", self.team_button_font_size*1.3))
        time_intervalKO_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_intervalKO_entry.bind("<KeyRelease>", lambda event: self.on_time_intervalKO_change(event))

        # time interval for final matches
        time_intervalFM_frame = ctk.CTkFrame(entry_frame2, bg_color='#0e1718', fg_color='#0e1718')
        time_intervalFM_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        time_intervalFM_label = ctk.CTkLabel(time_intervalFM_frame, text="Time Interval for Final Matches", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_intervalFM_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        time_intervalFM_entry = ctk.CTkEntry(time_intervalFM_frame, textvariable=self.time_intervalFM, font=("Helvetica", self.team_button_font_size*1.3))
        time_intervalFM_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_intervalFM_entry.bind("<KeyRelease>", lambda event: self.on_time_intervalFM_change(event))

        #time interval for final match
        time_intervalFinalMatch_frame = ctk.CTkFrame(entry_frame2, bg_color='#0e1718', fg_color='#0e1718')
        time_intervalFinalMatch_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        time_intervalFinalMatch_label = ctk.CTkLabel(time_intervalFinalMatch_frame, text="Time Interval for THE Final Match", font=("Helvetica", self.team_button_font_size*1.35, "bold"))
        time_intervalFinalMatch_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        time_intervalFinalMatch_entry = ctk.CTkEntry(time_intervalFinalMatch_frame, textvariable=self.time_interval_for_only_the_final_match, font=("Helvetica", self.team_button_font_size*1.3))
        time_intervalFinalMatch_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_intervalFinalMatch_entry.bind("<KeyRelease>", lambda event: self.on_time_intervalFinalMatch_change(event))
        
        ############################################################################################################

        entry_frame3 = ctk.CTkFrame(utility_frame, bg_color='#0e1718', fg_color='#0e1718')
        entry_frame3.pack(pady=7, anchor=tk.NW, side=tk.LEFT, padx=10)

        entry_frame3_label = ctk.CTkLabel(entry_frame3, text="Pause Settings", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        entry_frame3_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW)

        # pause time before ko matches
        time_pause_before_KO_frame = ctk.CTkFrame(entry_frame3, bg_color='#0e1718', fg_color='#0e1718')
        time_pause_before_KO_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)

        time_pause_before_KO_label = ctk.CTkLabel(time_pause_before_KO_frame, text="Pause Group Phase > KO", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_pause_before_KO_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)

        time_pause_before_KO_entry = ctk.CTkEntry(time_pause_before_KO_frame, textvariable=self.time_pause_before_KO, font=("Helvetica", self.team_button_font_size*1.3))
        time_pause_before_KO_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_pause_before_KO_entry.bind("<KeyRelease>", lambda event: self.on_time_pause_before_KO_change(event))

        
        # pause time before final matches
        time_pause_before_FM_frame = ctk.CTkFrame(entry_frame3, bg_color='#0e1718', fg_color='#0e1718')
        time_pause_before_FM_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)
        
        time_pause_before_FM_label = ctk.CTkLabel(time_pause_before_FM_frame, text="Pause KO/GP > Final Matches", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_pause_before_FM_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)
        
        time_pause_before_FM_entry = ctk.CTkEntry(time_pause_before_FM_frame, textvariable=self.time_pause_before_FM, font=("Helvetica", self.team_button_font_size*1.3), width=self.team_button_width*2)
        time_pause_before_FM_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_pause_before_FM_entry.bind("<KeyRelease>", lambda event: self.on_time_pause_before_FM_change(event))

        # pause time before the final match
        time_before_the_final_match_frame = ctk.CTkFrame(entry_frame3, bg_color='#0e1718', fg_color='#0e1718')
        time_before_the_final_match_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)

        time_before_the_final_match_label = ctk.CTkLabel(time_before_the_final_match_frame, text="Pause FMs > THE Final Match", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        time_before_the_final_match_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)

        time_before_the_final_match_entry = ctk.CTkEntry(time_before_the_final_match_frame, textvariable=self.time_before_the_final_match, font=("Helvetica", self.team_button_font_size*1.3))
        time_before_the_final_match_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        time_before_the_final_match_entry.bind("<KeyRelease>", lambda event: self.on_time_before_the_final_match_change(event))

        # Half time pause
        half_time_pause_frame = ctk.CTkFrame(entry_frame3, bg_color='#0e1718', fg_color='#0e1718')
        half_time_pause_frame.pack(pady=7, anchor=tk.N, side=tk.TOP, padx=0, expand=True, fill=tk.X)

        half_time_pause_label = ctk.CTkLabel(half_time_pause_frame, text="Half Time Pause", font=("Helvetica", self.team_button_font_size*1.4, "bold"))
        half_time_pause_label.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.N)

        half_time_pause_entry = ctk.CTkEntry(half_time_pause_frame, textvariable=self.half_time_pause, font=("Helvetica", self.team_button_font_size*1.3))
        half_time_pause_entry.pack(side=tk.TOP, pady=5, padx=0, anchor=tk.NW, expand=True, fill=tk.X)
        half_time_pause_entry.bind("<KeyRelease>", lambda event: self.on_half_time_pause_change(event))

        ############################################################################################################
        
        
    def on_volume_change(self, event):
        saveVolumeInDB = """
        UPDATE settingsData
        SET volume = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveVolumeInDB, (int(event),))
        self.settingsconnection.commit()
        
        
    def on_radio_button_change(self):
        self.cache_vars["getfinalmatches_changed_using_var"] = True
        selected_value = self.active_mode.get()

        print("selected_value", selected_value, "self.read_teamNames()", self.read_teamNames())
        if self.read_teamNames() == [''] and selected_value != 1:
            self.active_mode.set(1)
            self.on_radio_button_change()
            return
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
            
        if selected_value == 1:
            self.active_match = -1
            self.teams_playing = [None, None]

        elif selected_value == 2:
            self.cursor.execute("SELECT COUNT(*) FROM matchData")
            match_count = self.cursor.fetchone()[0]
            self.save_games_played_in_db(match_count)
            
        self.reload_spiel_button_command(True)
        self.updated_data.update({"activeMatchNumber": get_data_for_website(5)})
        self.updated_data.update({"finalMatches": get_data_for_website(6)})
        self.cache_vars["getkomatches_changed_using_var"] = True
        self.updated_data.update({"KOMatches": get_data_for_website(8)})

        
    def on_radio_debug_button_change(self):
        selected_value = self.debug_mode.get()
        saveModeInDB = """
        UPDATE settingsData
        SET debugMode = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()
        
        if self.debug_mode.get() == 1:
            self.console_handler.setLevel(logging.DEBUG)
        elif self.debug_mode.get() == 0:
            self.console_handler.setLevel(logging.ERROR)
            
        # self.reload_spiel_button_command()
        
        
    def is_valid_time(self, time_str):
        if ":" in time_str:
            time_parts = time_str.split(":")
            if len(time_parts) != 2:
                return False
            hour, minute = time_parts
            if not (hour.isdigit() and minute.isdigit() and len(hour) == 2 and len(minute) == 2):
                return False
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                return False
            return True
        else:
            return False


    def on_start_time_change(self, event):
        if self.start_time.get() == "":
            return
        time_str = str(self.start_time.get())
        if not self.is_valid_time(time_str):
            logging.warning(f"Invalid time format. Please enter time in HH:MM format.")
            return

        # Format time correctly
        hour, minute = time_str.split(":")
        formatted_time = f"{int(hour):02d}:{int(minute):02d}"

        saveStartTimeInDB = """
        UPDATE settingsData
        SET startTime = ?
        WHERE id = 1
        """
        logging.debug(f"on_start_time_change {formatted_time}")
        self.settingscursor.execute(saveStartTimeInDB, (formatted_time,))
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
        logging.debug(f"on_time_interval_change {self.time_interval.get()}")
        self.settingscursor.execute(saveTimeIntervalInDB, (self.time_interval.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"timeInterval": self.time_interval.get().replace("m", "")})


    def on_time_intervalKO_change(self, event):
        if self.time_intervalKO.get() == "":
            return
        if self.time_intervalKO.get()[-1] not in "0123456789m" or not "m" in self.time_intervalKO.get() or len(self.time_intervalKO.get()) < 1:
            return
        saveTimeIntervalKOInDB = """
        UPDATE settingsData
        SET timeIntervalKO = ?
        WHERE id = 1
        """
        logging.debug(f"on_time_intervalKO_change {self.time_intervalKO.get()}")
        self.settingscursor.execute(saveTimeIntervalKOInDB, (self.time_intervalKO.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"timeIntervalKOMatches": self.time_intervalKO.get().replace("m", "")})
        

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
        logging.debug(f"on_time_intervalFM_change {self.time_intervalFM.get()}")
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
        logging.debug(f"on_time_pause_before_FM_change {self.time_pause_before_FM.get()}")
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
        logging.debug(f"on_website_title_change {self.website_title.get()}")
        self.settingscursor.execute(saveWebsiteTitleInDB, (self.website_title.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"websiteTitle": self.website_title.get()})


    def on_pause_switch_change(self):
        selected_value = self.pause_mode.get()
        saveModeInDB = """
        UPDATE settingsData
        SET pauseMode = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()
        
        self.updated_data.update({"pauseMode": get_data_for_website(9)})
        
        
    def on_time_intervalFinalMatch_change(self, event):
        if self.time_interval_for_only_the_final_match.get() == "":
            return
        if self.time_interval_for_only_the_final_match.get()[-1] not in "0123456789m" or not "m" in self.time_interval_for_only_the_final_match.get() or len(self.time_interval_for_only_the_final_match.get()) < 1:
            return
        saveTimeIntervalFinalMatchInDB = """
        UPDATE settingsData
        SET timeIntervalForOnlyTheFinalMatch = ?
        WHERE id = 1
        """
        logging.debug(f"on_time_intervalFinalMatch_change {self.time_interval_for_only_the_final_match.get()}")
        self.settingscursor.execute(saveTimeIntervalFinalMatchInDB, (self.time_interval_for_only_the_final_match.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"timeIntervalFinalMatch": self.time_interval_for_only_the_final_match.get().replace("m", "")})
   
        
    def on_best_scorer_active_switch_change(self):
        selected_value = self.best_scorer_active.get()
        saveModeInDB = """
        UPDATE settingsData
        SET bestScorerActive = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()
        
        self.updated_data.update({"bestScorerActive": selected_value})


    def on_there_is_an_ko_phase_switch_change(self):
        selected_value = self.there_is_an_ko_phase.get()
        saveModeInDB = """
        UPDATE settingsData
        SET thereAreKOMatches = ?
        WHERE id = 1
        """
        self.settingscursor.execute(saveModeInDB, (selected_value,))
        self.settingsconnection.commit()
        
        self.updated_data.update({"thereIsAnKoPhase": selected_value})


    def on_pause_button_change(self):
        #######################################
        #This is not the Pause Switch Function!
        #######################################
        result = tkinter.messagebox.askyesno("Pause Manager", "Do you want to disable the pause mode?")
        if result:
            self.pause_mode.set(0)
            self.on_pause_switch_change()
            button = self.pause_mode_active_button
            button.pack_forget()
            button.destroy()
            return
        else:
            return
        
    
    def on_best_scorer_button_change(self):
        result = tkinter.messagebox.askyesno("Best Scorer Manager", "Do you want to disable the best scorer mode?")
        if result:
            self.best_scorer_active.set(0)
            self.on_best_scorer_active_switch_change()
            button = self.best_scorer_active_button
            button.pack_forget()
            button.destroy()
            return
        else:
            return
        

    def on_time_pause_before_KO_change(self, event):
        if self.time_pause_before_KO.get() == "":
            return
        if self.time_pause_before_KO.get()[-1] not in "0123456789m" or not "m" in self.time_pause_before_KO.get() or len(self.time_pause_before_KO.get()) < 1:
            return
        saveTimePauseBeforeKOInDB = """
        UPDATE settingsData
        SET pauseBeforeKO = ?
        WHERE id = 1
        """
        logging.debug(f"on_time_pause_before_KO_change {self.time_pause_before_KO.get()}")
        self.settingscursor.execute(saveTimePauseBeforeKOInDB, (self.time_pause_before_KO.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"pauseBeforeKOMatches": self.time_pause_before_KO.get().replace("m", "")})


    def on_time_before_the_final_match_change(self, event):
        if self.time_before_the_final_match.get() == "":
            return
        if self.time_before_the_final_match.get()[-1] not in "0123456789m" or not "m" in self.time_before_the_final_match.get() or len(self.time_before_the_final_match.get()) < 1:
            return
        saveTimeBeforeTheFinalMatchInDB = """
        UPDATE settingsData
        SET timeBeforeTheFinalMatch = ?
        WHERE id = 1
        """
        logging.debug(f"on_time_before_the_final_match_change {self.time_before_the_final_match.get()}")
        self.settingscursor.execute(saveTimeBeforeTheFinalMatchInDB, (self.time_before_the_final_match.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"pauseBeforeTheFinalMatch": self.time_before_the_final_match.get().replace("m", "")})


    def on_half_time_pause_change(self, event):
        if self.half_time_pause.get() == "":
            return
        if self.half_time_pause.get()[-1] not in "0123456789m" or not "m" in self.half_time_pause.get() or len(self.half_time_pause.get()) < 1:
            return
        saveHalfTimePauseInDB = """
        UPDATE settingsData
        SET halfTimePause = ?
        WHERE id = 1
        """
        logging.debug(f"on_half_time_pause_change {self.half_time_pause.get()}")
        self.settingscursor.execute(saveHalfTimePauseInDB, (self.half_time_pause.get(),))
        self.settingsconnection.commit()
        
        self.updated_data.update({"halfTimePause": self.half_time_pause.get().replace("m", "")})


    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    def show_frame(self, frame):
        # Hide all frames and pack the selected frame
        for frm in [self.Team_frame, self.player_frame, self.SPIEL_frame, self.tipping_frame, self.settings_frame]:
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)


    def show_Team_frame(self):
        self.reload_button_command()
        self.show_frame(self.Team_frame)
        self.watch_dog_process_can_be_active = False


    def show_player_frame(self):
        self.reload_button_player_command()
        self.show_frame(self.player_frame)
        self.watch_dog_process_can_be_active = False


    def show_SPIEL_frame(self):
        self.watch_dog_process_can_be_active = True
        if self.teams_playing.count(None) == 0 or self.reload_requried_on_click_SPIEL:
            self.reload_spiel_button_command()
            self.reload_requried_on_click_SPIEL = False
            
        #logging.debug(stored_data)
        self.calculate_matches()
        self.show_frame(self.SPIEL_frame)
    
    
    def show_tipping_frame(self):
        self.reload_tipping_page()
        self.show_frame(self.tipping_frame)
        self.watch_dog_process_can_be_active = False 
       
        
    def show_settings_frame(self):
        self.show_frame(self.settings_frame)
        self.watch_dog_process_can_be_active = False


    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    def delete_updated_data(self):
        #logging.debug("delete")
        #logging.debug(self.updated_data)
        self.updated_data = {}
        
        
    def play_mp3(self, file_path, volume=""):
        if file_path == "":
            return
        if volume == "":
            volume = self.volume

        if self.media_player_instance_save != None:
            self.media_player_instance_save.release()
        
        player = self.media_player_instance.media_player_new()
        media = self.media_player_instance.media_new(file_path)
        player.set_media(media)
        player.audio_set_volume(int(volume.get()))
        player.play()
        self.media_player_instance_save = player
        #logging.debug("play_mp3", file_path, "volume", volume.get(), "self.volume", self.volume.get(), "player", player,"media", media)
   
        
    ##############################################################################################
    #############################Calculate########################################################
    ##############################################################################################
    ##############################################################################################

    def calculate_matches(self):
        self.match_count = 0  # Reset matchCount to 0
        
        self.cache_vars["getmatches_changed_using_var"] = True

        #if self.active_mode.get() == 1 or True:
        initial_data = {
            "Teams": self.read_teamNames()
        }

        initial_data["Teams"].pop(0)

        teams = initial_data["Teams"][:]  # Create a copy of the teams array
        
        #teams.sort()
        
        logging.debug(f"calculate_matches: teams {teams}")

        # If the number of teams is odd, add a "dummy" team
        #if len(teams) % 2 != 0:
        #    logging.debug("calculate_matches: uneven number of teams, appending dummy team")
        #    teams.append("dummy")

        midpoint = (len(teams) + 1) // 2
        group1 = teams[:midpoint]
        group2 = teams[midpoint:]

        matches1 = self.calculate_matches_for_group(group1, "Gruppe 1")
        matches2 = self.calculate_matches_for_group(group2, "Gruppe 2")
        
        matches = self.interleave_matches(matches1, matches2)

        self.match_count = 0  # Reset matchCount to 0

        self.matches = list(map(lambda match: self.add_match_number(match), matches))
        
        #logging.debug("self.matches", self.matches)
        
        self.save_matches_to_db()
        
        return self.matches


    def calculate_matches_for_group(self, teams, group_name):
        n = len(teams)
        matches = []

        # If the number of teams is odd, add a "dummy" team
        dummy = False
        if n % 2 != 0:
            #logging.debug("calculate_matches_for_group: uneven number of teams, appending dummy team", "teams", teams)
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

        #logging.debug("calculate_matches_for_group: matches", matches)
        
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
                
                
        #logging.debug("teams_to_delete", teams_to_delete)
        
        #logging.debug("accsed matchData in save_matches_to_db")
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
        
        self.cache_vars["getpoints_changed_using_active_match"] = -1
                
        self.updated_data.update({"Points": get_data_for_website(3)})    
       

##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
 
def get_data_for_website(which_data=-1):
    
    if which_data == 0:
        
        if tkapp.cache_vars.get("getteams_changed_using_var") == True:
        
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            get_teams_query = """
            SELECT teamName FROM teamData
            ORDER BY id ASC
            """
            cursor.execute(get_teams_query)

            team_names = [team[0] for team in cursor.fetchall()]

            cursor.close()
            connection.close()
            
            tkapp.cache_vars["getteams_changed_using_var"] = False
            
            tkapp.cache["Teams"] = team_names

            return team_names

        else:
            return tkapp.cache.get("Teams")
    
    elif which_data == 1:
        
        if tkapp.cache_vars.get("getgoals_changed_using_var") == True:
        
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            Tore = []

            get_teams_data = """
            SELECT goals, goalsReceived FROM teamData
            ORDER BY id ASC
            """
            cursor.execute(get_teams_data)

            for row in cursor.fetchall():
                Tore.append((row[0], row[1]))

            cursor.close()
            connection.close()
            
            tkapp.cache_vars["getgoals_changed_using_var"] = False
            
            tkapp.cache["Goals"] = Tore
                
            return Tore
        
        else:
            return tkapp.cache.get("Goals")
        
    elif which_data == 2:     
        try:
            if tkapp.cache_vars.get("getgames_changed_using_var") == True:
            
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()

                get_games = """
                SELECT games FROM teamData
                ORDER BY id ASC
                """
                cursor.execute(get_games)

                games = [row[0] for row in cursor.fetchall()]

                cursor.close()
                connection.close()
                
                tkapp.cache_vars["getgames_changed_using_var"] = False
                
                tkapp.cache["Games"] = games

                return games
            
            else:
                return tkapp.cache.get("Games")
        except:
            cursor.close()
            connection.close()
            return []
    
    elif which_data == 3:
        
        try:
            if tkapp.cache_vars.get("getpoints_changed_using_active_match") != tkapp.active_match or tkapp.active_match == -1:
                
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                
                team_names = cursor.execute("SELECT id FROM teamData ORDER BY id ASC").fetchall()
                teams_with_points = {str(team[0]): 0 for team in team_names}
                
                if tkapp.active_mode.get() == 1:
                    selectMatches = """
                        SELECT team1Id, team2Id, team1Goals, team2Goals
                        FROM matchData
                        WHERE matchId <= ?
                    """
                    cursor.execute(selectMatches, (tkapp.active_match,))
                    matches = cursor.fetchall()
                else:
                    selectMatches = """
                        SELECT team1Id, team2Id, team1Goals, team2Goals
                        FROM matchData
                    """
                    cursor.execute(selectMatches)
                    matches = cursor.fetchall()
                    

                for match in matches:
                    team1Goals = int(match[2])
                    team2Goals = int(match[3])

                    if team1Goals > team2Goals:
                        teams_with_points[str(match[0])] = teams_with_points.get(str(match[0]), 0) + 3
                                
                    elif team1Goals < team2Goals:
                        teams_with_points[str(match[1])] = teams_with_points.get(str(match[1]), 0) + 3
                                
                    elif team1Goals != 0 and team2Goals != 0:
                        teams_with_points[str(match[0])] = teams_with_points.get(str(match[0]), 0) + 1
                        teams_with_points[str(match[1])] = teams_with_points.get(str(match[1]), 0) + 1
                
                cursor.close()
                connection.close()
                
                points_in_order = [teams_with_points[str(team[0])] for team in team_names]
                
                tkapp.cache_vars["getpoints_changed_using_active_match"] = tkapp.active_match
                
                tkapp.cache["Points"] = points_in_order
                
                return points_in_order
            else:
                return tkapp.cache.get("Points")
        except:
            return []
    
    elif which_data == 4:
        try:
            if tkapp.cache_vars.get("getmatches_changed_using_var") == True:
            
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()

                get_all_matches = """
                SELECT 
                    m.matchId,
                    t1.teamName as team1Name, 
                    t2.teamName as team2Name, 
                    m.team1Goals, 
                    m.team2Goals, 
                    m.groupNumber 
                FROM matchData m
                JOIN teamData t1 ON m.team1Id = t1.id
                JOIN teamData t2 ON m.team2Id = t2.id
                ORDER BY m.matchId ASC
                """

                cursor.execute(get_all_matches)

                all_matches = {row[0]: row[1:] for row in cursor.fetchall()}

                get_tipping_statistics_query = """
                SELECT matchId, team1Goals, team2Goals
                FROM tippingData
                ORDER BY matchId
                """
                cursor.execute(get_tipping_statistics_query)

                tipping_data = cursor.fetchall()

                cursor.close()
                connection.close()

                # Group data by matchId
                grouped_data = {}
                for row in tipping_data:
                    if row[0] not in grouped_data:
                        grouped_data[row[0]] = {'team1Goals': [], 'team2Goals': []}
                    grouped_data[row[0]]['team1Goals'].append(row[1])
                    grouped_data[row[0]]['team2Goals'].append(row[2])

                # Calculate median and percentages
                tipping_statistics = {}
                for matchId, data in grouped_data.items():
                    matchId += 1
                    team1Goals = data['team1Goals']
                    team2Goals = data['team2Goals']
                    average_team1Goals = sum(team1Goals) / len(team1Goals) if team1Goals else 0
                    average_team2Goals = sum(team2Goals) / len(team2Goals) if team2Goals else 0
                    averageRounded_team1Goals = round(average_team1Goals, 2)
                    averageRounded_team2Goals = round(average_team2Goals, 2)
                    percent_team1Wins = sum(1 for goal in team1Goals if goal > average_team2Goals) / len(team1Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    percent_team2Wins = sum(1 for goal in team2Goals if goal > average_team1Goals) / len(team2Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    tipping_statistics[matchId] = (average_team1Goals, average_team2Goals, percent_team1Wins, percent_team2Wins)

                # Combine both datasets
                combined_data = []
                for matchId in all_matches:
                    statistics = tipping_statistics.get(matchId, (None, None, None, None))
                    combined_data.append(list(all_matches[matchId]) + list([statistics]))

                tkapp.cache_vars["getmatches_changed_using_var"] = False

                tkapp.cache["Matches"] = combined_data

                return combined_data
            
            else:
                return tkapp.cache.get("Matches")
        except:
            return []
    
    elif which_data == 5:
        try:
            a_m = tkapp.active_match
            
            if tkapp.active_mode.get() == 2:
                a_m += 2
                a_m *= -1
            elif tkapp.active_mode.get() == 3:
                a_m += 100
                a_m *= -1
            tkapp.updated_data.update({"activeMatchNumber": a_m})
            return a_m
        except:
            logging.error("Error in get_data_for_website(5)")
            return 0
    
    elif which_data == 6:
        if tkapp.active_mode.get() == 2:
            if tkapp.cache_vars.get("getfinalmatches_changed_using_var") == True:
                
                final_goles = []
                
                if tkapp.endteam1 and tkapp.endteam3:
                    if tkapp.endteam1[1] != "No Team" and tkapp.endteam3[1] != "No Team":
                        final_goles.append([ich_kann_nicht_mehr(tkapp.endteam1[0], tkapp.endteam3[0]), ich_kann_nicht_mehr(tkapp.endteam3[0], tkapp.endteam1[0])])
                    else:
                        final_goles.append([0, 0])
                else:
                    final_goles.append([0, 0])
                    
                if tkapp.endteam2 and tkapp.endteam4:
                    if tkapp.endteam2[1] != "No Team" and tkapp.endteam4[1] != "No Team":
                        final_goles.append([ich_kann_nicht_mehr(tkapp.endteam2[0], tkapp.endteam4[0]), ich_kann_nicht_mehr(tkapp.endteam4[0], tkapp.endteam2[0])])
                    else:
                        final_goles.append([0, 0])
                else:
                    final_goles.append([0, 0])
                    
                if tkapp.spiel_um_platz_3:
                    final_goles.append([ich_kann_nicht_mehr(tkapp.spiel_um_platz_3[0][0], tkapp.spiel_um_platz_3[1][0]), ich_kann_nicht_mehr(tkapp.spiel_um_platz_3[1][0], tkapp.spiel_um_platz_3[0][0])])
                else:
                    final_goles.append([0, 0])
                    
                if tkapp.final_match_teams:
                    final_goles.append([ich_kann_nicht_mehr(tkapp.final_match_teams[0][0], tkapp.final_match_teams[1][0]), ich_kann_nicht_mehr(tkapp.final_match_teams[1][0], tkapp.final_match_teams[0][0])])
                else:
                    final_goles.append([0, 0])

                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()

                get_tipping_statistics_query = """
                SELECT matchId, team1Goals, team2Goals
                FROM tippingData
                ORDER BY matchId
                """
                cursor.execute(get_tipping_statistics_query)

                tipping_data = cursor.fetchall()

                cursor.close()
                connection.close()

                # Group data by matchId
                grouped_data = {}
                for row in tipping_data:
                    if row[0] not in grouped_data:
                        grouped_data[row[0]] = {'team1Goals': [], 'team2Goals': []}
                    grouped_data[row[0]]['team1Goals'].append(row[1])
                    grouped_data[row[0]]['team2Goals'].append(row[2])

                # Calculate median and percentages
                tipping_statistics = {}
                for matchId, data in grouped_data.items():
                    matchId *= -1
                    matchId = matchId - 1
                    if matchId < 0:
                        continue
                    team1Goals = data['team1Goals']
                    team2Goals = data['team2Goals']
                    average_team1Goals = sum(team1Goals) / len(team1Goals) if team1Goals else 0
                    average_team2Goals = sum(team2Goals) / len(team2Goals) if team2Goals else 0
                    averageRounded_team1Goals = round(average_team1Goals, 2)
                    averageRounded_team2Goals = round(average_team2Goals, 2)
                    percent_team1Wins = sum(1 for goal in team1Goals if goal > average_team2Goals) / len(team1Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    percent_team2Wins = sum(1 for goal in team2Goals if goal > average_team1Goals) / len(team2Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    tipping_statistics[matchId] = (average_team1Goals, average_team2Goals, percent_team1Wins, percent_team2Wins)

                #
                #    # Combine both datasets
                #    combined_data = []
                #    for matchId in all_matches:
                #        statistics = tipping_statistics.get(matchId, (None, None, None, None))
                #        combined_data.append(list(all_matches[matchId]) + list([statistics]))
                #    return combined_data
                    
                combined_data = []
                for matchId in range(1, 5):
                    statistics = tipping_statistics.get(matchId, (None, None, None, None))
                    combined_data.append(statistics)
                    print(f"matchId {matchId}, statistics {statistics}")

                v = [
                    [tkapp.endteam1[1] if tkapp.endteam1 and tkapp.endteam1[1] != "No Team" else None, tkapp.endteam3[1] if tkapp.endteam3 and tkapp.endteam3[1] != "No Team" else None, final_goles[0][0], final_goles[0][1], combined_data[0]],
                    [tkapp.endteam2[1] if tkapp.endteam2 and tkapp.endteam2[1] != "No Team" else None, tkapp.endteam4[1] if tkapp.endteam4 and tkapp.endteam4[1] != "No Team" else None, final_goles[1][0], final_goles[1][1], combined_data[1]],
                    [tkapp.spiel_um_platz_3[0][1] if tkapp.spiel_um_platz_3 else None, tkapp.spiel_um_platz_3[1][1] if tkapp.spiel_um_platz_3 else None, final_goles[2][0], final_goles[2][1], combined_data[2]],
                    [tkapp.final_match_teams[0][1] if tkapp.final_match_teams else None, tkapp.final_match_teams[1][1] if tkapp.final_match_teams else None, final_goles[3][0], final_goles[3][1], combined_data[3]]
                ]
                logging.debug(f"v {v}")
                
                tkapp.cache_vars["getfinalmatches_changed_using_var"] = False
                
                tkapp.cache["finalMatches"] = v
                
                return v
        
            else:
                return tkapp.cache.get("finalMatches")
        else:
            return None
    
    elif which_data == 7:
        start_time = tkapp.start_time.get()
        a, b = start_time.split(":")
        return [int(a), int(b)]
    
    elif which_data == 8:
        try:

            if tkapp.there_is_an_ko_phase.get() == 0:
                tkapp.cache_vars["getkomatches_changed_using_var"] = True
                return None
            
            if tkapp.active_mode.get() == 1: #and tkapp.pause_time_before_ko.get() == 0:
                tkapp.cache_vars["getkomatches_changed_using_var"] = True
                return None 
            
            if tkapp.cache_vars.get("getkomatches_changed_using_var") == True:
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()

                getAllMatchesFromKOMatchesDB = """
                SELECT 
                    t1.teamName as team1Name, 
                    t2.teamName as team2Name, 
                    m.team1Goals, 
                    m.team2Goals
                FROM KOMatchesData m
                JOIN teamData t1 ON m.team1Id = t1.id
                JOIN teamData t2 ON m.team2Id = t2.id
                ORDER BY m.matchId ASC
                """

                cursor.execute(getAllMatchesFromKOMatchesDB)

                all_matches = cursor.fetchall()

                get_tipping_statistics_query = """
                SELECT matchId, team1Goals, team2Goals
                FROM tippingData
                ORDER BY matchId
                """
                cursor.execute(get_tipping_statistics_query)

                tipping_data = cursor.fetchall()

                cursor.close()
                connection.close()

                # Group data by matchId
                grouped_data = {}
                for row in tipping_data:
                    if row[0] not in grouped_data:
                        grouped_data[row[0]] = {'team1Goals': [], 'team2Goals': []}
                    grouped_data[row[0]]['team1Goals'].append(row[1])
                    grouped_data[row[0]]['team2Goals'].append(row[2])

                # Calculate median and percentages
                    
                tipping_statistics = {}

                for matchId, data in grouped_data.items():
                    matchId *= -1
                    matchId = matchId - 100
                    matchId += 1
                    team1Goals = data['team1Goals']
                    team2Goals = data['team2Goals']
                    average_team1Goals = sum(team1Goals) / len(team1Goals) if team1Goals else 0
                    average_team2Goals = sum(team2Goals) / len(team2Goals) if team2Goals else 0
                    averageRounded_team1Goals = round(average_team1Goals, 2)
                    averageRounded_team2Goals = round(average_team2Goals, 2)
                    percent_team1Wins = sum(1 for goal in team1Goals if goal > average_team2Goals) / len(team1Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    percent_team2Wins = sum(1 for goal in team2Goals if goal > average_team1Goals) / len(team2Goals) * 100 if averageRounded_team1Goals != averageRounded_team2Goals else 50
                    tipping_statistics[matchId] = (average_team1Goals, average_team2Goals, percent_team1Wins, percent_team2Wins)

                combined_data = []
                for foo in all_matches:
                    statistics = tipping_statistics.get(foo[0], (None, None, None, None))
                    combined_data.append(list(foo) + list([statistics]))

                tkapp.cache_vars["getkomatches_changed_using_var"] = False

                tkapp.cache["KOMatches"] = combined_data



                return combined_data
            else:
                return tkapp.cache.get("KOMatches")
        except:
            return []
    
    elif which_data == 9:
        pauseMode = tkapp.pause_mode.get() - 1
        return pauseMode

    else:
        return None    
    

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
    
    logging.debug(f"ich_kann_nicht_mehr: teamID {teamID}, team2ID {team2ID}")
    
    onefetched = cursor.fetchone()
    
    if onefetched is None:
        logging.debug("ich_kann_nicht_mehr: onefetched is None")
        cursor.close()
        connection.close()
        return 0
            
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
        
  
def get_initial_data(template_name, base_url=None):
    global initial_data
    
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
        "LastUpdate": 0,
        "pauseMode": get_data_for_website(9), 
        "timeIntervalFinalMatch": tkapp.time_interval_for_only_the_final_match.get().replace("m", ""),
        "bestScorerActive": tkapp.best_scorer_active.get(),
        "KOMatches": get_data_for_website(8),
        "timeIntervalKOMatches": tkapp.time_intervalKO.get().replace("m", ""),
        "pauseBeforeTheFinalMatch": tkapp.time_before_the_final_match.get().replace("m", ""),
        "pauseBeforeKOMatches": tkapp.time_pause_before_KO.get().replace("m", ""),
        "halfTimePause": tkapp.half_time_pause.get().replace("m", ""),
    }
    #print("initial_data", initial_data)
    return make_response(render_template(template_name, initial_data=initial_data, base_url=base_url))


##############################################################################################
###################################### Google Auth ###########################################
##############################################################################################

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "450306821477-t53clamc7s8u20adedj2fqhv0904aa8t.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
admins_file = os.path.join(pathlib.Path(__file__).parent, "admins.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://technikag.serveo.net/callback"
)

def is_admin():
    if "email" in session:
        with open(admins_file, "r") as file:
            admins = json.load(file)
        print(session["email"] in admins)
        return session["email"] in admins
    else:
        return False

def login_is_required(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        if "google_id" not in session:
            session["next"] = request.url
            return redirect("/login")
        else:
            return function(*args, **kwargs)
    return decorator

@app.route("/login")
@limiter.limit("15 per minute", exempt_when=lambda: 'email' in session and is_admin())
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
@limiter.limit("15 per minute", exempt_when=lambda: 'email' in session and is_admin())
def callback():
    global session
    state = session.pop("state", None)  # Use pop to get and remove state from session
    if state is None or state != request.args.get("state"):
        return redirect("/login")

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)


    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID, 
        clock_skew_in_seconds=10
    )
  

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    return redirect(session.pop("next", "/"))
 
@app.route("/logout")
@limiter.limit("2 per minute", exempt_when=lambda: 'email' in session and is_admin())
def logout():
    session.clear()
    return redirect("/")


##############################################################################################
########################################## Tipping ###########################################
##############################################################################################

@app.route("/tipping_data")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
@login_is_required
def tipping_data_index():
    google_id = session["google_id"]
    
    getNameFromDB = """
    SELECT userName
    FROM userData
    WHERE googleId = ?
    """
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    cursor.execute(getNameFromDB, (google_id,))
    
    fetch_one = cursor.fetchone()
    
    if fetch_one is None:
        cursor.close()
        connection.close()
        return jsonify(name=None, tips=None)
    name = fetch_one[0]
    
    getTipsFromDB = """
    SELECT matchId, team1Goals, team2Goals
    FROM tippingData
    WHERE googleId = ?
    ORDER BY matchId ASC
    """
    
    cursor.execute(getTipsFromDB, (google_id,))
    
    fetch_all = cursor.fetchall()
    
    if fetch_all == []:
        cursor.close()
        connection.close()
        return jsonify(name=name, tips=None)
    
    tips = {row[0]: {"team1Goals": row[1], "team2Goals": row[2]} for row in fetch_all}
    
    cursor.close()
    connection.close()
    
    return jsonify(name=name, tips=tips)

@app.route("/send_tipping_data", methods=['POST'])
@limiter.limit("20 per minute", exempt_when=lambda: 'email' in session and is_admin())
@login_is_required
def send_tipping_data():
    google_id = session["google_id"]
    
    match_id = request.json['matchId']
    team1_goals = request.json['team1Goals']
    team2_goals = request.json['team2Goals']
    
    if match_id == "" or match_id == None:
        return "Please enter a valid match id", 400
    elif team1_goals == "" or team2_goals == "" or team1_goals == None or team2_goals == None:
        return "Please enter a valid number", 400
    
    
    if team1_goals == "" or team2_goals == "" or team1_goals == None or team2_goals == None:
        return "Please enter a valid number", 400
    
    try:
        team1_goals = int(team1_goals)
        team2_goals = int(team2_goals)
    except:
        return "Please enter a valid number", 400
    
    if team1_goals >= 25 or team2_goals >= 25:
        return "Please enter a valid number, too high", 400
    
    if match_id >= 0:
        if match_id <= tkapp.active_match:
            return "Match already started or finished", 400
    elif tkapp.active_match != -1 and tkapp.active_mode.get() == 2:
        match_id = (match_id * -1) - 2
        if match_id <= tkapp.active_match:
            return "Match already started or finished", 400
    elif tkapp.active_match != -1 and tkapp.active_mode.get() == 3:
        match_id = (match_id * -1) - 100
        if match_id <= tkapp.active_match:
            return "Match already started or finished", 400
            
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM tippingData WHERE googleId = ? AND matchId = ?", (google_id, match_id))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("UPDATE tippingData SET team1Goals = ?, team2Goals = ? WHERE googleId = ? AND matchId = ?", (team1_goals, team2_goals, google_id, match_id))
    else:
        cursor.execute("INSERT INTO tippingData (googleId, matchId, team1Goals, team2Goals) VALUES (?, ?, ?, ?)", (google_id, match_id, team1_goals, team2_goals))
    
    connection.commit()
    
    cursor.close()
    connection.close()

    tkapp.cache_vars["getmatches_changed_using_var"] = True
    tkapp.updated_data.update({"Matches": get_data_for_website(4)})
    
    return "Data successfully updated or inserted", 200

# send user name to db
@app.route("/send_user_name", methods=['POST'])
@limiter.limit("30 per minute", exempt_when=lambda: 'email' in session and is_admin())
@login_is_required
def send_user_name():
    google_id = session["google_id"]
    
    user_name = request.json['userName']
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM userData WHERE googleId = ?", (google_id,))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("UPDATE userData SET userName = ? WHERE googleId = ?", (user_name, google_id))
    else:
        cursor.execute("INSERT INTO userData (googleId, userName) VALUES (?, ?)", (google_id, user_name))
    
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify(message="Data successfully updated or inserted")


##############################################################################################
########################################### Sites ############################################
##############################################################################################

@app.route("/")
@limiter.limit("1 per minute", exempt_when=lambda: 'email' in session and is_admin())
def home():
    print("entered home")
    return get_initial_data("websitemain.html")

@app.route("/group")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def index():
    return get_initial_data("websitegroup.html")

@app.route("/tree")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def tree_index():
    return get_initial_data("websitetree.html")

@app.route("/plan")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def plan_index():
    return get_initial_data("websiteplan.html")

@app.route("/best_scorer")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def best_scorer_index():
    if tkapp.best_scorer_active.get() == 1:
        return get_initial_data("websitebestscorer.html")
    else:
        abort(404) 

@app.route("/tipping")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
@login_is_required
def tipping_index():
    return get_initial_data("websitetipping.html")

@app.route("/tv")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def tv_index():
    base_url = request.base_url
    return get_initial_data("websitetv.html", base_url)

@app.route("/admin")
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
@login_is_required
def admin_index():
    print("entered admin")
    if session.get("google_id"):
        print("google_id", session.get("google_id"))
    if session.get("name"):
        print("name", session.get("name"))
    if session.get("email"):
        print("email", session.get("email"))
    return get_initial_data("admin.html")

##############################################################################################
######################################### Handler ############################################
##############################################################################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify(error="ratelimit exceeded %s" % e.description), 429)


##############################################################################################
########################################### Data #############################################
##############################################################################################

@app.route('/best_scorer_data')
@limiter.limit("10 per minute", exempt_when=lambda: 'email' in session and is_admin())
def get_best_scorer_data():
    if tkapp.best_scorer_active.get() == 1:
        if tkapp.cache_vars.get("getbestscorer_changed_using_var") == True:
    
            getBestScorerDataQuery = """
            SELECT playerData.playerName, playerData.goals, teamData.teamName, DENSE_RANK() OVER (ORDER BY playerData.goals DESC) AS Rank 
            FROM playerData, teamData
            WHERE playerData.teamId = teamData.id
            ORDER BY playerData.goals DESC
            LIMIT 100
            """
            
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            
            cursor.execute(getBestScorerDataQuery)
            
            best_scorer_data = cursor.fetchall()
            
            output_json = []
            
            for player_data in best_scorer_data:
                new_json = {
                    "playerName": player_data[0],
                    "goals": player_data[1],
                    "teamName": player_data[2],
                    "rank": player_data[3]
                }
                output_json.append(new_json)
            
            cursor.close()
            connection.close()
            
            if output_json != []:
                tkapp.cache_vars["getbestscorer_changed_using_var"] = False
                
                tkapp.cache["BestScorer"] = output_json
            
            return jsonify(players=output_json)
        else:
            return jsonify(players=tkapp.cache.get("BestScorer"))
        
    else:
        abort(404)

@app.route('/update_data')
@limiter.limit("15 per minute", exempt_when=lambda: 'email' in session and is_admin())
def update_data():   
    timeatstart = time.time()
    
    last_data_update = request.headers.get('Last-Data-Update', 0)
    
    updated_data = tkapp.updated_data.copy()  # Create a copy to avoid modifying the original data
    
    if updated_data:
        keys_to_remove = []
        #print("updated_data", updated_data)
        #print("stored_data", stored_data)
        for key, value in updated_data.items():
            for key2, value2 in stored_data.items():
                if key in value2.keys():
                    keys_to_remove.append(key2)
                    
        for key in keys_to_remove:
            stored_data.pop(key)
            
            
        for key, value in updated_data.items():
            stored_data.update({timeatstart:{key:value}})
            timeatstart += 1  # Ensure unique keys for each update
        
    updated_data["LastUpdate"] = timeatstart  # Update 'LastUpdate' key only once
    
    for key, value in stored_data.items():
        if key >= float(last_data_update):
            updated_data.update(value)
    
    tkapp.delete_updated_data()

    return jsonify(updated_data)


##############################################################################################
########################################## Favicon ###########################################
##############################################################################################

@app.route('/favicon.ico')
@limiter.limit("10 per minute")
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
@limiter.limit("10 per minute")
def apple_touch_icon():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'apple-touch-icon.png', mimetype='image/png')

@app.route('/favicon-32x32.png')
@limiter.limit("10 per minute")
def favicon_32():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'favicon-32x32.png', mimetype='image/png')

@app.route('/favicon-16x16.png')
@limiter.limit("10 per minute")
def favicon_16():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'favicon-16x16.png', mimetype='image/png')

@app.route('/site.webmanifest')
@limiter.limit("10 per minute")
def site_webmanifest():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'site.webmanifest')

@app.route('/safari-pinned-tab.svg')
@limiter.limit("10 per minute")
def safari_pinned_tab():
    return send_from_directory(os.path.join(app.root_path, '../favicon'), 'safari-pinned-tab.svg', mimetype='image/svg+xml')


##############################################################################################
########################################### Init #############################################
##############################################################################################

global tkapp
global server_thread
global stored_data
global initial_data
global db_path


if platform.system() != 'Windows':
    try:
        subprocess.Popen(['Xvfb', ':1', '-screen', '0', '1024x768x16'])
        os.environ['DISPLAY'] = ":1"
    except:
        os.environ['DISPLAY']
        os.environ['DISPLAY'] = ":1"

start_server_and_ssh = True

db_path = "data/data.db"
stored_data = {}
tkapp = Window(start_server_and_ssh)

if start_server_and_ssh:
    subprocess.Popen(["python", "code/serveo_shh_connect.py"])

if __name__ == "__main__":
    tkapp.mainloop()