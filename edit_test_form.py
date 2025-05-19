import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
import sqlite3
import time

class EditTestForm(tk.Toplevel):
    def __init__(self, parent, test_id):
        super().__init__(parent)
        self.db = Database()
        self.test_id = test_id
        self.title("Редактирование теста")
        self.geometry("500x400")
        self.center_window()
        self.parent = parent

        self.questions = self.db.get_questions(test_id)
        self.create_widgets()
        self.load_questions()

    def create_widgets(self):
        tk.Label(self, text="Редактирование теста", font=("Arial", 16)).pack(pady=10)
        self.questions_listbox = tk.Listbox(self)
        self.questions_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Button(self, text="Добавить вопрос", command=self.add_question).pack(pady=5)
        tk.Button(self, text="Просмотреть вопрос", command=self.view_question).pack(pady=5)
        tk.Button(self, text="Редактировать вопрос", command=self.edit_question).pack(pady=5)
        tk.Button(self, text="Удалить вопрос", command=self.delete_question).pack(pady=5)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=5)

    def load_questions(self):
        self.questions_listbox.delete(0, tk.END)
        for question in self.questions:
            self.questions_listbox.insert(tk.END, f"{question['theme_local_number']}: {question['text']}")

    def ask_question_data(self, default_text="", default_options=None, default_correct=None):
        question_text = self.open_input_dialog("Вопрос", "Введите текст вопроса:", default_text)
        if not question_text:
            return None

        total_answers = self.open_input_dialog(
            "Количество ответов", "Введите общее количество ответов (2-10):",
            str(len(default_options) if default_options else 2)
        )
        if not total_answers or not total_answers.isdigit() or not (2 <= int(total_answers) <= 10):
            messagebox.showerror("Ошибка", "Количество ответов должно быть числом от 2 до 10.", parent=self)
            return None
        total_answers = int(total_answers)

        options = []
        for i in range(total_answers):
            default = default_options[i] if default_options and i < len(default_options) else ""
            option = self.open_input_dialog(
                "Вариант ответа", f"Введите текст варианта ответа {i + 1}:", default
            )
            if not option or not option.strip():
                messagebox.showerror("Ошибка", f"Вариант ответа {i + 1} не может быть пустым.", parent=self)
                return None
            options.append(option.strip())

        correct_def = ", ".join(str(idx + 1) for idx in default_correct) if default_correct else ""
        correct_answers = self.open_input_dialog(
            "Правильные ответы",
            f"Введите номера правильных ответов через запятую (1-{total_answers}):",
            correct_def
        )
        if not correct_answers:
            messagebox.showerror("Ошибка", "Необходимо указать хотя бы один правильный ответ.", parent=self)
            return None
        try:
            indices = [int(x.strip()) - 1 for x in correct_answers.split(",") if x.strip()]
            if not indices or not all(0 <= idx < total_answers for idx in indices):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные номера правильных ответов.", parent=self)
            return None

        return question_text, options, list(set(indices))

    def add_question(self):
        try:
            data = self.ask_question_data()
            if not data:
                return
            question_text, options, correct_answers = data
            self.db.add_question(self.test_id, question_text, options, correct_answers)
            self.questions = self.db.get_questions(self.test_id)
            self.load_questions()
            messagebox.showinfo("Вопрос добавлен", f"Вопрос успешно добавлен:\n\n{question_text}", parent=self)
        except sqlite3.OperationalError as e:
            if e.args[0] == "database is locked":
                time.sleep(0.1)
                self.add_question()
            else:
                raise

    def view_question(self):
        selected_index = self.questions_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите вопрос для просмотра.", parent=self)
            return
        question = self.questions[selected_index[0]]
        question_text = question['text']
        options = question['options']
        correct_answers = question.get('correct_option', [])

        question_window = tk.Toplevel(self)
        question_window.title("Просмотр вопроса")
        self.center_window(question_window)
        question_window.geometry("400x400")

        canvas = tk.Canvas(question_window, borderwidth=0, background="#f0f0f0")
        frame = tk.Frame(canvas, background="#f0f0f0")
        vscrollbar = tk.Scrollbar(question_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((20, 0), window=frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        frame.bind("<Configure>", on_frame_configure)

        question_label = tk.Label(
            frame, text=question_text, font=("Arial", 14),
            background="#f0f0f0", anchor="center", justify="center"
        )
        question_label.pack(pady=10, fill="x")

        answer_labels = []
        tk.Label(frame, text="Варианты ответов:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)
        for i, option in enumerate(options):
            lbl = tk.Label(
                frame, text=f"{i+1}. {option}", font=("Arial", 12),
                background="#f0f0f0", anchor="w", justify="left"
            )
            lbl.pack(pady=5, anchor="w", fill="x")
            answer_labels.append(lbl)

        tk.Label(frame, text="Правильные ответы:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)
        correct_labels = []
        for correct_answer in correct_answers:
            lbl = tk.Label(
                frame, text=f"{correct_answer+1}. {options[correct_answer]}", font=("Arial", 12),
                fg="green", background="#f0f0f0", anchor="w", justify="left"
            )
            lbl.pack(pady=5, anchor="w", fill="x")
            correct_labels.append(lbl)

        def update_wraplength(event):
            w = event.width - 40
            w = max(w, 100)
            question_label.config(wraplength=w)
            for lbl in answer_labels + correct_labels:
                lbl.config(wraplength=w)

        canvas.bind("<Configure>", update_wraplength)
        question_window.update_idletasks()
        initial_width = max(canvas.winfo_width() - 40, 100)
        question_label.config(wraplength=initial_width)
        for lbl in answer_labels + correct_labels:
            lbl.config(wraplength=initial_width)

    def open_input_dialog(self, title, prompt, default=""):
        return simpledialog.askstring(title, prompt, initialvalue=default, parent=self)

    def edit_question(self):
        selected_index = self.questions_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите вопрос для редактирования.", parent=self)
            return
        question = self.questions[selected_index[0]]
        data = self.ask_question_data(
            default_text=question["text"],
            default_options=question["options"],
            default_correct=question.get("correct_option", [])
        )
        if not data:
            return
        new_question_text, new_options, correct_indices = data
        self.db.update_question(question["id"], new_question_text, new_options, correct_indices)
        self.questions = self.db.get_questions(self.test_id)
        self.load_questions()
        messagebox.showinfo("Успешно", "Вопрос успешно обновлён.", parent=self)

    def delete_question(self):
        selected_index = self.questions_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите вопрос для удаления.", parent=self)
            return
        question = self.questions[selected_index[0]]
        question_id = question["id"]
        if messagebox.askyesno("Удаление вопроса", f"Вы уверены, что хотите удалить вопрос №{question['theme_local_number']}?", parent=self):
            self.db.delete_question(question_id)
            self.questions = self.db.get_questions(self.test_id)
            self.load_questions()
            messagebox.showinfo("Вопрос удалён", f"Вопрос №{question['theme_local_number']} успешно удалён.", parent=self)

    def go_back(self):
        self.destroy()
        if self.parent is not None:
            self.parent.deiconify()

    def center_window(self, window=None):
        if window is None:
            window = self
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"+{x}+{y}")
