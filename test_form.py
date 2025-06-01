import tkinter as tk
from tkinter import messagebox
from database import Database

class TestForm(tk.Toplevel):
    def __init__(self, parent, user_id, test_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.test_id = test_id
        self.questions = self.db.get_questions(test_id)
        self.answers = []
        self.current_question_index = 0
        self.selected_option = tk.IntVar(value=-1)
        self.all_dynamic_labels = []
        self.parent = parent

        # Таймер и тема (оставляем как есть)
        self.theme = self.db.get_theme(test_id)
        self.timer_seconds = self.theme[2] if self.theme and self.theme[2] else None
        self.time_left = self.timer_seconds

        self.title(f"Тест - {self.db.get_test_name(test_id)}")
        self.geometry("500x400")
        self.center_window()

        if not self.questions:
            messagebox.showinfo("Нет вопросов", "В этом тесте нет вопросов.")
            self.destroy()
            return

        self._build_ui()
        self.load_question()

        if self.timer_seconds:
            self.timer_label = tk.Label(self, text=self.format_time(self.time_left), font=("Arial", 14), bg="#f0f0f0")
            self.timer_label.place(x=10, y=10)  # Левый верхний угол
            self.update_timer()

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"Осталось: {minutes:02}:{secs:02}"

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=self.format_time(self.time_left))
            self.time_left -= 1
            self.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Время вышло!")
            self.finish_test_due_to_timeout()

    def finish_test_due_to_timeout(self):
        messagebox.showinfo("Тест завершён", "Время вышло! Тест завершён автоматически.", parent=self)
        # Остальные неотвеченные вопросы считаются без ответа (или неверными)
        self.answers += [-1] * (len(self.questions) - len(self.answers))
        score = sum(ans == q["correct_options"] for ans, q in zip(self.answers, self.questions))
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        self.destroy()
        self.parent.deiconify()

    def center_window(self):
        self.update_idletasks()
        w, h = 500, 400
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.container, background="#f0f0f0", highlightthickness=0)
        self.vscroll = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.outer_frame = tk.Frame(self.canvas, background="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.outer_frame, anchor="nw", tags="inner")
        self.scrollable_frame = tk.Frame(self.outer_frame, background="#f0f0f0")
        self.scrollable_frame.pack(anchor="nw", pady=20)
        self.outer_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("inner", width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.next_button = tk.Button(self, text="Следующий", command=self._on_next)
        self.next_button.pack(pady=10, side="bottom")
        self.bind("<Configure>", lambda e: self.after(100, self._update_wraplength))

    def _update_wraplength(self):
        width = self.canvas.winfo_width() - 120
        for lbl in self.all_dynamic_labels:
            lbl.config(wraplength=width if width > 0 else 360)

    def load_question(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        self.all_dynamic_labels.clear()
        q = self.questions[self.current_question_index]
        q_label = tk.Label(self.scrollable_frame, text=q['text'], font=("Arial", 14),
                           background="#f0f0f0", justify="left", anchor="w", wraplength=420)
        q_label.pack(pady=(10, 10), padx=10, anchor="w")
        self.all_dynamic_labels.append(q_label)

        self.selected_option.set(-1)
        answers_frame = tk.Frame(self.scrollable_frame, background="#f0f0f0")
        answers_frame.pack(fill="x", padx=(20, 0), anchor="w")

        for idx, option in enumerate(q["options"]):
            rb = tk.Radiobutton(answers_frame, variable=self.selected_option, value=idx,
                                background="#f0f0f0", highlightthickness=0)
            rb.grid(row=idx, column=0, sticky="w", padx=(0, 5), pady=2)

            lbl = tk.Label(answers_frame, text=option, font=("Arial", 12),
                           background="#f0f0f0", justify="left", anchor="w", wraplength=360)
            lbl.grid(row=idx, column=1, sticky="w", pady=2)
            self.all_dynamic_labels.append(lbl)

        is_last = self.current_question_index == len(self.questions) - 1
        self.next_button.config(
            text="Завершить тест" if is_last else "Следующий",
            command=self._on_finish if is_last else self._on_next
        )
        self.after(100, self._update_wraplength)
        self.canvas.yview_moveto(0)

    def _on_next(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
            return
        self.answers.append(sel)
        self.current_question_index += 1
        self.load_question()

    def _on_finish(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
            return
        self.answers.append(sel)
        score = sum(ans == q["correct_options"] for ans, q in zip(self.answers, self.questions))
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        messagebox.showinfo("Тест завершён", f"Ваш результат: {score} из {len(self.questions)}.", parent=self)
        self.destroy()
        self.parent.deiconify()