import tkinter as tk
from tkinter import messagebox
from manage_tests_form import ManageTestsForm
from manage_users_form import ManageUsersForm
from statistics_form import StatisticsForm


class AdminForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Панель администратора")
        self.geometry("400x300")
        self.center_window()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Панель администратора", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Управление тестами", command=self.open_manage_tests).pack(pady=5)
        tk.Button(self, text="Управление пользователями", command=self.open_manage_users).pack(pady=5)
        tk.Button(self, text="Просмотр статистики", command=self.open_statistics).pack(pady=5)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=5)
        tk.Button(self, text="Выход", command=self.exit_app).pack(pady=5)

    def open_manage_tests(self):
        self.withdraw()  # Скрыть текущее окно
        ManageTestsForm(self).mainloop()

    def open_manage_users(self):
        self.withdraw()  # Скрыть текущее окно
        ManageUsersForm(self).mainloop()

    def open_statistics(self):
        self.withdraw()  # Скрыть текущее окно
        StatisticsForm(self).mainloop()

    def go_back(self):
        if messagebox.askyesno("Вернуться", "Вы уверены, что хотите вернуться в меню регистрации?"):
            self.destroy()
            from login_form import LoginForm
            LoginForm().mainloop()

    def exit_app(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.destroy()

    def center_window(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")