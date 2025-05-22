import tkinter as tk
from tkinter import ttk
from database import Database

class StatisticsForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Statistics")
        self.geometry("600x400")
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Statistics", font=("Arial", 16)).pack(pady=10)

        self.student_var = tk.StringVar(self)
        self.test_var = tk.StringVar(self)

        self.create_dropdown("Select Student", self.student_var, self.db.get_all_students, "student")
        self.create_dropdown("Select Test", self.test_var, self.db.get_all_tests, "test")

        tk.Button(self, text="View by Student", command=lambda: self.view_results(self.student_var, self.db.get_results_by_student)).pack(pady=5)
        tk.Button(self, text="View by Test", command=lambda: self.view_results(self.test_var, self.db.get_results_by_test)).pack(pady=5)

        self.results_tree = ttk.Treeview(self, columns=("Username", "Test", "Score", "Date"), show="headings")
        for col in ("Username", "Test", "Score", "Date"):
            self.results_tree.heading(col, text=col)
        self.results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self, text="Back", command=self.go_back).pack(pady=5)

    def create_dropdown(self, label_text, var, data_func, attr):
        tk.Label(self, text=label_text).pack(pady=5)
        dropdown = ttk.Combobox(self, textvariable=var)
        dropdown.pack(pady=5)
        items = data_func()
        dropdown["values"] = [f"{item[0]}: {item[1]}" for item in items]
        setattr(self, f"{attr}_dropdown", dropdown)

    def view_results(self, var, results_func):
        selected = var.get()
        if not selected:
            return
        id_ = int(selected.split(":")[0])
        results = results_func(id_)
        self.populate_results(results)

    def populate_results(self, results):
        self.results_tree.delete(*self.results_tree.get_children())
        for result in results:
            self.results_tree.insert("", tk.END, values=result)

    def go_back(self):
        self.destroy()
        self.parent.deiconify()
