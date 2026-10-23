import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st

class LauncherWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Gateway Collection Tool Launcher")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.frame = ttk.Frame(root, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(self.frame, text="Initializing...", font=("Helvetica", 12, "bold"))
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.detail_label = ttk.Label(self.frame, text="Preparing system...", font=("Helvetica", 9))
        self.detail_label.pack(anchor=tk.W, pady=(0, 15))
        
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=360, mode="indeterminate")
        self.progress.pack(fill=tk.X, expand=True)

        self.log_box = st.ScrolledText(root, width = 40, height=10, wrap=tk.WORD)
        self.log_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.progress.start(10)

    def update_ui(self, status, detail, is_finished=False):
        """Thread-safe method called by the logic script to update the UI."""
        self.root.after(0, lambda: self._safe_update(status, detail, is_finished))

    def add_log(self, text):
        self.root.after(0, lambda: self._safe_add_log(text))

    def _safe_add_log(self, text):
        self.log_box.insert(tk.END, f"{text}\n")

    def _safe_update(self, status, detail, is_finished):
        self.status_label.config(text=status)
        self.detail_label.config(text=detail)
        
        if is_finished:
            self.progress.stop()
            self.root.after(5000, self.root.destroy)