import tkinter as tk
from tkinter import messagebox, simpledialog
from manage_tests_form import ManageTestsForm
from manage_users_form import ManageUsersForm
from statistics_form import StatisticsForm
from database import Database

class AdminForm(tk.Tk):
    # === Инициализация и конфигурация окна ===
    def __init__(self, admin_id):
        super().__init__()
        self.db = Database()
        self.admin_id = admin_id
        self.title("Панель администратора")
        self.geometry("400x300")
        self.center_window()
        self.create_widgets()

    def center_window(self):
        # Центрирование окна на экране
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # === Создание и обработка элементов интерфейса ===
    def create_widgets(self):
        # Создание виджетов и кнопок панели администратора
        tk.Label(self, text="Панель администратора", font=("Arial", 16)).pack(pady=10)
        buttons = [
            ("Управление тестами", self.open_form, ManageTestsForm),
            ("Управление пользователями", self.open_form, ManageUsersForm),
            ("Просмотр статистики", self.open_form, StatisticsForm),
            ("Изменить пароль", self.change_password, None),
            ("Назад", self.go_back, None),
            ("Выход", self.exit_app, None)
        ]
        for text, cmd, arg in buttons:
            tk.Button(self, text=text, command=(lambda c=cmd, a=arg: c(a) if a else c())).pack(pady=5)

    # === Методы управления формами ===
    def open_form(self, form_class):
        # Открытие выбранной формы и скрытие текущей
        self.withdraw()
        if form_class == ManageTestsForm:
            form_class(self, self.admin_id).mainloop()
        elif form_class.__name__ == "StatisticsForm":
            form_class(self, self.admin_id)
        elif form_class == ManageUsersForm:
            form_class(self, self.admin_id).mainloop()
        else:
            form_class(self).mainloop()

    # === Методы управления пользователем ===
    def change_password(self, _=None):
        # Изменение пароля администратора
        old = simpledialog.askstring("Старый пароль", "Введите старый пароль:", show='*', parent=self)
        if not old or not self.db.check_admin_password(self.admin_id, old):
            if old: messagebox.showerror("Ошибка", "Старый пароль неверный.", parent=self)
            return
        new = simpledialog.askstring("Новый пароль", "Введите новый пароль:", show='*', parent=self)
        if not new: return
        confirm = simpledialog.askstring("Подтверждение", "Повторите новый пароль:", show='*', parent=self)
        if new != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают.", parent=self)
            return
        self.db.update_admin_password(self.admin_id, new)
        messagebox.showinfo("Успешно", "Пароль успешно изменён!", parent=self)

    # === Методы управления приложением ===
    def go_back(self, _=None):
        # Возврат к форме входа
        if messagebox.askyesno("Вернуться", "Вы уверены, что хотите вернуться в меню входа?"):
            self.destroy()
            from login_form import LoginForm
            LoginForm().mainloop()

    def exit_app(self, _=None):
        # Завершение работы приложения
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.destroy()
