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
        # Формирование списка групп с чекбоксами
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
        # Сохраняет изменения в назначении групп преподавателю
        selected = [gid for var, gid in self.varlist if var.get()]
        current = set(g['id'] for g in self.db.get_groups_for_admin(self.admin_id))
        for gid in selected:
            if gid not in current:
                self.db.add_admin_to_group(self.admin_id, gid)
        for gid in current:
            if gid not in selected:
                self.db.remove_admin_from_group(self.admin_id, gid)

class AddUserDialog(simpledialog.Dialog):
    """Диалог для добавления преподавателя"""
    def body(self, master):
        # Формирование полей для ввода данных преподавателя
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
        # Проверка корректности введённых данных
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
        # Сохраняет введённые данные
        self.result = {
            "first_name": self.first_name_entry.get().strip(),
            "last_name": self.last_name_entry.get().strip(),
            "username": self.username_entry.get().strip(),
            "password": self.password_entry.get().strip(),
        }
# --- Главное окно ---
class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent, current_user_id):
        super().__init__(parent)
        self.db = Database()
        self.current_user_id = current_user_id
        self.title("Управление пользователями")
        self.geometry("900x650")
        self.parent = parent
        self.center_window()
        self.is_main_admin = self._is_main_admin()
        self.create_widgets()
        self.refresh_all()

    # --- Вспомогательные методы ---
    def _is_main_admin(self):
        # Проверяет, является ли пользователь главным администратором
        user = self.db.get_user_by_id(self.current_user_id)
        return user and user["role"] == "admin" and user["username"] == "admin"

    def center_window(self):
        # Центрирует окно на экране
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 900
            height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # --- Создание интерфейса ---
    def create_widgets(self):
        # Формирует все элементы интерфейса окна

        frame_teachers = tk.LabelFrame(self, text="Преподаватели")
        frame_teachers.pack(fill=tk.X, padx=10, pady=5)
        self.teachers_listbox = tk.Listbox(frame_teachers, height=8)
        self.teachers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        btns = tk.Frame(frame_teachers)
        btns.pack(side=tk.RIGHT, padx=5)
        self.btn_add_teacher = tk.Button(btns, text="Добавить", command=self.add_teacher)
        self.btn_add_teacher.pack(fill=tk.X, pady=2)
        self.btn_delete_teacher = tk.Button(btns, text="Удалить", command=self.delete_teacher)
        self.btn_delete_teacher.pack(fill=tk.X, pady=2)
        self.btn_assign_teacher = tk.Button(btns, text="Назначить в группы", command=self.assign_teacher_to_groups)
        self.btn_assign_teacher.pack(fill=tk.X, pady=2)

        # Отключение кнопок для преподавателей, если не главный админ
        if not self.is_main_admin:
            self.btn_add_teacher.config(state="disabled")
            self.btn_delete_teacher.config(state="disabled")
            self.btn_assign_teacher.config(state="disabled")

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

        frame_students = tk.LabelFrame(self, text="Студенты группы")
        frame_students.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        self.students_listbox = tk.Listbox(frame_students, exportselection=False)
        self.students_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        btns_s = tk.Frame(frame_students)
        btns_s.pack(side=tk.RIGHT, padx=5)
        tk.Button(btns_s, text="Добавить", command=self.add_student).pack(fill=tk.X, pady=2)
        tk.Button(btns_s, text="Удалить", command=self.delete_student).pack(fill=tk.X, pady=2)
        tk.Button(btns_s, text="Импорт", command=self.import_students).pack(fill=tk.X, pady=2)

        tk.Button(self, text="Назад", command=self.go_back).pack(pady=10)

        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

    # --- Загрузка и обновление данных ---
    def refresh_all(self):
        # Обновляет все списки на форме
        self.load_teachers()
        self.load_groups()
        self.load_students()

    def load_teachers(self):
        # Загружает список преподавателей
        self.teachers_listbox.delete(0, tk.END)
        self.teachers = self.db.fetch_all("SELECT id, last_name, first_name, username FROM USERS WHERE role='admin' AND username!='admin'")
        for idx, t in enumerate(self.teachers, 1):
            self.teachers_listbox.insert(tk.END, f"{idx}. {t['last_name']} {t['first_name']} ({t['username']})")

    def load_groups(self):
        # Загружает список групп
        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for i, group in enumerate(self.groups, 1):
            self.groups_listbox.insert(tk.END, f"{i}. {group['name']}")

    def load_students(self):
        # Загружает список студентов выбранной группы
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
        # Обновляет список студентов при выборе группы
        self.load_students()

    # --- Операции с преподавателями ---
    def add_teacher(self):
        # Добавляет нового преподавателя
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
        # Удаляет выбранного преподавателя
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
        # Открывает диалог назначения преподавателя в группы
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

    # --- Операции с группами ---
    def add_group(self):
        # Добавляет новую группу
        name = simpledialog.askstring("Имя группы", "Введите название группы:", parent=self)
        code = simpledialog.askstring("Код группы", "Введите код группы:", parent=self)
        if name and code:
            try:
                self.db.add_group(name, code)
                self.load_groups()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def edit_group(self):
        # Редактирует выбранную группу
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
        # Удаляет выбранную группу
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
        # Открывает окно просмотра состава группы
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Выберите группу для просмотра состава.")
            return
        group = self.groups[idx[0]]
        from group_users_form import GroupMembersForm
        GroupMembersForm(self, group['id'], group['name'], self.db)

    # --- Операции со студентами ---
    def add_student(self):
        # Добавляет нового студента в выбранную группу
        idx = self.groups_listbox.curselection()
        if not idx or idx[0] >= len(self.groups):
            messagebox.showerror("Ошибка", "Сначала выберите группу для добавления студента.")
            return
        from user_form import UserForm
        group_id = self.groups[idx[0]]['id']
        dlg = UserForm(self, "Добавить студента", group_id=group_id, role="student")
        self.load_students()

    def delete_student(self):
        # Удаляет выбранного студента из группы
        idx = self.students_listbox.curselection()
        if not idx or idx[0] >= len(self.students):
            messagebox.showerror("Ошибка", "Выберите студента для удаления.")
            return
        student_id = self.students[idx[0]]["id"]
        if messagebox.askyesno("Удалить студента", "Вы уверены?"):
            self.db.delete_user(student_id)
            self.load_students()

    def import_students(self):
        # Импортирует студентов из текстового файла в выбранную группу
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

    # --- Навигация ---
    def go_back(self):
        # Возвращает к предыдущему окну
        self.destroy()
        if self.parent:
            self.parent.deiconify()