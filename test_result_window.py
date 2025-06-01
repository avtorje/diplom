import tkinter as tk

class TestResultWindow(tk.Toplevel):
    def __init__(self, parent, time_seconds=None, percent=0, back_callback=None):
        super().__init__(parent)
        self.title("Результаты теста")
        self.geometry("350x220")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.grab_set()

        # Заголовок по центру
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
                        command=back_callback)
        btn.pack(pady=0)