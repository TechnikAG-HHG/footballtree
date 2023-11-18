import tkinter as tk
from tkinter import ttk

def add_name_entry():
    new_entry = ttk.Entry(frame)
    new_entry.grid(row=len(name_entries), column=0, pady=5, sticky='we')
    name_entries.append(new_entry)

def on_frame_configure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

root = tk.Tk()
root.title("Team Names Input")

# Create a canvas to hold the frame
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

# Create a scrollbar and connect it to the canvas
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame to hold the team name entries
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Add an initial entry field
name_entries = []
add_name_entry()

# Bind the frame to the scroll event
frame.bind("<Configure>", lambda event, canvas=canvas: on_frame_configure(canvas))

# Button to add a new name entry
add_button = ttk.Button(root, text="Add Name", command=add_name_entry)
add_button.pack(pady=10)

# Button to retrieve the entered names
def get_names():
    team_names = [entry.get() for entry in name_entries if entry.get()]
    print("Team Names:", team_names)

submit_button = ttk.Button(root, text="Submit", command=get_names)
submit_button.pack(pady=10)

root.mainloop()
