import tkinter as tk
from tkinter import messagebox
from database import Database
import sqlite3

class RegisterForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Регистрация")
        self.geometry("300x300")
        self.db = Database()

        fields = [
            ("Имя пользователя", "username", None),
            ("Пароль", "password", "*"),
            ("Подтверждение пароля", "confirm", "*")
        ]
        self.entries = {}
        for label, name, show in fields:
            tk.Label(self, text=label).pack(pady=5)
            entry = tk.Entry(self, show=show) if show else tk.Entry(self)
            entry.pack(pady=5)
            self.entries[name] = entry

        tk.Button(self, text="Зарегистрироваться", command=self.register).pack(pady=5)

    def register(self):
        username = self.entries["username"].get()
        password = self.entries["password"].get()
        confirm = self.entries["confirm"].get()

        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают.")
            return

        try:
            self.db.cursor.execute(
                "INSERT INTO USERS (username, password, role) VALUES (?, ?, ?)",
                (username, self.db.hash_password(password), "student")
            )
            self.db.connection.commit()
            messagebox.showinfo("Успешно", "Вы успешно зарегистрировались.")
            self.destroy()
            from login_form import LoginForm
            LoginForm().mainloop()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такой пользователь уже существует.")
