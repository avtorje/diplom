import tkinter as tk
from tkinter import messagebox
from database import Database
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

        group_id = self.db.get_user_group_id(self.user_id)
        group_info = self.db.get_group_by_id(group_id)
        group_name = group_info[1] if group_info else "Не определена"

        info_frame = tk.Frame(self)
        info_frame.pack(pady=10)
        tk.Label(info_frame, text=f"Студент: {self.username}", font=("Arial", 14, "bold")).pack()
        tk.Label(info_frame, text=f"Группа: {group_name}", font=("Arial", 12)).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Тесты", width=20, command=self.open_tests).pack(pady=5)
        tk.Button(btn_frame, text="Журнал", width=20, command=self.open_journal).pack(pady=5)
        tk.Button(btn_frame, text="Назад", width=20, command=self.go_back).pack(pady=5)
        tk.Button(btn_frame, text="Выход", width=20, command=self.exit_program).pack(pady=5)

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
        from test_selection_form import TestSelectionForm
        TestSelectionForm(self, self.user_id, student_form=self).mainloop()

    def open_journal(self):
        self.withdraw()
        ResultForm(self, self.user_id).mainloop()
        self.deiconify()

    def go_back(self):
        self.destroy()
        from login_form import LoginForm
        LoginForm().mainloop()

    def exit_program(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.quit()
            self.destroy()