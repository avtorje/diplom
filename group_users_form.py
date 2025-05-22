import tkinter as tk
from tkinter import messagebox
from database import Database
from user_form import UserForm

class GroupUsersForm(tk.Toplevel):
    def __init__(self, parent, group_id):
        super().__init__(parent)
        self.db = Database()
        self.group_id = group_id
        self.title(f"Пользователи группы {self.get_group_name()}")
        self.geometry("350x400")
        self.create_widgets()
        self.load_group_users()

    def get_group_name(self):
        group = self.db._execute("SELECT name FROM GROUPS WHERE id=?", (self.group_id,), fetch=True)
        return group[0][0] if group else "?"

    def create_widgets(self):
        tk.Label(self, text="Администраторы группы:", font=("Arial", 12, "bold")).pack(pady=2)
        self.admins_listbox = tk.Listbox(self)
        self.admins_listbox.pack(fill=tk.X, pady=2)

        tk.Label(self, text="Студенты группы:", font=("Arial", 12, "bold")).pack(pady=2)
        self.students_listbox = tk.Listbox(self)
        self.students_listbox.pack(fill=tk.BOTH, expand=True, pady=2)

        tk.Button(self, text="Добавить пользователя", command=self.add_user).pack(pady=5)
        tk.Button(self, text="Редактировать пользователя", command=self.edit_user).pack(pady=2)
        tk.Button(self, text="Удалить пользователя", command=self.delete_user).pack(pady=2)
        tk.Button(self, text="Закрыть", command=self.destroy).pack(pady=5)

    def load_group_users(self):
        self.admins_listbox.delete(0, tk.END)
        self.students_listbox.delete(0, tk.END)
        admins = self.db.get_admins_by_group(self.group_id)
        self.admin_ids = []
        for idx, admin in enumerate(admins, start=1):
            self.admins_listbox.insert(tk.END, f"{idx}. {admin[1]}")
            self.admin_ids.append(admin[0])
        students = self.db.get_students_by_group(self.group_id)
        self.student_ids = []
        for idx, student in enumerate(students, start=1):
            self.students_listbox.insert(tk.END, f"{idx}. {student[1]}")
            self.student_ids.append(student[0])

    def add_user(self):
        UserForm(self, "Добавить пользователя", group_id=self.group_id)
        self.wait_window()
        self.load_group_users()

    def edit_user(self):
        idx = self.admins_listbox.curselection()
        if idx:
            user_id = self.admin_ids[idx[0]]
        else:
            idx = self.students_listbox.curselection()
            if not idx:
                messagebox.showerror("Ошибка", "Выберите пользователя для редактирования.")
                return
            user_id = self.student_ids[idx[0]]
        UserForm(self, "Редактировать пользователя", user_id=user_id)
        self.wait_window()
        self.load_group_users()

    def delete_user(self):
        idx = self.admins_listbox.curselection()
        if idx:
            user_id = self.admin_ids[idx[0]]
        else:
            idx = self.students_listbox.curselection()
            if not idx:
                messagebox.showerror("Ошибка", "Выберите пользователя для удаления.")
                return
            user_id = self.student_ids[idx[0]]
        if messagebox.askyesno("Удалить пользователя", "Вы уверены, что хотите удалить этого пользователя?"):
            self.db.delete_user(user_id)
            self.load_group_users()