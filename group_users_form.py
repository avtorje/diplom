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
        self.center_window(350, 650)
        self._create_widgets()
        self._load_group_users()

    def center_window(self, width=350, height=650):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def get_group_name(self):
        group = self.db._execute("SELECT name FROM GROUPS WHERE id=?", (self.group_id,), fetch=True)
        # group[0][0] => group[0]["name"] (если row_factory=sqlite3.Row)
        return group[0]["name"] if group else "?"

    def _create_widgets(self):
        for label, attr in [("Администраторы группы:", "admins_listbox"), ("Студенты группы:", "students_listbox")]:
            tk.Label(self, text=label, font=("Arial", 12, "bold")).pack(pady=2)
            lb = tk.Listbox(self)
            lb.pack(fill=tk.BOTH if "students" in attr else tk.X, expand="students" in attr, pady=2)
            setattr(self, attr, lb)
        for text, cmd in [
            ("Добавить пользователя", self._add_user),
            ("Редактировать пользователя", self._edit_user),
            ("Удалить пользователя", self._delete_user),
            ("Закрыть", self.destroy)
        ]:
            tk.Button(self, text=text, command=cmd).pack(pady=2 if text != "Закрыть" else 5)

    def _load_group_users(self):
        if not self.winfo_exists():
            return
        if not self.admins_listbox.winfo_exists() or not self.students_listbox.winfo_exists():
            return
        if not getattr(self, 'admins_listbox', None) or not getattr(self, 'students_listbox', None):
            return
        if not self.admins_listbox.winfo_exists() or not self.students_listbox.winfo_exists():
            return

        self.admins_listbox.delete(0, tk.END)
        self.students_listbox.delete(0, tk.END)

        for lb, getter, id_attr in [
            (self.admins_listbox, self.db.get_admins_by_group, "admin_ids"),
            (self.students_listbox, self.db.get_students_by_group, "student_ids")
        ]:
            lb.delete(0, tk.END)
            users = getter(self.group_id)
            ids = []
            for idx, user in enumerate(users, 1):
                # user[1] -> user["username"], user[0] -> user["id"]
                lb.insert(tk.END, f"{idx}. {user['username']}")
                ids.append(user["id"])
            setattr(self, id_attr, ids)

    def _get_selected_user_id(self):
        for lb, ids in [(self.admins_listbox, self.admin_ids), (self.students_listbox, self.student_ids)]:
            idx = lb.curselection()
            if idx:
                return ids[idx[0]]
        return None

    def _add_user(self):
        form = UserForm(self, "Добавить пользователя", group_id=self.group_id)
        self.wait_window(form)
        self._load_group_users()

    def _edit_user(self):
        user_id = self._get_selected_user_id()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя для редактирования.")
            return
        form = UserForm(self, "Редактировать пользователя", user_id=user_id)
        self.wait_window(form)
        self._load_group_users()

    def _delete_user(self):
        user_id = self._get_selected_user_id()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления.")
            return
        if messagebox.askyesno("Удалить пользователя", "Вы уверены, что хотите удалить этого пользователя?"):
            self.db.delete_user(user_id)
            self._load_group_users()