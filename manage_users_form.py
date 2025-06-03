import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from group_users_form import GroupUsersForm

class AddAdminToGroupsDialog(simpledialog.Dialog):
    """Диалог для назначения преподавателя в группы"""
    def __init__(self, parent, admin_id, db):
        self.admin_id = admin_id
        self.db = db
        super().__init__(parent, "Назначить преподавателя в группы")

    def body(self, master):
        tk.Label(master, text="Выберите группы для преподавателя:").pack()
        self.groups = self.db.get_groups()
        self.varlist = []
        current_groups = set(g['id'] for g in self.db.get_groups_by_admin(self.admin_id))
        for i, group in enumerate(self.groups):
            var = tk.BooleanVar(value=group['id'] in current_groups)
            cb = tk.Checkbutton(master, text=group['name'], variable=var)
            cb.pack(anchor='w')
            self.varlist.append((var, group['id']))
        return None

    def apply(self):
        selected = [gid for var, gid in self.varlist if var.get()]
        current = set(g['id'] for g in self.db.get_groups_by_admin(self.admin_id))
        for gid in selected:
            if gid not in current:
                self.db.add_admin_to_group(self.admin_id, gid)
        for gid in current:
            if gid not in selected:
                self.db.remove_admin_from_group(self.admin_id, gid)

class AddUserDialog(simpledialog.Dialog):
    def body(self, master):
        self.result = None
        tk.Label(master, text="Выберите роль:").grid(row=0, column=0, columnspan=2, pady=5)
        self.role_var = tk.StringVar(value="admin")
        tk.Radiobutton(master, text="Преподаватель", variable=self.role_var, value="admin", command=self.update_fields).grid(row=1, column=0)
        # Студентов добавляем только через форму группы!
        # tk.Radiobutton(master, text="Студент", variable=self.role_var, value="student", command=self.update_fields).grid(row=1, column=1)
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
        # В этой форме только преподаватели
        self.username_entry.config(state="normal")
        self.password_entry.config(state="normal")

    def validate(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not first_name or not last_name:
            messagebox.showerror("Ошибка", "Имя и фамилия обязательны.")
            return False
        if not username:
            messagebox.showerror("Ошибка", "Логин обязателен для преподавателя.")
            return False
        if not password:
            messagebox.showerror("Ошибка", "Пароль обязателен для преподавателя.")
            return False
        return True

    def apply(self):
        self.result = {
            "first_name": self.first_name_entry.get().strip(),
            "last_name": self.last_name_entry.get().strip(),
            "username": self.username_entry.get().strip(),
            "password": self.password_entry.get().strip(),
        }

class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление преподавателями")
        self.center_window(500, 500)
        self.parent = parent
        self.create_widgets()
        self.load_admins()

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
        tk.Label(self, text="Преподаватели", font=("Arial", 14)).pack(pady=5)
        self.admins_listbox = tk.Listbox(self)
        self.admins_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Добавить преподавателя", command=self.add_admin).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Назначить в группы", command=self.assign_admin_to_groups).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Управление группами", command=self.open_groups_form).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Назад", command=self.go_back).pack(pady=5, fill=tk.X)

    def load_admins(self):
        self.main_admin_listbox.delete(0, tk.END)
        main_admin = self.db.get_main_admin()
        if main_admin:
            self.main_admin_listbox.insert(
                tk.END, f"{main_admin['username']} (Главный админ)"
            )
        self.admins_listbox.delete(0, tk.END)
        admins = self.db.fetch_all("SELECT id, username, first_name, last_name FROM USERS WHERE role='admin' AND username!='admin'")
        for a in admins:
            self.admins_listbox.insert(
                tk.END, f"{a['id']}: {a['last_name']} {a['first_name']} ({a['username']})"
            )

    def add_admin(self):
        dlg = AddUserDialog(self)
        if dlg.result:
            d = dlg.result
            try:
                self.db.add_admin(d["username"], d["first_name"], d["last_name"], d["password"])
                self.load_admins()
                messagebox.showinfo("Успешно", "Преподаватель добавлен.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def assign_admin_to_groups(self):
        idx = self.admins_listbox.curselection()
        if not idx:
            messagebox.showwarning("Внимание", "Выберите преподавателя.")
            return
        admin_str = self.admins_listbox.get(idx[0])
        admin_id = int(admin_str.split(":")[0])
        AddAdminToGroupsDialog(self, admin_id, self.db)
        self.load_admins()

    def open_groups_form(self):
        from groups_form import GroupsForm
        form = GroupsForm(self)
        self.wait_window(form)
        self.load_admins()

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()