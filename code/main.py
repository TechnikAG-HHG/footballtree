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
            
            
    def __init__(self):
        super().__init__()
        self.name_entries = []
        self.label_list = []
        self.updated_data = {}
        self.variable_dict = {}
        self.team_button_list = []
        self.spiel_buttons = {}

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
        
        #server_thread = threading.Thread(target=self.start_server)
        #server_thread.start()
        
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
                    f.write(entry.get() + "\n")
        self.updated_data.update({"Teams": self.read_team_names()})

                
    def read_team_names(self, teams_to_read="all"):
        with open("data/team_names.txt", "r") as f:
            self.name_entries_read = []
            if teams_to_read == "all":
                for line in f:
                    self.name_entries_read.append(line.replace("\n", ""))
            else:
                for i, line in enumerate(f):
                    if i in teams_to_read:
                        self.name_entries_read.append(line.replace("\n", ""))
        
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
        
    def save_names_player(self):
        entries = self.variable_dict.get(f"entries{self.frameplayer}")

        if entries:
            with open(f"data/{self.selected_team}.txt", "w+") as f:
                for entry in entries:
                    # Check if the entry widget exists
                    if entry.winfo_exists():
                        entry_text = entry.get()
                        if entry_text and entry_text != "\n":
                            f.write(entry_text + "\n")

        ###self.updated_data.update({"Players": {self.selected_team: self.read_team_names_player(self.selected_team)}})
            
    
    def add_name_entry_player(self, Frame, Counter, entry_text=""):
        varcountname = f"count{Frame}"
        varentriesname = f"entries{Frame}"
        varlabelname = f"label{Frame}"

        # Check if the variable already exists in the dictionary
        if varcountname not in self.variable_dict:
            self.variable_dict[varcountname] = 0  # Initialize count to 0

        if varentriesname not in self.variable_dict:
            self.variable_dict[varentriesname] = []

        if varlabelname not in self.variable_dict:
            self.variable_dict[varlabelname] = []

        # Now you can access the count using the dynamic variable name
        count = self.variable_dict[varcountname] + 1

        # Update the count in the dictionary
        self.variable_dict[varcountname] = count

        # Create a label with "Team 1" and the count
        label_text = f'{Counter} {count}'
        label = tk.Label(Frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.variable_dict[varentriesname]), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = tk.Entry(Frame, font=("Helvetica", 14))  # Increase font size
        #print("entry_text", entry_text)
        #print("new_entry")

        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)

        new_entry.grid(row=len(self.variable_dict[varentriesname]), column=1, pady=5, sticky='we')
        self.variable_dict[varentriesname].append(new_entry)
        self.variable_dict[varlabelname].append(label)

    
    
    def write_names_into_entry_fields_players(self, txt_file, Counter, Frame):
        try:
            with open(f"data/{txt_file}.txt", "r") as f:
                # if the file is empty, do nothing
                if os.stat(f"data/{txt_file}.txt").st_size == 0:
                    self.add_name_entry_player(Frame, Counter)

                
                # if the file is not empty, read the names from the file and put them into the entry fields
                else:
                    for i, line in enumerate(f):
                        print("line", line)
                        if line != "\n" and line != "":
                            self.add_name_entry_player(Frame, Counter, line.replace("\n", ""))
                        
                        if i == 1 and line == "\n" or i == 1 and line == "":
                            self.add_name_entry_player(Frame, Counter)    
                            
                    return False
        except FileNotFoundError:
            print("File not found")
            #create file
            
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
        varentriesname = f"entries{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentriesname):
            # Access the value associated with the key
            if self.variable_dict[varentriesname] != []:
                for entry in self.variable_dict[varentriesname]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
        
        
        
        self.variable_dict[varcountname] = 0
            
    
    
    
    def select_team(self, team_name, team_button_list, index):
        
        for button in team_button_list:
            button.config(bg="lightgray")
        
        team_button = team_button_list[index]
        
        team_button.config(bg="red")
        
        varcountname = f"count{str(self.frameplayer)}"
        varentriesname = f"entries{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentriesname):
            # Access the value associated with the key
            if self.variable_dict[varentriesname] != []:
                for entry in self.variable_dict[varentriesname]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
        
        self.selected_team = team_name
        
        self.variable_dict[varcountname] = 0
        
        self.write_names_into_entry_fields_players(team_name, "Player", self.frameplayer)
            
        
    
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
        SPIEL_button = tk.Button(self.SPIEL_frame, text="SPIEL Button", command=self.SPIEL_button_command)
        SPIEL_button.pack(pady=10)
        
        
        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}

        self.teams_playing = [1,2]

        # Inside your loop
        for team in self.read_team_names(self.teams_playing):
            print(team)
            try:
                with open(f"data/{team}.txt", "r") as f:
                    for i, line in enumerate(f):
                        # Create a new frame for each group
                        group_frame = tk.Frame(self.SPIEL_frame, background="lightcoral")
                        group_frame.pack(pady=10, anchor=tk.NW)

                        playertext1 = tk.Label(group_frame, text=line.strip(), font=("Helvetica", 14))
                        playertext1.pack(side=tk.TOP)

                        playerbutton = tk.Button(group_frame, text=line.strip(), command=self.test)
                        playerbutton.pack(side=tk.TOP)

                        #self.spiel_buttons[team] = (playerbutton)  # Use append for a list

            except FileNotFoundError:
                with open(f"data/{team}.txt", "w+") as f:
                    f.write("")


                
                
        

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
        self.show_frame(self.SPIEL_frame)

    #def show_contact_frame(self):
        #self.show_frame(self.contact_frame)

    # Button command functions

    def player_button_command(self):
        print("player Button Clicked")

    def SPIEL_button_command(self):
        print("SPIEL Button Clicked")

    #def contact_button_command(self):
        #print("Contact Button Clicked")
        
    ##############################################################################################
            
    def test(self):
        print("test")
        
    def delete_updated_data(self):
        print("delete")
        print(self.updated_data)
        self.updated_data = {}
        
    ##############################################################################################

@app.route("/")
def index():
    tkapp.test()
    initial_data = {}  # You can modify this data as needed
    initial_data["Teams"] = tkapp.read_team_names()
    initial_data["LastUpdate"] = 0
    resp = make_response(render_template("websitegroup.html", initial_data=initial_data))
    return resp

@app.route("/tree")
def tree_index():
    tkapp.test()
    initial_data = {}  # You can modify this data as needed
    initial_data["Teams"] = tkapp.read_team_names()
    initial_data["LastUpdate"] = 0
    resp = make_response(render_template("websitetree.html", initial_data=initial_data))
    return resp

@app.route("/plan")
def plan_index():
    tkapp.test()
    initial_data = {}  # You can modify this data as needed
    initial_data["Teams"] = tkapp.read_team_names()
    initial_data["LastUpdate"] = 0
    resp = make_response(render_template("websiteplan.html", initial_data=initial_data))
    return resp

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

global tkapp
global server_thread
global stored_data

stored_data = {}
tkapp = Window()

if __name__ == "__main__":
    
    
    tkapp.mainloop()
    