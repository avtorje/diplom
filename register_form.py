import tkinter as tk
from tkinter import messagebox
from database import Database


class RegisterForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Регистрация")
        self.geometry("300x300")

        self.db = Database()

        # UI компоненты
        tk.Label(self, text="Имя пользователя").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Пароль").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self, text="Подтверждение пароля").pack(pady=5)
        self.confirm_password_entry = tk.Entry(self, show="*")
        self.confirm_password_entry.pack(pady=5)

        tk.Button(self, text="Зарегистрироваться", command=self.register).pack(pady=5)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
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