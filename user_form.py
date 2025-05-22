import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class UserForm(tk.Toplevel):
    def __init__(self, parent, title, user_id=None, group_id=None):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.forced_group_id = group_id  # если создаём пользователя из группы — нельзя выбрать другую группу
        self.title(title)
        self.geometry("400x400")
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
        self.groups = self.db.get_groups()
        group_names = [g[1] for g in self.groups]
        self.group_combobox = ttk.Combobox(self, values=group_names, state="readonly")
        self.group_combobox.pack()
        if self.forced_group_id:  # если создаём из группы — выбор группы заблокирован
            self.group_combobox.set(self.get_group_name_by_id(self.forced_group_id))
            self.group_combobox["state"] = "disabled"

        self.password_label = tk.Label(self, text="Пароль:")
        self.password_entry = tk.Entry(self, show="*")

        tk.Button(self, text="Сохранить", command=self.save_user).pack(pady=10)
        self.role_changed()

    def get_group_name_by_id(self, group_id):
        for g in self.groups:
            if g[0] == group_id:
                return g[1]
        return ""

    def role_changed(self, event=None):
        if self.role_combobox.get() == "admin":
            if not self.password_label.winfo_ismapped():
                self.password_label.pack()
                self.password_entry.pack()
        else:
            if self.password_label.winfo_ismapped():
                self.password_label.pack_forget()
                self.password_entry.pack_forget()

    def save_user(self):
        username = self.username_entry.get()
        role = self.role_combobox.get()
        if self.forced_group_id:
            group_id = self.forced_group_id
        else:
            group_name = self.group_combobox.get()
            group_id = next((g[0] for g in self.groups if g[1] == group_name), None)

        if not username or not role:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        if role == "admin":
            password = self.password_entry.get()
            if not password:
                messagebox.showerror("Ошибка", "Пароль обязателен для администратора")
                return
        else:
            password = None

        # Не даём редактировать главного админа
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
            self.username_entry.insert(0, user[1])  # username
            self.role_combobox.set(user[2])         # role
            for i, g in enumerate(self.groups):
                if g[0] == user[3]:
                    self.group_combobox.current(i)
                    break
            if user[2] == "admin":
                self.password_label.pack()
                self.password_entry.pack()