import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from user_form import UserForm

class AddAdminDialog(simpledialog.Dialog):
    """Диалог для добавления существующего преподавателя в группу."""
    def __init__(self, parent, group_id, db):
        self.group_id = group_id
        self.db = db
        super().__init__(parent, "Добавить преподавателя в группу")

    def body(self, master):
        tk.Label(master, text="Выберите преподавателя для добавления:").pack()
        self.admins = [
            a for a in self.db.fetch_all("SELECT id, last_name, first_name, username FROM USERS WHERE role='admin' AND username!='admin'")
            if self.group_id not in {g['id'] for g in self.db.get_groups_by_admin(a['id'])}
        ]
        self.var = tk.StringVar()
        for admin in self.admins:
            label = f"{admin['last_name']} {admin['first_name']} ({admin['username']})"
            tk.Radiobutton(master, text=label, variable=self.var, value=str(admin['id'])).pack(anchor='w')
        return None

    def apply(self):
        self.result = int(self.var.get()) if self.var.get() else None

class GroupUsersForm(tk.Toplevel):
    def __init__(self, parent, group_id):
        super().__init__(parent)
        self.db = Database()
        self.group_id = group_id
        self.title(f"Пользователи группы {self.get_group_name()}")
        self.center_window(400, 650)
        self._create_widgets()
        self._load_group_users()

    def center_window(self, width=400, height=650):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def get_group_name(self):
        group = self.db._execute("SELECT name FROM GROUPS WHERE id=?", (self.group_id,), fetch=True)
        return group[0]["name"] if group else "?"

    def _create_widgets(self):
        # Преподаватели
        tk.Label(self, text="Преподаватели группы:", font=("Arial", 12, "bold")).pack(pady=2)
        self.admins_listbox = tk.Listbox(self)
        self.admins_listbox.pack(fill=tk.X, pady=2)
        adm_btn_frame = tk.Frame(self)
        adm_btn_frame.pack(pady=2)
        tk.Button(adm_btn_frame, text="Добавить преподавателя", command=self._add_admin).pack(side=tk.LEFT, padx=2)
        tk.Button(adm_btn_frame, text="Удалить преподавателя", command=self._remove_admin).pack(side=tk.LEFT, padx=2)
        # Студенты
        tk.Label(self, text="Студенты группы:", font=("Arial", 12, "bold")).pack(pady=2)
        self.students_listbox = tk.Listbox(self)
        self.students_listbox.pack(fill=tk.BOTH, expand=True, pady=2)
        stud_btn_frame = tk.Frame(self)
        stud_btn_frame.pack(pady=2)
        tk.Button(stud_btn_frame, text="Добавить студента", command=self._add_student).pack(side=tk.LEFT, padx=2)
        tk.Button(stud_btn_frame, text="Редактировать студента", command=self._edit_student).pack(side=tk.LEFT, padx=2)
        tk.Button(stud_btn_frame, text="Удалить студента", command=self._delete_student).pack(side=tk.LEFT, padx=2)
        tk.Button(self, text="Закрыть", command=self.destroy).pack(pady=7)

    def _load_group_users(self):
        self.admins_listbox.delete(0, tk.END)
        self.students_listbox.delete(0, tk.END)
        self.admin_ids = []
        self.student_ids = []

        admins = self.db.get_admins_by_group(self.group_id)

        for idx, admin in enumerate(admins, 1):
            label = f"{idx}. {admin['last_name']} {admin['first_name']} ({admin['username']})"
            print(f"DEBUG {idx=}, {label=}")
            self.admins_listbox.insert(tk.END, label)
            self.admin_ids.append(admin['id'])

        students = self.db.get_students_by_group(self.group_id)
        for idx, st in enumerate(students, 1):
            label = f"{idx}. {st['last_name']} {st['first_name']}"
            self.students_listbox.insert(tk.END, label)
            self.student_ids.append(st['id'])

    def _get_selected_admin_id(self):
        idx = self.admins_listbox.curselection()
        return self.admin_ids[idx[0]] if idx else None

    def _get_selected_student_id(self):
        idx = self.students_listbox.curselection()
        return self.student_ids[idx[0]] if idx else None

    def _add_admin(self):
        dlg = AddAdminDialog(self, self.group_id, self.db)
        if dlg.result:
            self.db.add_admin_to_group(dlg.result, self.group_id)
            self._load_group_users()

    def _remove_admin(self):
        admin_id = self._get_selected_admin_id()
        if not admin_id:
            messagebox.showerror("Ошибка", "Выберите преподавателя для удаления из группы.")
            return
        if messagebox.askyesno("Удалить преподавателя", "Удалить преподавателя из этой группы?"):
            self.db.remove_admin_from_group(admin_id, self.group_id)
            self._load_group_users()

    def _add_student(self):
        form = UserForm(self, "Добавить студента", group_id=self.group_id, role="student")
        self.wait_window(form)
        self._load_group_users()

    def _edit_student(self):
        student_id = self._get_selected_student_id()
        if not student_id:
            messagebox.showerror("Ошибка", "Выберите студента для редактирования.")
            return
        form = UserForm(self, "Редактировать студента", user_id=student_id, role="student")
        self.wait_window(form)
        self._load_group_users()

    def _delete_student(self):
        student_id = self._get_selected_student_id()
        if not student_id:
            messagebox.showerror("Ошибка", "Выберите студента для удаления.")
            return
        if messagebox.askyesno("Удалить студента", "Вы уверены, что хотите удалить этого студента?"):
            self.db.delete_user(student_id)
            self._load_group_users()