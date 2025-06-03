import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class UserForm(tk.Toplevel):
    def __init__(self, parent, title, user_id=None, group_id=None, role="student"):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.forced_group_id = group_id
        self.role = role
        self.groups = self.db.get_groups()
        self.title(title)
        self.center_window(400, 300)
        self.parent = parent
        self.create_widgets()
        if user_id:
            self.load_user()

    def center_window(self, width=400, height=300):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        tk.Label(self, text="Имя:").pack()
        self.first_name_entry = tk.Entry(self)
        self.first_name_entry.pack()

        tk.Label(self, text="Фамилия:").pack()
        self.last_name_entry = tk.Entry(self)
        self.last_name_entry.pack()

        tk.Label(self, text="Группа:").pack()
        group_names = [g['name'] for g in self.groups]
        self.group_combobox = ttk.Combobox(self, values=group_names, state="readonly")
        self.group_combobox.pack()
        if self.forced_group_id:
            self.group_combobox.set(self.get_group_name(self.forced_group_id))
            self.group_combobox["state"] = "disabled"

        tk.Button(self, text="Сохранить", command=self.save_user).pack(pady=10)

    def get_group_name(self, group_id):
        return next((g['name'] for g in self.groups if g['id'] == group_id), "")

    def save_user(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        group_id = self.forced_group_id or next((g['id'] for g in self.groups if g['name'] == self.group_combobox.get()), None)

        if not first_name or not last_name or not group_id:
            messagebox.showerror("Ошибка", "Заполните все поля.")
            return

        if self.user_id:
            self.db.update_user(self.user_id, None, None, "student", group_id, first_name, last_name)
        else:
            self.db.add_student(first_name, last_name, group_id)
        self.destroy()

    def load_user(self):
        user = self.db.get_user_by_id(self.user_id)
        if user:
            self.first_name_entry.delete(0, tk.END)
            self.first_name_entry.insert(0, user['first_name'] or "")
            self.last_name_entry.delete(0, tk.END)
            self.last_name_entry.insert(0, user['last_name'] or "")
            for i, g in enumerate(self.groups):
                if g['id'] == user['group_id']:
                    self.group_combobox.current(i)
                    break