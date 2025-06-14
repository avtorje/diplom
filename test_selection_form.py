import tkinter as tk
from tkinter import messagebox
from database import Database
from test_form import TestForm

class TestSelectionForm(tk.Toplevel):
    # === Инициализация и конфигурация окна ===
    def __init__(self, parent, user_id, student_form):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.student_form = student_form
        self.title("Выбор теста")
        self.geometry("400x400")
        self.resizable(False, False)
        self.center_window()

        tk.Label(self, text="Доступные тесты:", font=("Arial", 14, "bold")).pack(pady=10)

        self.tests_listbox = tk.Listbox(self, font=("Arial", 12))
        self.tests_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tests_listbox.bind("<Double-Button-1>", self.start_test)

        tk.Button(self, text="Назад", command=self.go_back).pack(pady=10)

        self.load_tests()

    def center_window(self):
        # Центрирование окна на экране
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 400
            height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # === Загрузка и отображение тестов ===
    def load_tests(self):
        # Получение пользователя и загрузка доступных тестов
        user = self.db.get_user_by_id(self.user_id)
        group_id = user["group_id"] if user else None
        self.tests = self.db.get_unpassed_tests_for_user(self.user_id, group_id)
        self.tests_listbox.delete(0, tk.END)
        if self.tests:
            for test in self.tests:
                test_name = test["name"]
                timer = test.get("timer_seconds")
                timer_str = f" (Время выполнения: {timer//60} мин)" if timer and timer > 0 else ""
                self.tests_listbox.insert(tk.END, f"{test_name}{timer_str}")
            self.tests_listbox.config(state=tk.NORMAL)
        else:
            self.tests_listbox.insert(tk.END, "Нет доступных тестов")
            self.tests_listbox.config(state=tk.DISABLED)

    # === Обработка событий пользователя ===
    def start_test(self, event):
        # Запуск выбранного теста
        selection = self.tests_listbox.curselection()
        if not selection or not self.tests:
            return
        idx = selection[0]
        test = self.tests[idx]
        test_id = test["id"]
        self.withdraw()
        from test_form import TestForm
        TestForm(self, self.user_id, test_id, self.student_form).mainloop()

    def go_back(self):
        # Возврат к предыдущему окну
        self.destroy()
        self.master.deiconify()