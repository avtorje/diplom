import tkinter as tk
from tkinter import messagebox
from database import Database
from groups_form import GroupsForm
from user_form import UserForm

class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление пользователями")
        self.geometry("500x500")
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
        tk.Button(self, text="Управление группами", command=self.open_groups_form).pack(pady=5)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=5)

    def open_groups_form(self):
        GroupsForm(self)
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1:
            width = 600
            height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_users(self):
        self.users_listbox.delete(0, tk.END)
        users = self.db.get_all_users()
        self.user_ids = []  # Сохраняем id пользователей в том же порядке, как и в списке
        for idx, user in enumerate(users, start=1):
            self.users_listbox.insert(tk.END, f"{idx}. {user[1]} ({user[3]})")
            self.user_ids.append(user[0])  # user[0] — настоящий id

    def add_user(self):
        new_user_window = UserForm(self, "Добавить пользователя")
        self.wait_window(new_user_window)
        self.load_users()

    def edit_user(self):
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для редактирования.")
            return

        user_id = self.user_ids[selected[0]]  # Получаем настоящий id
        edit_user_window = UserForm(self, "Редактировать пользователя", user_id)
        self.wait_window(edit_user_window)
        self.load_users()

    def delete_user(self):
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления.")
            return

        user_id = self.user_ids[selected[0]]  # Получаем настоящий id
        if messagebox.askyesno("Удалить пользователя", "Вы уверены, что хотите удалить этого пользователя?"):
            self.db.delete_user(user_id)
            self.load_users()

    def go_back(self):
        self.destroy()
        self.parent.deiconify()