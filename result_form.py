import tkinter as tk
from tkinter import ttk
from database import Database

class ResultForm(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.title("Your Results")
        self.geometry("600x400")
        self.parent = parent

        tk.Label(self, text="Your Test Results", font=("Arial", 16)).pack(pady=10)

        self.results_tree = ttk.Treeview(self, columns=("Test", "Score", "Date"), show="headings")
        for col in ("Test", "Score", "Date"):
            self.results_tree.heading(col, text=col)
        self.results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self, text="Back", command=self.go_back).pack(pady=10)

        self.load_results()

    def load_results(self):
        for result in self.db.get_results_by_student(self.user_id):
            self.results_tree.insert("", tk.END, values=result[1:4])

    def go_back(self):
        self.destroy()
        self.parent.deiconify()
