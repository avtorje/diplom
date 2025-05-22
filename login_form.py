import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from admin_form import AdminForm
from student_form import StudentForm

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вход")
        self.geometry("350x320")
        self.center_window()

        self.db = Database()

        tab_control = ttk.Notebook(self)
        self.admin_tab = tk.Frame(tab_control)
        self.student_tab = tk.Frame(tab_control)
        tab_control.add(self.admin_tab, text='Администратор')
        tab_control.add(self.student_tab, text='Студент')
        tab_control.pack(expand=1, fill="both")

        # --- Админ форма ---
        tk.Label(self.admin_tab, text="Имя пользователя").pack(pady=5)
        self.username_entry = tk.Entry(self.admin_tab)
        self.username_entry.pack(pady=5)

        tk.Label(self.admin_tab, text="Пароль").pack(pady=5)
        self.password_entry = tk.Entry(self.admin_tab, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.admin_tab, text="Войти", command=self.login).pack(pady=5)
        tk.Button(self.admin_tab, text="Регистрация", command=self.open_register_form).pack(pady=5)

        # --- Студенческая форма ---
        tk.Label(self.student_tab, text="Выберите группу").pack(pady=5)
        self.group_combobox = ttk.Combobox(self.student_tab, state="readonly")
        self.group_combobox.pack(pady=5)
        self.group_combobox.bind("<<ComboboxSelected>>", self.on_group_selected)

        tk.Label(self.student_tab, text="Выберите имя").pack(pady=5)
        self.student_combobox = ttk.Combobox(self.student_tab, state="readonly")
        self.student_combobox.pack(pady=5)

        tk.Label(self.student_tab, text="Код группы").pack(pady=5)
        self.group_code_entry = tk.Entry(self.student_tab, show="*")
        self.group_code_entry.pack(pady=5)

        tk.Button(self.student_tab, text="Войти", command=self.student_login).pack(pady=10)

        self.load_groups()

    def load_groups(self):
        groups = self.db.get_groups()
        self.group_combobox['values'] = [g[1] for g in groups]

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.db.validate_user(username, password)
        if user:
            role = user[3]
            if role == "admin":
                messagebox.showinfo("Успешно", "Добро пожаловать, администратор!")
                self.destroy()
                AdminForm(user[0]).mainloop()
            else:
                messagebox.showinfo("Успешно", "Добро пожаловать, студент!")
                self.destroy()
                StudentForm(user[0], user[1]).mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

    def student_login(self):
        group_name = self.group_combobox.get()
        student_name = self.student_combobox.get()
        group_code = self.group_code_entry.get()

        group = self.db.get_group_by_name(group_name)
        if not group or group['access_code'] != group_code:
            messagebox.showerror("Ошибка", "Неверный код группы!")
            return

        user = self.db.get_user_by_name_and_group(student_name, group['id'])
        if not user:
            messagebox.showerror("Ошибка", "Студент не найден!")
            return

        messagebox.showinfo("Вход выполнен", f"Добро пожаловать, {student_name}!")
        self.destroy()
        StudentForm(user[0], user[1]).mainloop()

    def on_group_selected(self, event):
        group_name = self.group_combobox.get()
        group = self.db.get_group_by_name(group_name)
        if group:
            students = self.db.get_students_by_group(group['id'])
            self.student_combobox['values'] = [s[1] for s in students]
            self.student_combobox.set('')

    def open_register_form(self):
        self.destroy()
        from register_form import RegisterForm
        RegisterForm().mainloop()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")