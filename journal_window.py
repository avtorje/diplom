import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def calc_mark(score: int) -> int:
    if score >= 90:
        return 5
    elif score >= 70:
        return 4
    elif score >= 50:
        return 3
    elif score >= 30:
        return 2
    else:
        return 1

def format_timer(seconds):
    if seconds is None:
        return "Без ограничения"
    else:
        m = int(seconds) // 60
        return f"{m} минут" if m else f"{seconds} секунд"

class JournalWindow(tk.Toplevel):
    def __init__(self, master, db, user_id):
        super().__init__(master)
        self.title("Журнал прохождения тестов")
        self.geometry("900x400")

        columns = ("test_name", "teacher", "date", "score", "mark", "timer", "answers")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("test_name", text="Название теста")
        self.tree.heading("teacher", text="Преподаватель")
        self.tree.heading("date", text="Дата")
        self.tree.heading("score", text="Результат (%)")
        self.tree.heading("mark", text="Оценка")
        self.tree.heading("timer", text="Ограничение по времени")
        self.tree.heading("answers", text="Время прохождения (сек)")

        # Устанавливаем ширину столбцов: score и mark уменьшены в 3 раза
        self.tree.column("score", anchor="center", width=100) # Было 150, стало 50
        self.tree.column("mark", anchor="center", width=100)  # Было 120, стало 40

        # Остальные столбцы можно оставить по умолчанию или скорректировать под себя
        for col in columns:
            if col not in ("score", "mark"):
                self.tree.column(col, anchor="center")

        # Вертикальный скроллбар
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Горизонтальный скроллбар
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")  # горизонтальный скроллбар под деревом

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Итоговая строка под скроллами
        self.avg_label = ttk.Label(self, text="")
        self.avg_label.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.populate(db, user_id)
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 900
            height = 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def populate(self, db, user_id):
        results = db.get_journal_for_user(user_id)
        total = 0
        count = 0
        for r in results:
            mark = calc_mark(r["score"])
            timer_display = format_timer(r["timer_seconds"])
            answers_time = r["elapsed_seconds"] if "elapsed_seconds" in r.keys() else ""
            teacher = r["teacher_name"] if "teacher_name" in r.keys() else ""
            self.tree.insert(
                "", "end",
                values=(
                    r["test_name"],
                    teacher,
                    r["date"],
                    r["score"],
                    mark,
                    timer_display,
                    answers_time
                )
            )
            total += mark
            count += 1
        avg = round(total / count, 2) if count else 0
        self.avg_label.config(text=f"Средний балл по всем тестам: {avg}")