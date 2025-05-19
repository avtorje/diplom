import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database


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
        """Загрузка всех вопросов для текущего теста."""
        self.questions_listbox.delete(0, tk.END)
        for question in self.questions:
            self.questions_listbox.insert(tk.END, f"{question['theme_local_number']}: {question['text']}")
        
    def add_question(self):
        """Добавление нового вопроса."""
        try:
            question_text = self.open_input_dialog("Добавить вопрос", "Введите текст нового вопроса:")
            if not question_text:
                return

            total_answers = self.open_input_dialog(
                "Количество ответов", "Введите общее количество ответов (2-10):"
            )
            if not total_answers or not total_answers.isdigit() or not (2 <= int(total_answers) <= 10):
                messagebox.showerror("Ошибка", "Количество ответов должно быть числом от 2 до 10.", parent=self)
                return
            total_answers = int(total_answers)

            options = []
            for i in range(total_answers):
                option = self.open_input_dialog(
                    "Добавить вариант ответа", f"Введите текст варианта ответа {i + 1}:"
                )
                if option and option.strip():
                    options.append(option.strip())
                else:
                    messagebox.showerror("Ошибка", f"Вариант ответа {i + 1} не может быть пустым.", parent=self)
                    return

            correct_answers = self.open_input_dialog(
                "Правильные ответы",
                f"Введите номера правильных ответов через запятую (1-{total_answers}):"
            )
            if not correct_answers:
                messagebox.showerror("Ошибка", "Необходимо указать хотя бы один правильный ответ.", parent=self)
                return

            try:
                parts = [x.strip() for x in correct_answers.split(",")]
                if "" in parts:
                    raise ValueError("Обнаружены пустые значения.")

                correct_answers = list(set(int(x) - 1 for x in parts))
            except ValueError:
                messagebox.showerror("Ошибка", "Номера правильных ответов должны быть целыми числами без пропусков.", parent=self)
                return

            if not correct_answers or not all(0 <= x < total_answers for x in correct_answers):
                messagebox.showerror(
                    "Ошибка", f"Номера правильных ответов должны быть в диапазоне от 1 до {total_answers}.", parent=self
                )
                return

            self.db.add_question(self.test_id, question_text, options, correct_answers)
            self.questions = self.db.get_questions(self.test_id)
            self.load_questions()
            messagebox.showinfo("Вопрос добавлен", f"Вопрос успешно добавлен:\n\n{question_text}", parent=self)
        except sqlite3.OperationalError as e:
            if e.args[0] == "database is locked":
                time.sleep(0.1)  # wait for 100ms
                self.add_question()  # retry the operation
            else:
                raise e
        question_text = self.open_input_dialog("Добавить вопрос", "Введите текст нового вопроса:")
        if not question_text:
            return

        total_answers = self.open_input_dialog(
            "Количество ответов", "Введите общее количество ответов (2-10):"
        )
        if not total_answers or not total_answers.isdigit() or not (2 <= int(total_answers) <= 10):
            messagebox.showerror("Ошибка", "Количество ответов должно быть числом от 2 до 10.", parent=self)
            return
        total_answers = int(total_answers)

        options = []
        for i in range(total_answers):
            option = self.open_input_dialog(
                "Добавить вариант ответа", f"Введите текст варианта ответа {i + 1}:"
            )
            if option and option.strip():
                options.append(option.strip())
            else:
                messagebox.showerror("Ошибка", f"Вариант ответа {i + 1} не может быть пустым.", parent=self)
                return

        correct_answers = self.open_input_dialog(
            "Правильные ответы",
            f"Введите номера правильных ответов через запятую (1-{total_answers}):"
        )
        if not correct_answers:
            messagebox.showerror("Ошибка", "Необходимо указать хотя бы один правильный ответ.", parent=self)
            return

        try:
            parts = [x.strip() for x in correct_answers.split(",")]
            if "" in parts:
                raise ValueError("Обнаружены пустые значения.")

            correct_answers = list(set(int(x) - 1 for x in parts))
        except ValueError:
            messagebox.showerror("Ошибка", "Номера правильных ответов должны быть целыми числами без пропусков.", parent=self)
            return

        if not correct_answers or not all(0 <= x < total_answers for x in correct_answers):
            messagebox.showerror(
                "Ошибка", f"Номера правильных ответов должны быть в диапазоне от 1 до {total_answers}.", parent=self
            )
            return

        self.db.add_question(self.test_id, question_text, options, correct_answers)
        self.questions = self.db.get_questions(self.test_id)
        self.load_questions()
        messagebox.showinfo("Вопрос добавлен", f"Вопрос успешно добавлен:\n\n{question_text}", parent=self)

    def view_question(self):
        """Просмотр выбранного вопроса с ответами и выделение правильных ответов."""
        selected_index = self.questions_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите вопрос для просмотра.", parent=self)
            return

        question = self.questions[selected_index[0]]
        question_text = question['text']
        options = question['options']
        correct_answers = question.get('correct_option', [])

        # Создает новое окно для отображения вопроса и ответов.
        question_window = tk.Toplevel(self)
        question_window.title("Просмотр вопроса")
        self.center_window(question_window)
        question_window.geometry("400x400")

        # --- Начало: добавляем скроллинг ---
        canvas = tk.Canvas(question_window, borderwidth=0, background="#f0f0f0")
        frame = tk.Frame(canvas, background="#f0f0f0")
        vscrollbar = tk.Scrollbar(question_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)

        vscrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0,0), window=frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)
        # --- Конец: добавляем скроллинг ---

        # Показывает текст вопроса, выравнивание по центру
        tk.Label(
            frame,
            text=question_text,
            font=("Arial", 14),
            background="#f0f0f0",
            anchor="center",
            justify="center"
        ).pack(pady=10, fill="x")

        # Показывает варианты ответов.
        tk.Label(frame, text="Варианты ответов:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)
        for i, option in enumerate(options):
            tk.Label(frame, text=f"{i+1}. {option}", font=("Arial", 12), background="#f0f0f0").pack(pady=5, anchor="w")

        # Показывает правильные ответы.
        tk.Label(frame, text="Правильные ответы:", font=("Arial", 12), background="#f0f0f0").pack(pady=5)
        for correct_answer in correct_answers:
            tk.Label(
                frame,
                text=f"{correct_answer+1}. {options[correct_answer]}",
                font=("Arial", 12),
                fg="green",
                background="#f0f0f0"
            ).pack(pady=5, anchor="w")
            
    def open_input_dialog(self, title, prompt, default=""):
        import tkinter.simpledialog as simpledialog
        return simpledialog.askstring(title, prompt, initialvalue=default, parent=self)

    def edit_question(self):
        """Редактирование выбранного вопроса."""
        selected_index = self.questions_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите вопрос для редактирования.", parent=self)
            return

        question = self.questions[selected_index[0]]

        # Редактировать текст вопроса
        new_question_text = self.open_input_dialog(
            "Редактировать вопрос", "Введите новый текст вопроса:", question["text"]
        )
        if new_question_text is None:
            return

        # Изменить количество ответов
        total_answers_str = self.open_input_dialog(
            "Количество ответов",
            "Введите новое общее количество ответов (2-10):",
            str(len(question["options"]))
        )
        if total_answers_str is None or not total_answers_str.isdigit() or not (2 <= int(total_answers_str) <= 10):
            messagebox.showerror("Ошибка", "Количество ответов должно быть числом от 2 до 10.", parent=self)
            return
        total_answers = int(total_answers_str)

        # Редактировать варианты ответов
        new_options = []
        for i in range(total_answers):
            default = question["options"][i] if i < len(question["options"]) else ""
            option_text = self.open_input_dialog(
                "Вариант ответа", f"Введите текст варианта ответа {i+1}:", default
            )
            if not option_text or not option_text.strip():
                messagebox.showerror("Ошибка", f"Вариант ответа {i+1} не может быть пустым.", parent=self)
                return
            new_options.append(option_text.strip())

        # Ввести правильные ответы
        correct_def = ", ".join(
            str(idx + 1) for idx in question["correct_option"] if idx < total_answers
        )
        correct_answers_str = self.open_input_dialog(
            "Правильные ответы",
            f"Введите номера правильных ответов через запятую (1-{total_answers}):",
            correct_def
        )
        if not correct_answers_str:
            messagebox.showerror("Ошибка", "Необходимо указать хотя бы один правильный ответ.", parent=self)
            return
        try:
            correct_indices = [int(x.strip()) - 1 for x in correct_answers_str.split(",")]
            if not all(0 <= idx < total_answers for idx in correct_indices):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные номера правильных ответов.", parent=self)
            return

        # Обновить вопрос в базе
        self.db.update_question(question["id"], new_question_text, new_options, correct_indices)
        self.questions = self.db.get_questions(self.test_id)
        self.load_questions()
        messagebox.showinfo("Успешно", "Вопрос успешно обновлён.", parent=self)

    def delete_question(self):
        """Удаление выбранного вопроса (заглушка)."""
        messagebox.showinfo("Удалить вопрос", "Функция удаления пока не реализована.", parent=self)

    def go_back(self):
        """Вернуться к списку тестов."""
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

    def delete_question(self):
        """Удаление выбранного вопроса."""
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

