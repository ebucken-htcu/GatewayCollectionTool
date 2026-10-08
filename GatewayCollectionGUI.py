from datetime import datetime
from pathlib import Path
import tkinter as tk
import ResidentialScan
from tkinter import messagebox
from tkinter import filedialog

case_number = "-1"
report_location = "\\"
agency = ""
analyst = ""

def make_case_folder():
    case_folder = Path(f"{report_location}\\{case_number}")
    case_folder.mkdir(parents=True, exist_ok=True)

def set_case_number(number):
    global case_number
    case_number = number

def set_report_location(location):
    global report_location
    report_location = location

def set_agency(name):
    global agency
    agency = name

def set_analyst(name):
    global analyst
    analyst = name


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
            frame = ScreenClass(parent=container, controller=main_frame)
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

        def browse_directory():
            dir_path = filedialog.askdirectory(title="Select a folder", initialdir="/")
            if  dir_path:
                global report_location
                report_location = dir_path
                report_location_entry.delete(0, tk.END)
                report_location_entry.insert(0, report_location)

        def is_entry_blank(entry):
            user_input = entry.get()
            if user_input.strip() == "":
                return True
            else:
                return False

        def on_submit():
            if is_entry_blank(case_number_entry) == False:
                set_case_number(case_number_entry.get())
            else:
                messagebox.showwarning("Warning", "Please enter a Case Number!")
                return
            
            if is_entry_blank(agency_entry) == False:
                set_agency(agency_entry.get())
            else:
                messagebox.showwarning("Warning", "Please enter an Agency!")
                return
            
            if is_entry_blank(analyst_entry) == False:
                set_analyst(analyst_entry.get())
            else:
                messagebox.showwarning("Warning", "Please enter an Analyst!")
                return
            
            if is_entry_blank(report_location_entry) == False:
                set_agency(report_location_entry.get())
            else:
                messagebox.showwarning("Warning", "Please enter a Report Location!")
                return

            make_case_folder()
            start_screen.controller.show_frame(MainScreen)
            

        title = tk.Label(start_screen, text="Gateway Collection Tool", font=("Arial", 18))
        title.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        case_number_title = tk.Label(start_screen, text="Case Number:", font=("Arial", 12))
        case_number_entry = tk.Entry(start_screen, font=("Arial", 12), width=25)
        case_number_title.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        case_number_entry.grid(row=1, column=1, padx=10, pady=10)

        agency_title = tk.Label(start_screen, text="Agency:", font=("Arial", 12))
        agency_entry = tk.Entry(start_screen, font=("Arial", 12), width=25)
        agency_title.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        agency_entry.grid(row=2, column=1, padx=10, pady=10)

        analyst_title = tk.Label(start_screen, text="Analyst:", font=("Arial", 12))
        analyst_entry = tk.Entry(start_screen, font=("Arial", 12), width=25)
        analyst_title.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        analyst_entry.grid(row=3, column=1, padx=10, pady=10)

        report_location_title = tk.Label(start_screen, text="Report Location:", font=("Arial", 12))
        report_location_entry = tk.Entry(start_screen, font=("Arial", 12), width=25)
        report_location_button = tk.Button(start_screen, text="Browse Folder...", command=browse_directory)
        report_location_title.grid(row=4, column=0, padx=0, pady=10, sticky="e")
        report_location_entry.grid(row=4, column=1, padx=0, pady=10)
        report_location_button.grid(row=4, column=2, padx=0, pady=0)

        submit_button = tk.Button(start_screen, text="Submit", font=("Arial", 10, "bold"), command=on_submit)
        submit_button.grid(row=5, column=1, padx=10, pady=10)



class MainScreen(tk.Frame):
    def __init__(main_screen, parent, controller):
            scan_type = ""
            
            super().__init__(parent)
            main_screen.controller = controller

            def start_scan():
                start_scan_button['state'] = tk.DISABLED
                if (residential_scan_button['state'] == tk.DISABLED):
                    print(f"[+] Started Residential Scan")
                    ResidentialScan.main(case_number, report_location, agency, analyst)
                    print(f"[+] Residential Scan is done")
                    start_scan_button['state'] = tk.NORMAL
                    residential_scan_button['state'] = tk.NORMAL
                    messagebox.showinfo("Scan Complete!", "The Residential Scan is now complete! You can now run another scan")


            def residential_scan():
                residential_scan_button['state'] = tk.DISABLED

            title = tk.Label(main_screen, text="Gateway Collection Tool", font=("Arial", 18))
            title.grid(row=0, column=1, padx=10, pady=10, sticky="e")

            pick_scan_title = tk.Label(main_screen, text="Please Pick a Scan From Below:", font=("Arial", 18))
            pick_scan_title.grid(row=1, column=1, padx=10, pady=10, sticky="e")

            residential_scan_button = tk.Button(main_screen, text="Residential Scan", font=("Arial", 10, "bold"), command=residential_scan)
            residential_scan_button.grid(row=2, column=0, padx=10, pady=10)

            start_scan_button = tk.Button(main_screen, text="Start Scan", font=("Arial", 10, "bold"), command=start_scan)
            start_scan_button.grid(row=3, column=1, padx=10, pady=10)


if __name__ == "__main__":
    app = AppController()
    app.mainloop()
