import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import threading
import requests
import os
import time
from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect

app = Flask(__name__)
app.secret_key = "Felix.com"

lock = threading.Lock()

class Window(tk.Tk):
    def create_navigation_bar(self):
        navigation_frame = tk.Frame(self, bg="lightgray")
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y)

        buttons = [
            ("Home", self.show_home_frame),
            ("About", self.show_about_frame),
            ("Services", self.show_services_frame),
            ("Contact", self.show_contact_frame),
        ]

        button_width = 10  # Set a fixed width for all buttons

        for text, command in buttons:
            button = tk.Button(navigation_frame, text=text, command=command, width=button_width, pady=5)
            button.pack(side=tk.TOP, anchor=tk.W)
            
            
            
    def __init__(self):
        super().__init__()
        self.name_entries = []
        self.label_list = []

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
        self.home_frame = tk.Frame(self, bg="lightblue")
        self.about_frame = tk.Frame(self, bg="lightgreen")
        self.services_frame = tk.Frame(self, bg="lightcoral")
        self.contact_frame = tk.Frame(self, bg="lightyellow")

        # Create elements for each frame
        self.create_home_elements()
        self.create_about_elements()
        self.create_services_elements()
        self.create_contact_elements()

        # Display the default frame
        self.show_frame(self.home_frame)

            
            
##############################################################################################
    def add_name_entry(self, entry_text=""):
        count = len(self.name_entries) + 1

        # Create a label with "Team 1" and the count
        label_text = f'Team {count}'
        label = tk.Label(self.frame, text=label_text)
        label.grid(row=len(self.name_entries), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = tk.Entry(self.frame)
        
        #write entry_text to the entry field if it is not empty
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
                if entry != "":
                    f.write(entry.get() + "\n")
                
    def read_names(self):
        with open("names.txt", "r") as f:
            for line in f:
                self.add_name_entry()
                self.name_entries[-1].insert(0, line.strip())
        
        return self.name_entries
    
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


    def create_home_elements(self):
        
        # Read the names from the file at the start of the program and put them into the entry fields
        
        
        
        # Create elements for the Home frame
        canvas = tk.Canvas(self.home_frame, bg="lightblue")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ttk.Scrollbar(self.home_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frame = tk.Frame(canvas, bg="lightblue")
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        name_entries = []
        self.write_names_into_entry_fields()

        self.frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        # Button to add a new name entry
        add_button = ttk.Button(self.home_frame, text="Add Name", command=self.add_name_entry)
        add_button.pack(pady=10)

        # Button to retrieve the entered names


        submit_button = ttk.Button(self.home_frame, text="Submit", command=self.save_names)
        submit_button.pack(pady=10)

        
        reload_button = tk.Button(self.home_frame, text="Reload", command=self.reload_button_command)
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
        for frm in [self.home_frame, self.about_frame, self.services_frame, self.contact_frame]:
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def show_home_frame(self):
        self.show_frame(self.home_frame)

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

@app.route("/")
def index():
    resp = make_response(render_template(".html"))
    return resp


if __name__ == "__main__":
    
    tkapp = Window()
    tkapp.mainloop()
    
    #app.run(debug=False, threaded=True, port=5000, host="0.0.0.0", use_reloader=True)