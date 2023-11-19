import tkinter as tk
from tkinter import simpledialog

def read_teams_from_file(file_path):
    with open(file_path, 'r') as file:
        teams = [line.strip() for line in file.readlines() if line.strip()]
    return teams

def open_team_window(team_name):
    team_window = tk.Toplevel(root)
    team_window.title(f"Enter Names for {team_name}")

    def save_names():
        names = entry.get("1.0", "end-1c").split('\n')
        names = [name.strip() for name in names if name.strip()]
        print(f"Names for {team_name}: {names}")
        team_window.destroy()

    tk.Label(team_window, text=f"Enter names for {team_name} (one per line):").pack(pady=10)
    entry = tk.Text(team_window, height=5, width=30)
    entry.pack(pady=10)

    save_button = tk.Button(team_window, text="Save", command=save_names)
    save_button.pack(pady=10)

# Read teams from file
teams_list = read_teams_from_file('names.txt')

# Create main window
root = tk.Tk()
root.title("Team Names")

# Create buttons for each team
for team_name in teams_list:
    team_button = tk.Button(root, text=team_name, command=lambda name=team_name: open_team_window(name))
    team_button.pack(pady=5)

root.mainloop()
