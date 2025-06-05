import tkinter as tk
from database import Database

class GroupMembersForm(tk.Toplevel):
    # ----------- Инициализация и конфигурация окна -----------
    def __init__(self, parent, group_id, group_name, db):
        super().__init__(parent)
        self.db = db
        self.group_id = group_id
        self.title(f"Состав группы: {group_name}")
        self.center_window(400, 470)
        self.create_widgets()

    # ----------- Вспомогательные методы интерфейса -----------
    def center_window(self, width=400, height=470):
        # Центрирует окно на экране
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ----------- Создание и заполнение виджетов -----------
    def create_widgets(self):
        pad = {"padx": 10, "pady": 5}

        # Блок преподавателей
        tk.Label(self, text="Преподаватели группы:", font=("Arial", 12, "bold")).pack(anchor="w", **pad)
        adm_frame = tk.Frame(self)
        adm_frame.pack(fill=tk.X, padx=10)
        adm_scroll = tk.Scrollbar(adm_frame, orient=tk.VERTICAL)
        self.admins_listbox = tk.Listbox(adm_frame, height=6, yscrollcommand=adm_scroll.set)
        adm_scroll.config(command=self.admins_listbox.yview)
        self.admins_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        adm_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        admins = self.db.get_admins_by_group(self.group_id)
        if admins:
            for a in admins:
                # Добавление преподавателей в список
                self.admins_listbox.insert(tk.END, f"{a['last_name']} {a['first_name']} ({a['username']})")
        else:
            # Если преподавателей нет
            self.admins_listbox.insert(tk.END, "Нет преподавателей")

        # Блок студентов
        tk.Label(self, text="Студенты группы:", font=("Arial", 12, "bold")).pack(anchor="w", **pad)
        stud_frame = tk.Frame(self)
        stud_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        stud_scroll = tk.Scrollbar(stud_frame, orient=tk.VERTICAL)
        self.students_listbox = tk.Listbox(stud_frame, height=12, yscrollcommand=stud_scroll.set)
        stud_scroll.config(command=self.students_listbox.yview)
        self.students_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stud_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        students = self.db.get_students_by_group(self.group_id)
        if students:
            for s in students:
                # Добавление студентов в список
                self.students_listbox.insert(tk.END, f"{s['last_name']} {s['first_name']}")
        else:
            # Если студентов нет
            self.students_listbox.insert(tk.END, "Нет студентов")

        # Кнопка закрытия окна
        tk.Button(self, text="Закрыть", command=self.destroy).pack(pady=15)