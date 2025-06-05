import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import Database
# from result_form import ResultForm
from journal_window import JournalWindow

class StudentForm(tk.Toplevel):
    # === Инициализация и конфигурация окна ===
    def __init__(self, user_id):
        super().__init__()
        self.db = Database()
        self.user_id = user_id
        user = self.db.get_user_by_id(self.user_id)
        if user:
            self.first_name = user['first_name']
            self.last_name = user['last_name']
            username = user['username']
        else:
            self.first_name = self.last_name = ""
            username = ""
        self.title(f"Панель студента - {self.last_name} {self.first_name}")
        self.geometry("400x300")
        self.resizable(False, False)
        self.center_window()

        group_id = user["group_id"] if user else None
        group_info = self.db.get_group_by_id(group_id)
        group_name = group_info["name"] if group_info else "Не определена"

        # Фрейм с информацией о студенте
        info_frame = tk.Frame(self)
        info_frame.pack(pady=10)
        tk.Label(info_frame, text=f"Студент: {self.last_name} {self.first_name}", font=("Arial", 14, "bold")).pack()
        tk.Label(info_frame, text=f"Группа: {group_name}", font=("Arial", 12)).pack()

        # Фрейм с кнопками управления
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Тесты", width=20, command=self.open_tests).pack(pady=5)
        tk.Button(btn_frame, text="Журнал", width=20, command=self.open_journal).pack(pady=5)
        tk.Button(btn_frame, text="Назад", width=20, command=self.go_back).pack(pady=5)
        tk.Button(btn_frame, text="Выход", width=20, command=self.exit_program).pack(pady=5)

    # === Вспомогательные методы интерфейса ===
    def center_window(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 400
            height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # === Методы обработки событий кнопок ===
    def open_tests(self):
        """Открывает окно выбора тестов."""
        self.withdraw()
        from test_selection_form import TestSelectionForm
        TestSelectionForm(self, self.user_id, student_form=self).mainloop()

    def open_journal(self):
        """Открывает окно с журналом студента."""
        try:
            JournalWindow(self, self.db, self.user_id)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def go_back(self):
        """Возврат к окну авторизации."""
        self.destroy()
        from login_form import LoginForm
        LoginForm().mainloop()

    def exit_program(self):
        """Завершает работу приложения после подтверждения."""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.quit()
            self.destroy()