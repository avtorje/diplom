import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class UserForm(tk.Toplevel):
    def __init__(self, parent, title, user_id=None, group_id=None):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.forced_group_id = group_id
        self.title(title)
        self.geometry("400x400")
        self.groups = self.db.get_groups()
        self.parent = parent
        self.create_widgets()
        if user_id:
            self.load_user()

    def create_widgets(self):
        tk.Label(self, text="Имя пользователя:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Роль:").pack()
        self.role_combobox = ttk.Combobox(self, values=["student", "admin"], state="readonly")
        self.role_combobox.pack()
        self.role_combobox.bind("<<ComboboxSelected>>", self.role_changed)

        tk.Label(self, text="Группа:").pack()
        group_names = [g[1] for g in self.groups]
        self.group_combobox = ttk.Combobox(self, values=group_names, state="readonly")
        self.group_combobox.pack()
        if self.forced_group_id:
            self.group_combobox.set(self.get_group_name(self.forced_group_id))
            self.group_combobox["state"] = "disabled"

        self.password_label = tk.Label(self, text="Пароль:")
        self.password_entry = tk.Entry(self, show="*")

        tk.Button(self, text="Сохранить", command=self.save_user).pack(pady=10)
        self.role_changed()

    def get_group_name(self, group_id):
        return next((g[1] for g in self.groups if g[0] == group_id), "")

    def role_changed(self, event=None):
        if self.role_combobox.get() == "admin":
            self.password_label.pack()
            self.password_entry.pack()
        else:
            self.password_label.pack_forget()
            self.password_entry.pack_forget()

    def save_user(self):
        username = self.username_entry.get()
        role = self.role_combobox.get()
        group_id = self.forced_group_id or next((g[0] for g in self.groups if g[1] == self.group_combobox.get()), None)

        if not username or not role:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        password = self.password_entry.get() if role == "admin" else None
        if role == "admin" and not password:
            messagebox.showerror("Ошибка", "Пароль обязателен для администратора")
            return

        if self.user_id:
            user = self.db.get_user_by_id(self.user_id)
            if user and user[1] == "admin" and user[2] == "admin":
                messagebox.showerror("Ошибка", "Главного администратора нельзя редактировать")
                return
            self.db.update_user(self.user_id, username, password, role, group_id)
        else:
            self.db.add_user(username, password, role, group_id)
        self.destroy()

    def load_user(self):
        user = self.db.get_user_by_id(self.user_id)
        if user:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, user[1])
            self.role_combobox.set(user[2])
            for i, g in enumerate(self.groups):
                if g[0] == user[3]:
                    self.group_combobox.current(i)
                    break
            if user[2] == "admin":
                self.password_label.pack()
                self.password_entry.pack()
