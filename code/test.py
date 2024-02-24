import tkinter as tk
import time

def update_label():
    current_time = time.strftime("%H:%M:%S")
    label.config(text=current_time)
    label.after(1000, update_label)  # Update label every 1 second

root = tk.Tk()
label = tk.Label(root, font=("Arial", 24))
label.pack()

update_label()  # Start updating the label

root.mainloop()