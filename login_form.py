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
        self._create_labeled_entry(self.admin_tab, "Имя пользователя", "username_entry")
        self._create_labeled_entry(self.admin_tab, "Пароль", "password_entry", show="*")
        tk.Button(self.admin_tab, text="Войти", command=self.login).pack(pady=5)

        # --- Студенческая форма ---
        self._create_labeled_combobox(self.student_tab, "Выберите группу", "group_combobox", self.on_group_selected)
        self._create_labeled_combobox(self.student_tab, "Выберите имя", "student_combobox")
        self._create_labeled_entry(self.student_tab, "Код группы", "group_code_entry", show="*")
        tk.Button(self.student_tab, text="Войти", command=self.student_login).pack(pady=10)

        self.load_groups()

    def _create_labeled_entry(self, parent, label, attr, **kwargs):
        tk.Label(parent, text=label).pack(pady=5)
        entry = tk.Entry(parent, **kwargs)
        entry.pack(pady=5)
        setattr(self, attr, entry)

    def _create_labeled_combobox(self, parent, label, attr, bind_func=None):
        tk.Label(parent, text=label).pack(pady=5)
        cb = ttk.Combobox(parent, state="readonly")
        cb.pack(pady=5)
        if bind_func:
            cb.bind("<<ComboboxSelected>>", bind_func)
        setattr(self, attr, cb)

    def load_groups(self):
        groups = self.db.get_groups()
        self.group_combobox['values'] = [g['name'] for g in groups]

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.db.validate_user(username, password)
        if user:
            self._open_form(user)
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

    def student_login(self):
        group_name = self.group_combobox.get()
        student_fullname = self.student_combobox.get()
        group_code = self.group_code_entry.get()
        group = self.db.get_group_by_name(group_name)
        if not group or group['access_code'] != group_code:
            messagebox.showerror("Ошибка", "Неверный код группы!")
            return
        try:
            first_name, last_name = student_fullname.strip().split(' ', 1)
        except ValueError:
            messagebox.showerror("Ошибка", "Выберите имя и фамилию из списка!")
            return
        user = self.db.get_user_by_fullname_and_group(first_name, last_name, group['id'])
        if not user:
            messagebox.showerror("Ошибка", "Студент не найден!")
            return
        self._open_form(user, student=True)

    def _open_form(self, user, student=False):
        if not student and user["role"] == "admin":
            messagebox.showinfo("Успешно", "Добро пожаловать, администратор!")
            self.destroy()
            from admin_form import AdminForm
            AdminForm(user["id"]).mainloop()
        else:
            messagebox.showinfo("Вход выполнен", f"Добро пожаловать, {user['first_name']} {user['last_name']}!")
            self.destroy()
            import tkinter as tk
            from student_form import StudentForm
            root = tk.Tk()
            root.withdraw()  # Скрываем главное окно
            StudentForm(user["id"])
            root.mainloop()

    def on_group_selected(self, event):
        group_name = self.group_combobox.get()
        group = self.db.get_group_by_name(group_name)
        if group:
            students = self.db.get_students_by_group(group['id'])
            self.student_combobox['values'] = [
                f"{s['first_name']} {s['last_name']}" for s in students
            ]
            self.student_combobox.set('')

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")