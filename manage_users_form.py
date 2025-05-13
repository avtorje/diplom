import tkinter as tk
from tkinter import messagebox
from database import Database


class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление пользователями")
        self.geometry("400x400")
        self.parent = parent
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        tk.Label(self, text="Управление пользователями", font=("Arial", 16)).pack(pady=10)

        self.users_listbox = tk.Listbox(self)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Button(self, text="Добавить пользователя", command=self.add_user).pack(pady=5)
        tk.Button(self, text="Редактировать пользователя", command=self.edit_user).pack(pady=5)
        tk.Button(self, text="Удалить пользователя", command=self.delete_user).pack(pady=5)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=5)

    def load_users(self):
        self.users_listbox.delete(0, tk.END)
        users = self.db.get_all_users()
        for user in users:
            self.users_listbox.insert(tk.END, f"{user[0]}: {user[1]} ({user[3]})")

    def add_user(self):
        new_user_window = UserForm(self, "Добавить пользователя")
        self.wait_window(new_user_window)
        self.load_users()

    def edit_user(self):
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для редактирования.")
            return

        user_id = int(self.users_listbox.get(selected[0]).split(":")[0])
        edit_user_window = UserForm(self, "Редактировать пользователя", user_id)
        self.wait_window(edit_user_window)
        self.load_users()

    def delete_user(self):
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления.")
            return

        user_id = int(self.users_listbox.get(selected[0]).split(":")[0])
        if messagebox.askyesno("Удалить пользователя", "Вы уверены, что хотите удалить этого пользователя?"):
            self.db.delete_user(user_id)
            self.load_users()

    def go_back(self):
        self.destroy()
        self.parent.deiconify()