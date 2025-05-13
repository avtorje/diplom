import tkinter as tk
from tkinter import messagebox
from database import Database


class TestForm(tk.Toplevel):
    def __init__(self, parent, user_id, theme_id):
        super().__init__(parent)
        self.db = Database()
        self.user_id = user_id
        self.theme_id = theme_id
        self.current_question_index = 0
        self.answers = []
        self.questions = self.db.get_questions(theme_id)
        self.title(f"Test - {self.db.get_test_name(theme_id)}")
        self.geometry("400x400")
        self.parent = parent

        if not self.questions:
            messagebox.showinfo("No Questions", "This test has no questions.")
            self.destroy()
            return

        self.create_widgets()
        self.load_question()

    def create_widgets(self):
        self.question_label = tk.Label(self, text="", wraplength=380, font=("Arial", 14))
        self.question_label.pack(pady=10)

        self.options_frame = tk.Frame(self)
        self.options_frame.pack(pady=10)

        self.submit_button = tk.Button(self, text="Submit Answer", command=self.submit_answer)
        self.submit_button.pack(pady=5)

        self.navigation_frame = tk.Frame(self)
        self.navigation_frame.pack(pady=10)

        self.previous_button = tk.Button(self.navigation_frame, text="Previous", command=self.previous_question)
        self.previous_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(self.navigation_frame, text="Next", command=self.next_question)
        self.next_button.grid(row=0, column=1, padx=5)

        self.finish_button = tk.Button(self, text="Finish Test", command=self.finish_test)
        self.finish_button.pack(pady=5)

    def load_question(self):
        question = self.questions[self.current_question_index]
        # Добавляем независимую нумерацию вопросов (theme_local_number)
        question_text = f"Q{question['theme_local_number']}: {question['text']}"
        self.question_label.config(text=question_text)

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.selected_option = tk.IntVar(value=-1)

        for idx, option in enumerate(question["options"]):
            tk.Radiobutton(
                self.options_frame, text=option, variable=self.selected_option, value=idx
            ).pack(anchor="w")

        # Если на вопрос есть ответ, выбираем его.
        if len(self.answers) > self.current_question_index:
            self.selected_option.set(self.answers[self.current_question_index])

    def submit_answer(self):
        selected = self.selected_option.get()
        if selected == -1:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return

        # Save answer
        if len(self.answers) > self.current_question_index:
            self.answers[self.current_question_index] = selected
        else:
            self.answers.append(selected)

        messagebox.showinfo("Answer Submitted", "Your answer has been recorded.")

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()
        else:
            messagebox.showinfo("End of Test", "You have reached the last question.")

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()
        else:
            messagebox.showinfo("Start of Test", "This is the first question.")

    def finish_test(self):
        if len(self.answers) < len(self.questions):
            if not messagebox.askyesno(
                "Incomplete Test", "You have unanswered questions. Finish anyway?"
            ):
                return

        score = self.calculate_score()
        self.db.save_test_results(self.user_id, self.theme_id, self.questions, self.answers, score)
        messagebox.showinfo("Test Completed", f"You scored {score} out of {len(self.questions)}!")
        self.destroy()
        self.parent.deiconify()

    def calculate_score(self):
        score = 0
        for idx, question in enumerate(self.questions):
            if idx < len(self.answers) and self.answers[idx] == question["correct_option"]:
                score += 1
        return score