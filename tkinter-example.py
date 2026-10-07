import tkinter as tk
from tkinter import messagebox

# 1. Create the main application window
root = tk.Tk()
root.title("Simple GUI Example")
root.geometry("400x200")  # Width x Height

# 2. Define the button action (the logic)
def on_submit():
    user_input = entry.get()  # Get text from the input field
    if user_input.strip() == "":
        messagebox.showwarning("Warning", "Please enter a name!")
    else:
        # Update the result label with a greeting
        result_label.config(text=f"Hello, {user_input}! Welcome.")

# 3. Create and pack UI widgets (elements)
# Add a prompt label
label = tk.Label(root, text="Enter your name:", font=("Arial", 12))
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

# 4. Start the GUI application event loop
root.mainloop()
