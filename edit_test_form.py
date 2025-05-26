import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database

class EditTestForm(tk.Toplevel):
    def __init__(self, parent, test_id):
        super().__init__(parent)
        self.db = Database()
        self.test_id = test_id
        self.parent = parent
        self.title("Редактирование теста")
        self.geometry("500x400")
        self.center_window()
        self.questions = self.db.get_questions(test_id)
        self.create_widgets()
        self.load_questions()

    def create_widgets(self):
        tk.Label(self, text="Редактирование теста", font=("Arial", 16)).pack(pady=10)
        self.questions_listbox = tk.Listbox(self)
        self.questions_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        actions = [
            ("Добавить вопрос", self.add_question),
            ("Просмотреть вопрос", self.view_question),
            ("Редактировать вопрос", self.edit_question),
            ("Удалить вопрос", self.delete_question),
            ("Назад", self.go_back)
        ]
        for text, cmd in actions:
            tk.Button(self, text=text, command=cmd).pack(pady=5)

    def load_questions(self):
        self.questions = self.db.get_questions(self.test_id)
        self.questions_listbox.delete(0, tk.END)
        for q in self.questions:
            self.questions_listbox.insert(tk.END, f"{q['theme_local_number']}: {q['text']}")

    def ask_question_data(self, default_text="", default_options=None, default_correct=None):
        q_text = self.open_input_dialog("Вопрос", "Введите текст вопроса:", default_text)
        if not q_text: return None

        total = self.open_input_dialog(
            "Количество ответов", "Введите общее количество ответов (2-10):",
            str(len(default_options) if default_options else 2)
        )
        if not (total and total.isdigit() and 2 <= int(total) <= 10):
            messagebox.showerror("Ошибка", "Количество ответов должно быть числом от 2 до 10.", parent=self)
            return None
        total = int(total)

        options = []
        for i in range(total):
            default = default_options[i] if default_options and i < len(default_options) else ""
            opt = self.open_input_dialog("Вариант ответа", f"Введите текст варианта ответа {i+1}:", default)
            if not (opt and opt.strip()):
                messagebox.showerror("Ошибка", f"Вариант ответа {i+1} не может быть пустым.", parent=self)
                return None
            options.append(opt.strip())

        correct_def = ", ".join(str(idx+1) for idx in (default_correct or []))
        correct = self.open_input_dialog(
            "Правильные ответы", f"Введите номера правильных ответов через запятую (1-{total}):", correct_def
        )
        if not correct:
            messagebox.showerror("Ошибка", "Необходимо указать хотя бы один правильный ответ.", parent=self)
            return None
        try:
            indices = [int(x.strip())-1 for x in correct.split(",") if x.strip()]
            if not indices or not all(0 <= idx < total for idx in indices):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные номера правильных ответов.", parent=self)
            return None
        return q_text, options, list(set(indices))

    def add_question(self):
        try:
            data = self.ask_question_data()
            if not data: return
            q_text, options, correct = data
            if any(q['text'].strip().lower() == q_text.strip().lower() for q in self.questions):
                messagebox.showerror("Ошибка", "Вопрос с таким текстом уже существует в этом тесте.", parent=self)
                return
            self.db.add_question(self.test_id, q_text, options, correct)
            self.load_questions()
            messagebox.showinfo("Вопрос добавлен", f"Вопрос успешно добавлен:\n\n{q_text}", parent=self)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def view_question(self):
        idx = self.get_selected_index("просмотра")
        if idx is None: return
        self.load_questions()  # Всегда обновлять данные перед просмотром
        q = self.questions[idx]
        if q['options']:
            for i, opt in enumerate(q['options']):
                tk.Label(frame, text=f"{i+1}. {opt}", font=("Arial", 12), background="#f0f0f0", anchor="w", justify="left").pack(pady=5, anchor="w", fill="x")
        else:
            tk.Label(frame, text="Нет вариантов ответа", font=("Arial", 12), background="#f0f0f0", fg="red").pack(pady=5, anchor="w", fill="x")
        win = tk.Toplevel(self)
        win.title("Просмотр вопроса")
        self.center_window(win)
        win.geometry("400x400")
        canvas = tk.Canvas(win, borderwidth=0, background="#f0f0f0")
        frame = tk.Frame(canvas, background="#f0f0f0")
        vscroll = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((20, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Вопрос
        q_lbl = tk.Label(frame, text=q['text'], font=("Arial", 14), background="#f0f0f0", anchor="center", justify="center")
        q_lbl.pack(pady=10, fill="x")
        tk.Label(frame, text="Варианты ответов:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)

        # Варианты ответов
        if q['options']:
            for i, opt in enumerate(q['options']):
                tk.Label(frame, text=f"{i+1}. {opt}", font=("Arial", 12), background="#f0f0f0", anchor="w", justify="left").pack(pady=5, anchor="w", fill="x")
        else:
            tk.Label(frame, text="Нет вариантов ответа", font=("Arial", 12), background="#f0f0f0", fg="red").pack(pady=5, anchor="w", fill="x")

        # Правильные ответы
        tk.Label(frame, text="Правильные ответы:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)
        corr_lbls = [
            tk.Label(frame, text=f"{i+1}. {q['options'][i]}", font=("Arial", 12), fg="green", background="#f0f0f0", anchor="w", justify="left")
            for i in q.get('correct_option', [])
            if isinstance(i, int) and 0 <= i < len(q['options'])
        ]
        if corr_lbls:
            for lbl in corr_lbls: lbl.pack(pady=5, anchor="w", fill="x")
        else:
            tk.Label(frame, text="Нет правильных ответов", font=("Arial", 12), background="#f0f0f0", fg="red").pack(pady=5, anchor="w", fill="x")

    def edit_question(self):
        idx = self.get_selected_index("редактирования")
        if idx is None: return
        q = self.questions[idx]
        data = self.ask_question_data(q["text"], q["options"], q.get("correct_option", []))
        if not data: return
        q_text, options, correct = data
        self.db.update_question(q["id"], q_text, options, correct)
        self.load_questions()
        messagebox.showinfo("Успешно", "Вопрос успешно обновлён.", parent=self)

    def delete_question(self):
        idx = self.get_selected_index("удаления")
        if idx is None: return
        q = self.questions[idx]
        if messagebox.askyesno("Удаление вопроса", f"Вы уверены, что хотите удалить вопрос №{q['theme_local_number']}?", parent=self):
            self.db.delete_question(q["id"])
            self.renumber_questions()
            self.load_questions()
            messagebox.showinfo("Вопрос удалён", "Вопрос успешно удалён.", parent=self)

    def renumber_questions(self):
        for idx, q in enumerate(self.db.get_questions(self.test_id)):
            if q['theme_local_number'] != idx+1:
                self.db.update_theme_local_number(q['id'], idx+1)

    def go_back(self):
        self.destroy()
        if self.parent: self.parent.deiconify()

    def center_window(self, window=None):
        window = window or self
        window.update_idletasks()
        w, h = window.winfo_width(), window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        window.geometry(f"+{x}+{y}")

    def open_input_dialog(self, title, prompt, default=""):
        return simpledialog.askstring(title, prompt, initialvalue=default, parent=self)

    def get_selected_index(self, action):
        idxs = self.questions_listbox.curselection()
        if not idxs:
            messagebox.showerror("Ошибка", f"Выберите вопрос для {action}.", parent=self)
            return None
        return idxs[0]
