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

        self.selected_option = tk.IntVar(value=-1)
        self.create_widgets()
        self.load_question()

    def create_widgets(self):
        self.question_label = tk.Label(self, wraplength=380, font=("Arial", 14))
        self.question_label.pack(pady=10)

        self.options_frame = tk.Frame(self)
        self.options_frame.pack(pady=10)

        tk.Button(self, text="Submit Answer", command=self.submit_answer).pack(pady=5)

        nav = tk.Frame(self)
        nav.pack(pady=10)
        tk.Button(nav, text="Previous", command=lambda: self.navigate(-1)).grid(row=0, column=0, padx=5)
        tk.Button(nav, text="Next", command=lambda: self.navigate(1)).grid(row=0, column=1, padx=5)

        tk.Button(self, text="Finish Test", command=self.finish_test).pack(pady=5)

    def load_question(self):
        q = self.questions[self.current_question_index]
        self.question_label.config(text=f"Q{q['theme_local_number']}: {q['text']}")
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.selected_option.set(self.answers[self.current_question_index] if len(self.answers) > self.current_question_index else -1)
        for idx, option in enumerate(q["options"]):
            tk.Radiobutton(self.options_frame, text=option, variable=self.selected_option, value=idx).pack(anchor="w")

    def submit_answer(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return
        if len(self.answers) > self.current_question_index:
            self.answers[self.current_question_index] = sel
        else:
            self.answers.append(sel)
        messagebox.showinfo("Answer Submitted", "Your answer has been recorded.")

    def navigate(self, step):
        new_idx = self.current_question_index + step
        if 0 <= new_idx < len(self.questions):
            self.current_question_index = new_idx
            self.load_question()
        else:
            messagebox.showinfo("Boundary", "No more questions in this direction.")

    def finish_test(self):
        if len(self.answers) < len(self.questions):
            if not messagebox.askyesno("Incomplete Test", "You have unanswered questions. Finish anyway?"):
                return
        score = sum(
            ans == q["correct_option"]
            for ans, q in zip(self.answers, self.questions)
        )
        self.db.save_test_results(self.user_id, self.theme_id, self.questions, self.answers, score)
        messagebox.showinfo("Test Completed", f"You scored {score} out of {len(self.questions)}!")
        self.destroy()
        self.parent.deiconify()
