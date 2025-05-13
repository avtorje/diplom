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
        self.create_widgets()
        self.load_results()

    def create_widgets(self):
        tk.Label(self, text="Your Test Results", font=("Arial", 16)).pack(pady=10)

        self.results_tree = ttk.Treeview(self, columns=("Test", "Score", "Date"), show="headings")
        self.results_tree.heading("Test", text="Test")
        self.results_tree.heading("Score", text="Score")
        self.results_tree.heading("Date", text="Date")
        self.results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self, text="Back", command=self.go_back).pack(pady=10)

    def load_results(self):
        results = self.db.get_results_by_student(self.user_id)
        for result in results:
            self.results_tree.insert("", tk.END, values=(result[1], result[2], result[3]))

    def go_back(self):
        self.destroy()
        self.parent.deiconify()