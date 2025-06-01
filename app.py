import tkinter as tk
from login_form import LoginForm
from database import Database

if __name__ == "__main__":
    # Инициализация базы данных
    db = Database()

    # Запуск приложения
    app = LoginForm()
    app.mainloop()