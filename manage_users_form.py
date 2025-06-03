import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from group_users_form import GroupUsersForm

class AddUserDialog(simpledialog.Dialog):
    def body(self, master):
        self.result = None

        tk.Label(master, text="Выберите роль:").grid(row=0, column=0, columnspan=2, pady=5)
        self.role_var = tk.StringVar(value="student")
        tk.Radiobutton(master, text="Студент", variable=self.role_var, value="student", command=self.update_fields).grid(row=1, column=0)
        tk.Radiobutton(master, text="Преподаватель", variable=self.role_var, value="admin", command=self.update_fields).grid(row=1, column=1)

        tk.Label(master, text="Имя:").grid(row=2, column=0, sticky="e")
        self.first_name_entry = tk.Entry(master)
        self.first_name_entry.grid(row=2, column=1)

        tk.Label(master, text="Фамилия:").grid(row=3, column=0, sticky="e")
        self.last_name_entry = tk.Entry(master)
        self.last_name_entry.grid(row=3, column=1)

        tk.Label(master, text="Логин:").grid(row=4, column=0, sticky="e")
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=4, column=1)

        tk.Label(master, text="Пароль:").grid(row=5, column=0, sticky="e")
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=5, column=1)

        self.update_fields()
        return self.first_name_entry

    def update_fields(self):
        role = self.role_var.get()
        if role == "student":
            self.username_entry.config(state="disabled")
            self.password_entry.config(state="disabled")
        else:
            self.username_entry.config(state="normal")
            self.password_entry.config(state="normal")

    def validate(self):
        role = self.role_var.get()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not first_name or not last_name:
            messagebox.showerror("Ошибка", "Имя и фамилия обязательны.")
            return False
        if role == "admin":
            if not username:
                messagebox.showerror("Ошибка", "Логин обязателен для преподавателя.")
                return False
            if not password:
                messagebox.showerror("Ошибка", "Пароль обязателен для преподавателя.")
                return False
        return True

    def apply(self):
        role = self.role_var.get()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        self.result = {
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "username": username if role == "admin" else None,
            "password": password if role == "admin" else None,
        }

class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление пользователями")
        self.center_window(500, 500)
        self.parent = parent
        self.create_widgets()
        self.load_users()

    def center_window(self, width=500, height=500):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        tk.Label(self, text="Главный администратор", font=("Arial", 14, "bold")).pack(pady=5)
        self.main_admin_listbox = tk.Listbox(self, height=1)
        self.main_admin_listbox.pack(fill=tk.X, pady=2)

        tk.Label(self, text="Управление по группам", font=("Arial", 14)).pack(pady=5)
        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.groups_listbox.bind("<Double-Button-1>", self.on_group_double_click)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Добавить пользователя", command=self.add_user).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Управление группами", command=self.open_groups_form).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Назад", command=self.go_back).pack(pady=5, fill=tk.X)

    def load_users(self):
        self.main_admin_listbox.delete(0, tk.END)
        main_admin = self.db.get_main_admin()
        if main_admin:
            self.main_admin_listbox.insert(tk.END, f"{main_admin['username']} (Главный админ)")

        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for i, group in enumerate(self.groups, 1):
            self.groups_listbox.insert(tk.END, f"{i}. {group['name']}")

    def on_group_double_click(self, event):
        idx = self.groups_listbox.nearest(event.y)
        if idx < 0 or idx >= len(self.groups):
            return
        self.groups_listbox.selection_clear(0, tk.END)
        self.groups_listbox.selection_set(idx)
        group_id = self.groups[idx]['id']
        GroupUsersForm(self, group_id)

    def open_groups_form(self):
        from groups_form import GroupsForm
        form = GroupsForm(self)
        self.wait_window(form)
        self.load_users()

    def add_user(self):
        dlg = AddUserDialog(self)
        if dlg.result:
            data = dlg.result
            try:
                if data["role"] == "student":
                    self.db.add_student(data["first_name"], data["last_name"])
                else:
                    self.db.add_admin(data["username"], data["first_name"], data["last_name"], data["password"])
                self.load_users()
                messagebox.showinfo("Успешно", "Пользователь добавлен.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()