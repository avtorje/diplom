import tkinter as tk
from tkinter import messagebox
from database import Database
from test_form import TestForm

class TestSelectionForm(tk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.title("Выбор теста")
        self.geometry("400x300")
        self.resizable(False, False)
        self.center_window()

        tk.Label(self, text="Доступные тесты:", font=("Arial", 14, "bold")).pack(pady=10)

        self.tests_listbox = tk.Listbox(self, font=("Arial", 12))
        self.tests_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tests_listbox.bind("<Double-Button-1>", self.start_test)

        tk.Button(self, text="Назад", command=self.go_back).pack(pady=10)

        self.load_tests()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 400
            height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_tests(self):
        group_id = self.db.get_user_group_id(self.user_id)
        self.tests = self.db.get_all_tests(group_id=group_id)  # [(id, name), ...]
        self.tests_listbox.delete(0, tk.END)
        if self.tests:
            for _, test_name in self.tests:
                self.tests_listbox.insert(tk.END, test_name)
        else:
            self.tests_listbox.insert(tk.END, "Нет доступных тестов")
            self.tests_listbox.config(state=tk.DISABLED)

    def start_test(self, event):
        selection = self.tests_listbox.curselection()
        if not selection or not self.tests:
            return
        idx = selection[0]
        test_id, test_name = self.tests[idx]
        self.withdraw()
        TestForm(self, self.user_id, test_id).mainloop()
        self.deiconify()

    def go_back(self):
        self.destroy()
        self.master.deiconify()