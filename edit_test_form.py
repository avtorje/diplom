import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database

class EditTestForm(tk.Toplevel):
    # === Инициализация и создание интерфейса ===
    def __init__(self, parent, test_id, current_user_id):
        super().__init__(parent)
        self.db = Database()
        self.test_id = test_id
        self.current_user_id = current_user_id
        self.parent = parent
        self.title("Редактирование теста")
        self.geometry("500x650")
        self.center_window()
        self.create_widgets()
        self.initialized = False
        self.load_test_info()
        self.load_questions()
        self.initialized = True

    def create_widgets(self):
        # Создание всех элементов интерфейса
        tk.Label(self, text="Редактирование теста", font=("Arial", 16)).pack(pady=10)

        name_frame = tk.Frame(self)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="Название теста:").pack(side="left")
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(name_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(side="left", padx=(5, 10))

        timer_frame = tk.Frame(self)
        timer_frame.pack(pady=5)
        tk.Label(timer_frame, text="Таймер (минут):").pack(side="left")
        self.timer_var = tk.StringVar()
        self.timer_entry = tk.Entry(timer_frame, textvariable=self.timer_var, width=6)
        self.timer_entry.pack(side="left", padx=(0, 10))
        self.timer_check = tk.IntVar(value=1)
        self.timer_remove = tk.Checkbutton(timer_frame, text="Убрать таймер", variable=self.timer_check, command=self.toggle_timer)
        self.timer_remove.pack(side="left")
        tk.Button(timer_frame, text="Сохранить таймер", command=self.save_timer).pack(side="left", padx=5)

        tk.Label(self, text="Назначить тест в группы:").pack(pady=(10, 0))
        self.groups_frame = tk.Frame(self)
        self.groups_frame.pack(padx=10, pady=5, fill=tk.X)
        self.group_vars = []

        tk.Button(self, text="Сохранить параметры теста", command=self.save_test_params).pack(pady=5)

        tk.Label(self, text="Вопросы теста:", font=("Arial", 14)).pack(pady=(10, 2))
        self.questions_listbox = tk.Listbox(self)
        self.questions_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        actions = [
            ("Добавить вопрос", self.add_question),
            ("Просмотреть вопрос", lambda: self.show_question(view_only=True)),
            ("Редактировать вопрос", lambda: self.show_question(view_only=False)),
            ("Удалить вопрос", self.delete_question),
            ("Назад", self.go_back)
        ]
        for text, cmd in actions:
            tk.Button(self, text=text, command=cmd).pack(pady=3)

    def center_window(self, window=None):
        # Центрирование окна на экране
        window = window or self
        window.update_idletasks()
        w, h = window.winfo_width(), window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        window.geometry(f"+{x}+{y}")

    # === Загрузка и сохранение информации о тесте ===
    def load_test_info(self):
        # Загрузка информации о тесте (название, таймер, группы)
        theme = self.db.get_theme(self.test_id)
        if theme:
            self.name_var.set(theme["name"])
            if theme["timer_seconds"] is not None and theme["timer_seconds"] > 0:
                self.timer_var.set(str(theme["timer_seconds"] // 60))
                self.timer_check.set(0)
            else:
                self.timer_var.set("")
                self.timer_check.set(1)
        else:
            self.name_var.set("")
            self.timer_var.set("")
            self.timer_check.set(1)
        self.toggle_timer()

        test_groups = set(
            row["group_id"] for row in self.db._execute(
                "SELECT group_id FROM THEME_GROUP WHERE theme_id=?", (self.test_id,), fetch=True)
        )
        available_groups = self.db.get_available_groups_for_admin(self.current_user_id)
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        self.group_vars = []
        for group in available_groups:
            var = tk.BooleanVar(value=group["id"] in test_groups)
            cb = tk.Checkbutton(self.groups_frame, text=group["name"], variable=var)
            cb.pack(anchor="w")
            self.group_vars.append((var, group["id"]))

    def save_test_params(self):
        # Сохранение параметров теста (название, группы)
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Название теста не может быть пустым.", parent=self)
            return
        new_group_ids = [gid for var, gid in self.group_vars if var.get()]
        if not new_group_ids:
            messagebox.showerror("Ошибка", "Выберите хотя бы одну группу.", parent=self)
            return
        try:
            self.db._execute("UPDATE THEME SET name=? WHERE id=?", (name, self.test_id))
            self.db.update_test_groups(self.test_id, new_group_ids, self.current_user_id)
            messagebox.showinfo("Успешно", "Параметры теста успешно обновлены.", parent=self)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    # === Работа с таймером теста ===
    def toggle_timer(self):
        # Включение/отключение поля ввода таймера
        if self.timer_check.get():
            self.timer_entry.configure(state='disabled')
            self.timer_var.set("")
        else:
            self.timer_entry.configure(state='normal')

    def save_timer(self):
        # Сохранение значения таймера теста
        try:
            timer_seconds = None
            if not self.timer_check.get():
                mins = self.timer_var.get()
                if not mins.strip():
                    raise ValueError
                mins = int(mins)
                if mins <= 0:
                    raise ValueError
                timer_seconds = mins * 60
            self.db.update_test(self.test_id, self.db.get_test_name(self.test_id), timer_seconds)
            messagebox.showinfo("Успешно", "Таймер теста сохранён.", parent=self)
            self.load_test_info()
        except Exception:
            messagebox.showerror("Ошибка", "Введите корректное значение таймера (целое число минут > 0) либо уберите таймер.", parent=self)

    # === Работа с вопросами теста ===
    def load_questions(self):
        # Загрузка списка вопросов теста
        self.questions = self.db.get_questions(self.test_id)
        self.questions_listbox.delete(0, tk.END)
        for q in self.questions:
            self.questions_listbox.insert(tk.END, f"{q['theme_local_number']}: {q['text']}")

    def add_question(self):
        # Добавление нового вопроса в тест
        try:
            data = self.ask_question_data()
            if not data:
                return
            q_text, options, correct = data
            if any(q['text'].strip().lower() == q_text.strip().lower() for q in self.questions):
                messagebox.showerror("Ошибка", "Вопрос с таким текстом уже существует в этом тесте.", parent=self)
                return
            self.db.add_question(self.test_id, q_text, options, correct)
            self.load_questions()
            last_idx = len(self.questions)
            if last_idx > 0:
                self.questions_listbox.selection_clear(0, tk.END)
                self.questions_listbox.selection_set(last_idx - 1)
                self.questions_listbox.activate(last_idx - 1)
            messagebox.showinfo("Вопрос добавлен", f"Вопрос успешно добавлен:\n\n{q_text}", parent=self)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def show_question(self, view_only=True):
        # Просмотр или редактирование выбранного вопроса
        idx = self.get_selected_index("просмотра")
        if idx is None:
            return
        q = self.questions[idx]
        if view_only:
            self.show_question_window(q)
        else:
            data = self.ask_question_data(q["text"], q["options"], q.get("correct_options", []))
            if not data: return
            q_text, options, correct = data
            self.db.update_question(q["id"], q_text, options, correct)
            self.load_questions()
            messagebox.showinfo("Успешно", "Вопрос успешно обновлён.", parent=self)

    def delete_question(self):
        # Удаление выбранного вопроса из теста
        idx = self.get_selected_index("удаления")
        if idx is None:
            return
        q = self.questions[idx]
        if messagebox.askyesno("Удаление вопроса", f"Вы уверены, что хотите удалить вопрос №{q['theme_local_number']}?", parent=self):
            self.db.delete_question(q["id"])
            self.renumber_questions()
            self.load_questions()
            next_idx = min(idx, len(self.questions) - 1)
            if next_idx >= 0:
                self.questions_listbox.selection_clear(0, tk.END)
                self.questions_listbox.selection_set(next_idx)
                self.questions_listbox.activate(next_idx)
            messagebox.showinfo("Вопрос удалён", "Вопрос успешно удалён.", parent=self)

    def renumber_questions(self):
        # Перенумерация вопросов после удаления
        for idx, q in enumerate(self.db.get_questions(self.test_id)):
            if q['theme_local_number'] != idx+1:
                self.db.update_theme_local_number(q['id'], idx+1)

    def ask_question_data(self, default_text="", default_options=None, default_correct=None):
        # Диалог для ввода/редактирования данных вопроса
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

    # === Просмотр вопроса (отдельное окно) ===
    def show_question_window(self, q):
        # Окно просмотра вопроса с вариантами и правильными ответами
        win = tk.Toplevel(self)
        win.title("Просмотр вопроса")
        win.geometry("400x400")
        self.center_window(win)

        frame, canvas = self.create_scrollable_frame(win)
        all_dynamic_labels = []

        def update_wraplength_now(event=None):
            new_width = canvas.winfo_width() - 40
            for lbl in all_dynamic_labels:
                lbl.config(wraplength=new_width)

        def update_wraplength_delayed(event):
            nonlocal resize_after_id
            if resize_after_id:
                win.after_cancel(resize_after_id)
            resize_after_id = win.after(100, update_wraplength_now)

        resize_after_id = None
        win.bind("<Configure>", update_wraplength_delayed)

        q_label = tk.Label(
            frame, text=q['text'], font=("Arial", 14),
            background="#f0f0f0", justify="center", anchor="center", wraplength=360
        )
        q_label.grid(row=0, column=0, pady=(10, 5), sticky="n")
        all_dynamic_labels.append(q_label)

        opt_title = tk.Label(
            frame, text="Варианты ответов:", font=("Arial", 12),
            background="#f0f0f0", justify="center", anchor="center", wraplength=360
        )
        opt_title.grid(row=1, column=0, pady=(5, 5), sticky="n")
        all_dynamic_labels.append(opt_title)

        if q['options']:
            for i, opt in enumerate(q['options']):
                lbl = tk.Label(
                    frame, text=f"{i+1}. {opt}", font=("Arial", 12),
                    background="#f0f0f0", justify="left", anchor="w", wraplength=360
                )
                lbl.grid(row=2 + i, column=0, sticky="w", padx=20, pady=2)
                all_dynamic_labels.append(lbl)
            next_row = 2 + len(q['options'])
        else:
            no_opt = tk.Label(
                frame, text="Нет вариантов ответа", font=("Arial", 12),
                background="#f0f0f0", fg="red", justify="center", anchor="center", wraplength=360
            )
            no_opt.grid(row=2, column=0, sticky="n", pady=5)
            all_dynamic_labels.append(no_opt)
            next_row = 3

        corr_title = tk.Label(
            frame, text="Правильные ответы:", font=("Arial", 12),
            background="#f0f0f0", justify="center", anchor="center", wraplength=360
        )
        corr_title.grid(row=next_row, column=0, pady=(10, 5), sticky="n")
        all_dynamic_labels.append(corr_title)
        next_row += 1

        corr_indices = q.get('correct_options', [])
        corr_lbls = [
            tk.Label(
                frame, text=f"{i+1}. {q['options'][i]}", font=("Arial", 12), fg="green",
                background="#f0f0f0", justify="left", anchor="w", wraplength=360
            )
            for i in corr_indices if isinstance(i, int) and 0 <= i < len(q['options'])
        ]

        if corr_lbls:
            for lbl in corr_lbls:
                lbl.grid(row=next_row, column=0, sticky="w", padx=20, pady=2)
                all_dynamic_labels.append(lbl)
                next_row += 1
        else:
            no_corr = tk.Label(
                frame, text="Нет правильных ответов", font=("Arial", 12),
                background="#f0f0f0", fg="red", justify="center", anchor="center", wraplength=360
            )
            no_corr.grid(row=next_row, column=0, sticky="n", pady=5)
            all_dynamic_labels.append(no_corr)

        def force_initial_wrap():
            update_wraplength_now()

        win.after(100, force_initial_wrap)

    def create_scrollable_frame(self, win):
        # Создание прокручиваемого фрейма для окна просмотра вопроса
        container = tk.Frame(win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, background="#f0f0f0", highlightthickness=0)
        vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        outer_frame = tk.Frame(canvas, background="#f0f0f0")
        canvas.create_window((0, 0), window=outer_frame, anchor="n", tags="inner")

        scrollable_frame = tk.Frame(outer_frame, background="#f0f0f0")
        scrollable_frame.pack(anchor="n", pady=20)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        outer_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig("inner", width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)

        return scrollable_frame, canvas

    # === Вспомогательные методы ===
    def go_back(self):
        # Возврат к родительскому окну
        self.destroy()
        if self.parent:
            self.parent.deiconify()

    def open_input_dialog(self, title, prompt, default=""):
        # Открытие диалогового окна для ввода строки
        return simpledialog.askstring(title, prompt, initialvalue=default, parent=self)

    def get_selected_index(self, action="действия"):
        # Получение индекса выбранного вопроса в списке
        selection = self.questions_listbox.curselection()
        if not selection:
            messagebox.showinfo("Выбор вопроса", f"Выберите вопрос для {action}.", parent=self)
            return None
        return selection[0]