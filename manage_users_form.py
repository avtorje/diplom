import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from database import Database

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
        current_groups = set(g['id'] for g in self.db.get_groups_for_admin(self.admin_id))
        for i, group in enumerate(self.groups):
            var = tk.BooleanVar(value=group['id'] in current_groups)
            cb = tk.Checkbutton(master, text=group['name'], variable=var)
            cb.pack(anchor='w')
            self.varlist.append((var, group['id']))
        return None

    def apply(self):
        selected = [gid for var, gid in self.varlist if var.get()]
        current = set(g['id'] for g in self.db.get_groups_for_admin(self.admin_id))
        for gid in selected:
            if gid not in current:
                self.db.add_admin_to_group(self.admin_id, gid)
        for gid in current:
            if gid not in selected:
                self.db.remove_admin_from_group(self.admin_id, gid)

class AddUserDialog(simpledialog.Dialog):
    def body(self, master):
        self.result = None
        tk.Label(master, text="Имя:").grid(row=0, column=0, sticky="e")
        self.first_name_entry = tk.Entry(master)
        self.first_name_entry.grid(row=0, column=1)
        tk.Label(master, text="Фамилия:").grid(row=1, column=0, sticky="e")
        self.last_name_entry = tk.Entry(master)
        self.last_name_entry.grid(row=1, column=1)
        tk.Label(master, text="Логин:").grid(row=2, column=0, sticky="e")
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=2, column=1)
        tk.Label(master, text="Пароль:").grid(row=3, column=0, sticky="e")
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=3, column=1)
        return self.first_name_entry

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
        self.title("Управление пользователями")
        self.geometry("900x650")
        self.parent = parent
        self.center_window()  # Добавьте эту строку
        self.create_widgets()
        self.refresh_all()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 900
            height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Преподаватели
        frame_teachers = tk.LabelFrame(self, text="Преподаватели")
        frame_teachers.pack(fill=tk.X, padx=10, pady=5)
        self.teachers_listbox = tk.Listbox(frame_teachers, height=8)
        self.teachers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        btns = tk.Frame(frame_teachers)
        btns.pack(side=tk.RIGHT, padx=5)
        tk.Button(btns, text="Добавить", command=self.add_teacher).pack(fill=tk.X, pady=2)
        tk.Button(btns, text="Удалить", command=self.delete_teacher).pack(fill=tk.X, pady=2)
        tk.Button(btns, text="Назначить в группы", command=self.assign_teacher_to_groups).pack(fill=tk.X, pady=2)

        # Группы
        frame_groups = tk.LabelFrame(self, text="Группы")
        frame_groups.pack(fill=tk.X, padx=10, pady=5)
        self.groups_listbox = tk.Listbox(frame_groups, height=8, exportselection=False)
        self.groups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        btns_g = tk.Frame(frame_groups)
        btns_g.pack(side=tk.RIGHT, padx=5)
        tk.Button(btns_g, text="Добавить", command=self.add_group).pack(fill=tk.X, pady=2)
        tk.Button(btns_g, text="Удалить", command=self.delete_group).pack(fill=tk.X, pady=2)
        tk.Button(btns_g, text="Редактировать", command=self.edit_group).pack(fill=tk.X, pady=2)
        tk.Button(btns_g, text="Состав группы", command=self.view_group_members).pack(fill=tk.X, pady=2)

        # Студенты группы
        frame_students = tk.LabelFrame(self, text="Студенты группы")
        frame_students.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        self.students_listbox = tk.Listbox(frame_students, exportselection=False)
        self.students_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        btns_s = tk.Frame(frame_students)
        btns_s.pack(side=tk.RIGHT, padx=5)
        tk.Button(btns_s, text="Добавить", command=self.add_student).pack(fill=tk.X, pady=2)
        tk.Button(btns_s, text="Удалить", command=self.delete_student).pack(fill=tk.X, pady=2)
        tk.Button(btns_s, text="Импорт", command=self.import_students).pack(fill=tk.X, pady=2)

        # Назад
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=10)

        # Привязки
        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

    def refresh_all(self):
        self.load_teachers()
        self.load_groups()
        self.load_students()

    def load_teachers(self):
        self.teachers_listbox.delete(0, tk.END)
        self.teachers = self.db.fetch_all("SELECT id, last_name, first_name, username FROM USERS WHERE role='admin' AND username!='admin'")
        for idx, t in enumerate(self.teachers, 1):
            self.teachers_listbox.insert(tk.END, f"{idx}. {t['last_name']} {t['first_name']} ({t['username']})")

    def load_groups(self):
        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for i, group in enumerate(self.groups, 1):
            self.groups_listbox.insert(tk.END, f"{i}. {group['name']}")

    def load_students(self):
        self.students_listbox.delete(0, tk.END)
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            self.students = []
            return
        group_id = self.groups[idx[0]]['id']
        self.students = self.db.get_students_by_group(group_id)
        for i, s in enumerate(self.students, 1):
            self.students_listbox.insert(tk.END, f"{i}. {s['last_name']} {s['first_name']}")
    
    def on_group_select(self, event=None):
        self.load_students()

    def add_teacher(self):
        dlg = AddUserDialog(self)
        if dlg.result:
            d = dlg.result
            try:
                self.db.add_admin(d["username"], d["first_name"], d["last_name"], d["password"])
                self.load_teachers()
                messagebox.showinfo("Успешно", "Преподаватель добавлен.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_teacher(self):
        idx = self.teachers_listbox.curselection()
        if not idx:
            messagebox.showwarning("Внимание", "Выберите преподавателя для удаления.")
            return
        if idx[0] >= len(self.teachers):
            messagebox.showerror("Ошибка", "Некорректный выбор преподавателя.")
            return
        admin_id = self.teachers[idx[0]]["id"]
        if messagebox.askyesno("Удаление", "Удалить выбранного преподавателя?"):
            try:
                self.db.delete_user(admin_id)
                self.load_teachers()
                messagebox.showinfo("Успешно", "Преподаватель удалён.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def assign_teacher_to_groups(self):
        idx = self.teachers_listbox.curselection()
        if not idx:
            messagebox.showwarning("Внимание", "Выберите преподавателя.")
            return
        if idx[0] >= len(self.teachers):
            messagebox.showerror("Ошибка", "Некорректный выбор преподавателя.")
            return
        admin_id = self.teachers[idx[0]]["id"]
        AddAdminToGroupsDialog(self, admin_id, self.db)
        self.load_teachers()

    def add_group(self):
        name = simpledialog.askstring("Имя группы", "Введите название группы:", parent=self)
        code = simpledialog.askstring("Код группы", "Введите код группы:", parent=self)
        if name and code:
            try:
                self.db.add_group(name, code)
                self.load_groups()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def edit_group(self):
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Выберите группу для редактирования.")
            return
        group = self.groups[idx[0]]
        name = simpledialog.askstring("Имя группы", "Введите новое название группы:", initialvalue=group['name'], parent=self)
        code = simpledialog.askstring("Код группы", "Введите новый код группы:", initialvalue=group['access_code'], parent=self)
        if name and code:
            try:
                self.db.edit_group(group['id'], name, code)
                self.load_groups()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_group(self):
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Выберите группу для удаления.")
            return
        group_id = self.groups[idx[0]]['id']
        if messagebox.askyesno("Удалить группу", "Вы уверены?"):
            self.db.delete_group(group_id)
            self.load_groups()
            self.load_students()

    def view_group_members(self):
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Выберите группу для просмотра состава.")
            return
        group = self.groups[idx[0]]
        from group_users_form import GroupMembersForm
        GroupMembersForm(self, group['id'], group['name'], self.db)

    def add_student(self):
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Сначала выберите группу для добавления студента.")
            return
        from user_form import UserForm
        group_id = self.groups[idx[0]]['id']
        dlg = UserForm(self, "Добавить студента", group_id=group_id, role="student")
        self.load_students()

    def delete_student(self):
        idx = self.students_listbox.curselection()
        if not idx or idx[0] >= len(self.students):
            messagebox.showerror("Ошибка", "Выберите студента для удаления.")
            return
        student_id = self.students[idx[0]]["id"]
        if messagebox.askyesno("Удалить студента", "Вы уверены?"):
            self.db.delete_user(student_id)
            self.load_students()

    def import_students(self):
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Сначала выберите группу для импорта студентов.")
            return
        group_id = self.groups[idx[0]]['id']
        file_path = filedialog.askopenfilename(title="Выберите файл для импорта", filetypes=[("Текстовые файлы", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # Поддержка запятой и пробела в качестве разделителя
                        if "," in line:
                            parts = [p.strip() for p in line.split(",")]
                        else:
                            parts = line.split()
                        if len(parts) >= 2:
                            first_name, last_name = parts[0], parts[1]
                            self.db.add_student(first_name, last_name, group_id)
                self.load_students()
                messagebox.showinfo("Импорт завершён", "Студенты успешно импортированы.")
            except Exception as e:
                messagebox.showerror("Ошибка импорта", str(e))

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()