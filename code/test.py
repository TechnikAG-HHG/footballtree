import tkinter as tk
from tkinter import ttk

def exersize_check_button_function():
    print("Exersize 1: " + str(exersize_radio_var.get()))

window = tk.Tk()
window.title("Tkinter Exersize")

exersize_check_button_var = tk.BooleanVar(value=False)

exersize_check_button = ttk.Checkbutton(window, text="Exersize Check", command=exersize_check_button_function, variable=exersize_check_button_var)
exersize_check_button.pack()

exersize_radio_var = tk.IntVar()

exersize_radio1 = ttk.Radiobutton(window, text="Exersize 1", value=1, variable=exersize_radio_var)
exersize_radio1.pack()

exersize_radio2 = ttk.Radiobutton(window, text="Exersize 2", value=2, variable=exersize_radio_var)
exersize_radio2.pack()



window.mainloop()