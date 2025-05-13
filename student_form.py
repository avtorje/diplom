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

        self.create_widgets()
        self.load_themes()

    def create_widgets(self):
        tk.Label(self, text=f"Добро пожаловать, {self.username}!", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="Выберите тест").pack(pady=5)
        self.theme_var = tk.StringVar(self)
        self.theme_dropdown = tk.OptionMenu(self, self.theme_var, [])
        self.theme_dropdown.pack(pady=5)

        tk.Button(self, text="Начать тест", command=self.start_test).pack(pady=5)
        tk.Button(self, text="Посмотреть результаты", command=self.view_results).pack(pady=5)
        tk.Button(self, text="Выйти", command=self.logout).pack(pady=5)

    def load_themes(self):
        themes = self.db.get_all_tests()
        if themes:
            self.theme_var.set(themes[0][1])  # Установить первый тест как значение по умолчанию
            self.theme_dropdown["menu"].delete(0, "end")
            for theme in themes:
                self.theme_dropdown["menu"].add_command(
                    label=theme[1], command=lambda value=theme[1]: self.theme_var.set(value)
                )
        else:
            self.theme_var.set("Нет доступных тестов")

    def start_test(self):
        selected_theme = self.theme_var.get()
        theme_id = self.db.get_test_id(selected_theme)
        if selected_theme and theme_id:
            self.withdraw()
            TestForm(self, self.user_id, theme_id).mainloop()
        else:
            messagebox.showerror("Ошибка", "Выберите корректный тест.")

    def view_results(self):
        self.withdraw()
        ResultForm(self, self.user_id).mainloop()

    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.destroy()