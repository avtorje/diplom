import tkinter as tk
from tkinter import ttk
from database import Database

class ResultForm(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.title("Результаты тестов")
        self.geometry("600x400")
        self.parent = parent

        tk.Label(self, text="Ваши результаты тестов", font=("Arial", 16)).pack(pady=10)

        self.results_tree = ttk.Treeview(self, columns=("Тест", "Результат (%)", "Дата"), show="headings")
        for col, rus in zip(("Тест", "Результат (%)", "Дата"), ("Тест", "Результат (%)", "Дата")):
            self.results_tree.heading(col, text=rus)
        self.results_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self, text="Назад", command=self.go_back).pack(pady=10)

        self.load_results()

    def load_results(self):
        # Ожидается, что get_results_by_student возвращает (id, test_name, score, date)
        for result in self.db.get_results_by_student(self.user_id):
            self.results_tree.insert("", tk.END, values=result[1:4])

    def go_back(self):
        self.destroy()
        self.parent.deiconify()