import tkinter as tk
import datetime

class TestResultWindow(tk.Toplevel):
    # ---------- Инициализация и конфигурация окна ----------
    def __init__(self, parent, db, user_id, theme_id, time_seconds=None, percent=0, back_callback=None):
        super().__init__(parent)
        self.title("Результаты теста")
        self.geometry("350x220")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.grab_set()  # Блокирует взаимодействие с другими окнами

        self.lift()
        self.attributes('-topmost', True)
        self.center_window()  # Центрирует окно на экране

        self.back_callback = back_callback
        self.db = db
        self.user_id = user_id
        self.theme_id = theme_id
        self.percent = percent
        self.time_seconds = time_seconds

        # ---------- Отображение информации о результате теста ----------
        label_title = tk.Label(self, text="Тест завершён!", font=("Arial", 16, "bold"),
                              bg="#f0f0f0", anchor="center", justify="center")
        label_title.pack(pady=(24, 12))

        if time_seconds is not None:
            mins = time_seconds // 60
            secs = time_seconds % 60
            time_str = f"{mins} мин {secs:02} сек"
            label_time = tk.Label(self, text=f"Время: {time_str}", font=("Arial", 13), bg="#f0f0f0")
            label_time.pack(pady=(0, 8))

        label_score = tk.Label(self, text=f"Результат: {percent:.0f}%", font=("Arial", 13), bg="#f0f0f0")
        label_score.pack(pady=(0, 28))

        btn = tk.Button(self, text="Вернуться на главную", font=("Arial", 12), width=20,
                        command=self._on_back)
        btn.pack(pady=0)

        # ---------- Сохранение результата теста ----------
        self.save_result()

    # ---------- Методы работы с базой данных ----------
    def save_result(self):
        """Сохраняет результат теста в базу данных."""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params = [self.user_id, self.theme_id, int(self.percent), date_str, ""]
        query = "INSERT INTO TEST_SUMMARY (user_id, theme_id, score, date, answers"
        if self.time_seconds is not None:
            query += ", elapsed_seconds"
            params.append(int(self.time_seconds))
        query += ") VALUES (?, ?, ?, ?, ?"
        if self.time_seconds is not None:
            query += ", ?"
        query += ")"
        self.db._execute(query, tuple(params))

    # ---------- Обработка событий ----------
    def _on_back(self):
        """Закрывает окно и вызывает обратный вызов возврата."""
        self.destroy()
        if self.back_callback:
            self.back_callback()

    # ---------- Вспомогательные методы ----------
    def center_window(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        w, h = 350, 220
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")