import tkinter as tk
from tkinter import messagebox
from database import Database
from admin_form import AdminForm
from student_form import StudentForm


class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вход")
        self.geometry("300x200")
        self.center_window()

        self.db = Database()

        # UI компоненты
        tk.Label(self, text="Имя пользователя").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Пароль").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Войти", command=self.login).pack(pady=5)
        tk.Button(self, text="Регистрация", command=self.open_register_form).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.db.validate_user(username, password)
        if user:
            role = user[3]
            if role == "admin":
                messagebox.showinfo("Успешно", "Добро пожаловать, администратор!")
                self.destroy()
                AdminForm().mainloop()
            else:
                messagebox.showinfo("Успешно", "Добро пожаловать, студент!")
                self.destroy()
                StudentForm(user[0], user[1]).mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

    def open_register_form(self):
        self.destroy()
        from register_form import RegisterForm
        RegisterForm().mainloop()

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