import tkinter as tk
from tkinter import messagebox
from database import Database

class TestForm(tk.Toplevel):
    def __init__(self, parent, user_id, test_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.test_id = test_id
        self.current_question_index = 0
        self.answers = []
        self.questions = self.db.get_questions(test_id)
        self.title(f"Тест - {self.db.get_test_name(test_id)}")
        self.geometry("400x400")
        self.parent = parent

        if not self.questions:
            messagebox.showinfo("Нет вопросов", "В этом тесте нет вопросов.")
            self.destroy()
            return

        self.selected_option = tk.IntVar(value=-1)
        self.create_widgets()
        self.load_question()

    def create_widgets(self):
        self.question_label = tk.Label(self, wraplength=380, font=("Arial", 14))
        self.question_label.pack(pady=10)

        self.options_frame = tk.Frame(self)
        self.options_frame.pack(pady=10)

        tk.Button(self, text="Ответить", command=self.submit_answer).pack(pady=5)

        nav = tk.Frame(self)
        nav.pack(pady=10)
        tk.Button(nav, text="Предыдущий", command=lambda: self.navigate(-1)).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Следующий", command=lambda: self.navigate(1)).grid(row=0, column=1, padx=5)

        tk.Button(self, text="Завершить тест", command=self.finish_test).pack(pady=5)

    def load_question(self):
        q = self.questions[self.current_question_index]
        self.question_label.config(text=f"Вопрос {q['theme_local_number']}: {q['text']}")
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.selected_option.set(self.answers[self.current_question_index] if len(self.answers) > self.current_question_index else -1)
        for idx, option in enumerate(q["options"]):
            tk.Radiobutton(self.options_frame, text=option, variable=self.selected_option, value=idx, font=("Arial", 12)).pack(anchor="w")

    def submit_answer(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.")
            return
        if len(self.answers) > self.current_question_index:
            self.answers[self.current_question_index] = sel
        else:
            self.answers.append(sel)
        messagebox.showinfo("Ответ принят", "Ваш ответ сохранён.")

    def navigate(self, step):
        new_idx = self.current_question_index + step
        if 0 <= new_idx < len(self.questions):
            self.current_question_index = new_idx
            self.load_question()
        else:
            messagebox.showinfo("Конец", "Дальше вопросов нет.")

    def finish_test(self):
        if len(self.answers) < len(self.questions):
            if not messagebox.askyesno("Тест не завершён", "Вы не ответили на все вопросы. Завершить тест?"):
                return
        # Подсчёт правильных ответов
        score = sum(
            ans == q["correct_options"]
            for ans, q in zip(self.answers, self.questions)
        )
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        messagebox.showinfo("Тест завершён", f"Ваш результат: {score} из {len(self.questions)}.")
        self.destroy()
        self.parent.deiconify()