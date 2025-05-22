import tkinter as tk
from tkinter import messagebox
from database import Database
from groups_form import GroupsForm
from user_form import UserForm
from group_users_form import GroupUsersForm

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
        # Главный администратор отображается отдельно
        tk.Label(self, text="Главный администратор", font=("Arial", 14, "bold")).pack(pady=5)
        self.main_admin_listbox = tk.Listbox(self, height=1)
        self.main_admin_listbox.pack(fill=tk.X, pady=2)

        tk.Label(self, text="Управление по группам", font=("Arial", 14)).pack(pady=5)
        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

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
        # Главный админ
        self.main_admin_listbox.delete(0, tk.END)
        main_admin = self.db.get_main_admin()
        if main_admin:
            self.main_admin_listbox.insert(tk.END, f"{main_admin[1]} (Главный админ)")

        # Группы
        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for group in self.groups:
            self.groups_listbox.insert(tk.END, f"{group[0]}: {group[1]}")
        # Автоматически показать пользователей первой группы
        if self.groups:
            self.groups_listbox.select_set(0)
            self.on_group_select(None)

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

    def on_group_select(self, event):
        selection = self.groups_listbox.curselection()
        if not selection:
            return
        group_id = self.groups[selection[0]][0]
        GroupUsersForm(self, group_id)
        
    def open_groups_form(self):
        GroupsForm(self)

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()