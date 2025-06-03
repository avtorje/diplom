import tkinter as tk
from tkinter import messagebox
import time
from database import Database
from test_result_window import TestResultWindow

class TestForm(tk.Toplevel):
    def __init__(self, parent, user_id, test_id, student_form):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.test_id = test_id
        self.questions = self.db.get_questions(test_id)
        self.answers = []
        self.current_question_index = 0
        self.selected_option = tk.IntVar(value=-1)
        self.selected_options_vars = None  # Для множественного выбора
        self.all_dynamic_labels = []
        self.parent = parent
        self.start_time = time.time()
        self.student_form = student_form

        # Таймер и тема (обращения к словарю)
        self.theme = self.db.get_theme(test_id)
        self.timer_seconds = self.theme["timer_seconds"] if self.theme and self.theme["timer_seconds"] else None
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
            self.timer_label.place(x=10, y=10)
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
        # Остальные неотвеченные вопросы считаются без ответа
        while len(self.answers) < len(self.questions):
            q = self.questions[len(self.answers)]
            if len(q["correct_options"]) > 1:
                self.answers.append([])  # пустой выбор для множественного
            else:
                self.answers.append(-1)
        score = self.calculate_score()
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        percent = (score / len(self.questions)) * 100 if self.questions else 0
        total_time = self.timer_seconds
        self.show_result_window(total_time, percent)

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

        is_multiple = len(q["correct_options"]) > 1
        answers_frame = tk.Frame(self.scrollable_frame, background="#f0f0f0")
        answers_frame.pack(fill="x", padx=(20, 0), anchor="w")

        if is_multiple:
            self.selected_options_vars = []
            for idx, option in enumerate(q["options"]):
                var = tk.IntVar(value=0)
                cb = tk.Checkbutton(answers_frame, variable=var, background="#f0f0f0")
                cb.grid(row=idx, column=0, sticky="w", padx=(0, 5), pady=2)
                lbl = tk.Label(answers_frame, text=option, font=("Arial", 12),
                               background="#f0f0f0", justify="left", anchor="w", wraplength=360)
                lbl.grid(row=idx, column=1, sticky="w", pady=2)
                self.selected_options_vars.append(var)
                self.all_dynamic_labels.append(lbl)
        else:
            self.selected_option.set(-1)
            self.selected_options_vars = None
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
        q = self.questions[self.current_question_index]
        is_multiple = len(q["correct_options"]) > 1
        if is_multiple:
            selected = [i for i, var in enumerate(self.selected_options_vars) if var.get()]
            if not selected:
                messagebox.showwarning("Нет ответа", "Пожалуйста, выберите хотя бы один вариант.", parent=self)
                return
            self.answers.append(selected)
        else:
            sel = self.selected_option.get()
            if sel == -1:
                messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
                return
            self.answers.append(sel)
        self.current_question_index += 1
        self.load_question()

    def _on_finish(self):
        q = self.questions[self.current_question_index]
        is_multiple = len(q["correct_options"]) > 1
        if is_multiple:
            selected = [i for i, var in enumerate(self.selected_options_vars) if var.get()]
            if not selected:
                messagebox.showwarning("Нет ответа", "Пожалуйста, выберите хотя бы один вариант.", parent=self)
                return
            self.answers.append(selected)
        else:
            sel = self.selected_option.get()
            if sel == -1:
                messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
                return
            self.answers.append(sel)
        score = self.calculate_score()
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        percent = (score / len(self.questions)) * 100 if self.questions else 0
        # Время прохождения теста
        if self.timer_seconds:
            total_time = self.timer_seconds - self.time_left
        else:
            total_time = int(time.time() - self.start_time)
        self.show_result_window(total_time if self.timer_seconds else None, percent)

    def calculate_score(self):
        score = 0
        for ans, q in zip(self.answers, self.questions):
            if isinstance(ans, list):
                # Множественный выбор, сравнение множеств
                if set(ans) == set(q["correct_options"]):
                    score += 1
            else:
                if ans in q["correct_options"]:
                    score += 1
        return score

    def show_result_window(self, time_seconds, percent):
        def back_to_student():
            self.destroy()  # Закрыть окно теста
            self.student_form.deiconify()  # Показать панель студента
        TestResultWindow(
            self,
            db=self.db,
            user_id=self.user_id,
            theme_id=self.test_id,
            time_seconds=time_seconds,
            percent=percent,
            back_callback=back_to_student
        )
        self.withdraw()  # Скрыть форму теста на время показа результатов