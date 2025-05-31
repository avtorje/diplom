import tkinter as tk
from tkinter import messagebox
from database import Database
from test_form import TestForm
from result_form import ResultForm

class StudentForm(tk.Toplevel):
    def __init__(self, user_id, username):
        super().__init__()
        self.db = Database()
        self.user_id = user_id
        self.username = username
        self.title(f"Панель студента - {username}")
        self.geometry("400x300")
        self.resizable(False, False)
        self.center_window()

        # Получаем информацию о группе
        group_id = self.db.get_user_group_id(self.user_id)
        group_info = self.db.get_group_by_id(group_id)
        group_name = group_info[1] if group_info else "Не определена"

        # Информация о студенте
        info_frame = tk.Frame(self)
        info_frame.pack(pady=10)
        tk.Label(info_frame, text=f"Студент: {self.username}", font=("Arial", 14, "bold")).pack()
        tk.Label(info_frame, text=f"Группа: {group_name}", font=("Arial", 12)).pack()

        # Кнопки
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Тесты", width=20, command=self.open_tests).pack(pady=5)
        tk.Button(btn_frame, text="Журнал", width=20, command=self.open_journal).pack(pady=5)
        tk.Button(btn_frame, text="Назад", width=20, command=self.go_back).pack(pady=5)
        tk.Button(btn_frame, text="Выход", width=20, command=self.logout).pack(pady=5)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 400
            height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def open_tests(self):
        self.withdraw()
        ThemeTestSelection(self, self.user_id, self.username).mainloop()

    def open_journal(self):
        self.withdraw()
        ResultForm(self, self.user_id).mainloop()

    def go_back(self):
        self.destroy()

    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.destroy()

class ThemeTestSelection(tk.Toplevel):
    def __init__(self, parent, user_id, username):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.username = username
        self.title("Выбор теста")
        self.geometry("350x200")
        self.resizable(False, False)
        self.center_window()

        tk.Label(self, text="Выберите тест", font=("Arial", 13)).pack(pady=10)

        self.theme_var = tk.StringVar(self)
        self.theme_dropdown = tk.OptionMenu(self, self.theme_var, "")
        self.theme_dropdown.pack(pady=5)

        tk.Button(self, text="Начать тест", command=self.start_test).pack(pady=10)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=2)

        self.load_themes()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 350
            height = 200
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_themes(self):
        group_id = self.db.get_user_group_id(self.user_id)
        themes = self.db.get_all_tests(group_id=group_id)
        menu = self.theme_dropdown["menu"]
        menu.delete(0, "end")
        if themes:
            for theme_id, theme_name in themes:
                menu.add_command(label=theme_name, command=lambda v=theme_name: self.theme_var.set(v))
            self.theme_var.set(themes[0][1])
        else:
            self.theme_var.set("Нет доступных тестов")

    def start_test(self):
        selected_theme = self.theme_var.get()
        theme_id = self.db.get_test_id(selected_theme)
        if theme_id:
            self.withdraw()
            TestForm(self, self.user_id, theme_id).mainloop()
        else:
            messagebox.showerror("Ошибка", "Выберите корректный тест.")

    def go_back(self):
        self.destroy()
        self.master.deiconify()