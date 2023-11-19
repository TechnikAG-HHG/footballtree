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
            ("About", self.show_about_frame),
            ("Services", self.show_services_frame),
            ("Contact", self.show_contact_frame),
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
        self.about_frame = tk.Frame(self, bg="lightgreen")
        self.services_frame = tk.Frame(self, bg="lightcoral")
        self.contact_frame = tk.Frame(self, bg="lightyellow")

        # Create elements for each frame
        self.create_Team_elements()
        self.create_about_elements()
        self.create_services_elements()
        self.create_contact_elements()

        # Display the default frame
        self.show_frame(self.Team_frame)
        
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
        with open("names.txt", "w+") as f:
            for entry in self.name_entries:
                if entry != "" and entry != "\n":
                    f.write(entry.get() + "\n")
        self.updated_data.update({"Teams": self.read_team_names()})

                
    def read_team_names(self):
        with open("names.txt", "r") as f:
            self.name_entries_read = []
            for line in f:
                self.name_entries_read.append(line.replace("\n", ""))
        
        return self.name_entries_read
    
    def write_names_into_entry_fields(self):
        try:
            with open("names.txt", "r") as f:
                # if the file is empty, do nothing
                if os.stat("names.txt").st_size == 0:
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

    def create_about_elements(self):
        # Create elements for the About frame
        about_button = tk.Button(self.about_frame, text="About Button", command=self.about_button_command)
        about_button.pack(pady=10)
        

##############################################################################################

##############################################################################################

    def create_services_elements(self):
        # Create elements for the Services frame
        services_button = tk.Button(self.services_frame, text="Services Button", command=self.services_button_command)
        services_button.pack(pady=10)
        

##############################################################################################

##############################################################################################

    def create_contact_elements(self):
        # Create elements for the Contact frame
        contact_button = tk.Button(self.contact_frame, text="Contact Button", command=self.contact_button_command)
        contact_button.pack(pady=10)
        

##############################################################################################

    def show_frame(self, frame):
        # Hide all frames and pack the selected frame
        for frm in [self.Team_frame, self.about_frame, self.services_frame, self.contact_frame]:
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def show_Team_frame(self):
        self.reload_button_command()
        self.show_frame(self.Team_frame)

    def show_about_frame(self):
        self.show_frame(self.about_frame)

    def show_services_frame(self):
        self.show_frame(self.services_frame)

    def show_contact_frame(self):
        self.show_frame(self.contact_frame)

    # Button command functions

    def about_button_command(self):
        print("About Button Clicked")

    def services_button_command(self):
        print("Services Button Clicked")

    def contact_button_command(self):
        print("Contact Button Clicked")
        
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
    resp = make_response(render_template("index.html", initial_data=initial_data))
    return resp

@app.route('/update_data')
def update_data():
    
    timeatstart = time.time()
    
    last_data_update = request.headers.get('Last-Data-Update', 0)
    print(last_data_update)
    
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
        print("magucken")
        if key >= float(last_data_update):
            print("key", key, "value", value, "last_data_update", last_data_update, "should be updated")
            updated_data.update(value)
            print("updated_data", updated_data)
            
    
    print("stored_data", stored_data, "updated_data", updated_data, "last_data_update", last_data_update)
        
    print(updated_data)
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
    