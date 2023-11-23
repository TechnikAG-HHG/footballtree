import tkinter as tk

def button_click(button_number):
    print(f"Button {button_number} clicked!")

root = tk.Tk()
root.title("Variable Buttons Example")

# Create a variable number of buttons
num_buttons = 10  # You can change this to the desired number of buttons

up_frame = tk.Frame(root)
up_frame.pack(side=tk.TOP)

down_frame = tk.Frame(root)
down_frame.pack(side=tk.BOTTOM)

for i in range(num_buttons):
    # Place the first 6 buttons at the top, and the rest using a different layout option
    if i < 6:
        button = tk.Button(up_frame, text=f"Button {i+1}", command=lambda i=i: button_click(i+1), width=15)
        button.pack(side=tk.LEFT, anchor=tk.N)
    else:
        button = tk.Button(down_frame, text=f"Button {i+1}", command=lambda i=i: button_click(i+1), width=15)
        button.pack(side=tk.LEFT, anchor=tk.S)

root.mainloop()
