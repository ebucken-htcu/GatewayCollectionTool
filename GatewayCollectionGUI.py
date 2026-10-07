from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class AppController(tk.Tk):
    def __init__(main_frame):
        super().__init__()
        main_frame.title("Gateway Collection Tool")
        main_frame.geometry("640x360")

        container = tk.Frame(main_frame)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        main_frame.frames = {}

        for ScreenClass in (StartScreen, MainScreen):
            frame = ScreenClass(parent=container, controller=self)
            main_frame.frames[ScreenClass] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")
        
        main_frame.show_frame(StartScreen)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()


class StartScreen(tk.Frame):
    def __init__(start_screen, parent, controller):
        super().__init__(parent)
        start_screen.controller = controller

    label = tk.Label(, text="Enter Case Number:", font=("Arial", 12))
label.pack(pady=10)  # pady adds vertical spacing

# Add a text entry field
entry = tk.Entry(root, font=("Arial", 12), width=25)
entry.pack(pady=5)

# Add a submit button
submit_button = tk.Button(root, text="Submit", font=("Arial", 10, "bold"), command=on_submit)
submit_button.pack(pady=10)

# Add a label to display the output
result_label = tk.Label(root, text="", font=("Arial", 12, "italic"), fg="blue")
result_label.pack(pady=10)

# 2. Define the button action (the logic)
def on_submit():
    user_input = entry.get()  # Get text from the input field
    if user_input.strip() == "":
        messagebox.showwarning("Warning", "Please enter a name!")
    else:
        case_folder = Path(f"{user_input}")
        case_folder.mkdir(parents=True, exist_ok=True)



# 4. Start the GUI application event loop

root.mainloop()
