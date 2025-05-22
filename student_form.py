import tkinter as tk
from tkinter import messagebox
from database import Database
from test_form import TestForm
from result_form import ResultForm

class StudentForm(tk.Toplevel):
    def __init__(self, user_id, username):
        super().__init__()
        self.db = Database()
        self.user_id = user_id
        self.username = username
        self.title(f"Панель студента - {username}")
        self.geometry("400x300")

        tk.Label(self, text=f"Добро пожаловать, {username}!", font=("Arial", 16)).pack(pady=10)
        tk.Label(self, text="Выберите тест").pack(pady=5)

        self.theme_var = tk.StringVar(self)
        self.theme_dropdown = tk.OptionMenu(self, self.theme_var, "")
        self.theme_dropdown.pack(pady=5)

        tk.Button(self, text="Начать тест", command=self.start_test).pack(pady=5)
        tk.Button(self, text="Посмотреть результаты", command=lambda: self.open_form(ResultForm, self.user_id)).pack(pady=5)
        tk.Button(self, text="Выйти", command=self.logout).pack(pady=5)

        self.load_themes()

    def load_themes(self):
        themes = self.db.get_all_tests()
        menu = self.theme_dropdown["menu"]
        menu.delete(0, "end")
        if themes:
            for theme_id, theme_name in themes:
                menu.add_command(label=theme_name, command=lambda v=theme_name: self.theme_var.set(v))
            self.theme_var.set(themes[0][1])
        else:
            self.theme_var.set("Нет доступных тестов")

    def start_test(self):
        selected_theme = self.theme_var.get()
        theme_id = self.db.get_test_id(selected_theme)
        if theme_id:
            self.open_form(TestForm, self.user_id, theme_id)
        else:
            messagebox.showerror("Ошибка", "Выберите корректный тест.")

    def open_form(self, form_class, *args):
        self.withdraw()
        form_class(self, *args).mainloop()

    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.destroy()
