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

        # Dropdowns for viewing statistics
        tk.Label(self, text="Select Student").pack(pady=5)
        self.student_var = tk.StringVar(self)
        self.student_dropdown = ttk.Combobox(self, textvariable=self.student_var)
        self.student_dropdown.pack(pady=5)
        self.load_students()

        tk.Label(self, text="Select Test").pack(pady=5)
        self.test_var = tk.StringVar(self)
        self.test_dropdown = ttk.Combobox(self, textvariable=self.test_var)
        self.test_dropdown.pack(pady=5)
        self.load_tests()

        tk.Button(self, text="View by Student", command=self.view_by_student).pack(pady=5)
        tk.Button(self, text="View by Test", command=self.view_by_test).pack(pady=5)

        self.results_tree = ttk.Treeview(self, columns=("Username", "Test", "Score", "Date"), show="headings")
        self.results_tree.heading("Username", text="Username")
        self.results_tree.heading("Test", text="Test")
        self.results_tree.heading("Score", text="Score")
        self.results_tree.heading("Date", text="Date")
        self.results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self, text="Back", command=self.go_back).pack(pady=5)

    def load_students(self):
        students = self.db.get_all_students()
        self.student_dropdown["values"] = [f"{student[0]}: {student[1]}" for student in students]

    def load_tests(self):
        tests = self.db.get_all_tests()
        self.test_dropdown["values"] = [f"{test[0]}: {test[1]}" for test in tests]

    def view_by_student(self):
        selected = self.student_var.get()
        if not selected:
            return
        student_id = int(selected.split(":")[0])
        results = self.db.get_results_by_student(student_id)
        self.populate_results(results)

    def view_by_test(self):
        selected = self.test_var.get()
        if not selected:
            return
        test_id = int(selected.split(":")[0])
        results = self.db.get_results_by_test(test_id)
        self.populate_results(results)

    def populate_results(self, results):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for result in results:
            self.results_tree.insert("", tk.END, values=result)

    def go_back(self):
        self.destroy()
        self.parent.deiconify()