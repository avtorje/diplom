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
        self.geometry("500x400")
        self.parent = parent

        if not self.questions:
            messagebox.showinfo("Нет вопросов", "В этом тесте нет вопросов.")
            self.destroy()
            return

        self.selected_option = tk.IntVar(value=-1)
        self.all_dynamic_labels = []
        self.create_widgets()
        self.center_window()
        self.after(100, self.load_question)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            width, height = 500, 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Scrollable area setup
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, background="#f0f0f0", highlightthickness=0)
        self.vscroll = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Вложенный контейнер для скролла
        self.outer_frame = tk.Frame(self.canvas, background="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.outer_frame, anchor="n", tags="inner")

        self.scrollable_frame = tk.Frame(self.outer_frame, background="#f0f0f0")
        self.scrollable_frame.pack(anchor="n", pady=20)

        # Привязка прокрутки
        self.outer_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("inner", width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Кнопка "Следующий"/"Завершить тест" всегда видна внизу
        self.next_button = tk.Button(self, text="Следующий", command=self.next_question)
        self.next_button.pack(pady=10, side="bottom")

        # Для wraplength
        self.resize_after_id = None
        self.bind("<Configure>", self.update_wraplength_delayed)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_wraplength_now(self, event=None):
        new_width = self.canvas.winfo_width()
        if new_width <= 1:
            self.after(100, self.update_wraplength_now)
            return
        new_width -= 40
        for lbl in self.all_dynamic_labels:
            lbl.config(wraplength=new_width)


    def update_wraplength_delayed(self, event):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        self.resize_after_id = self.after(100, self.update_wraplength_now)

    def load_question(self):
        # Очистить старое
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        self.all_dynamic_labels = []

        q = self.questions[self.current_question_index]

        # ВОПРОС по центру
        q_label = tk.Label(
            self.scrollable_frame,
            text=q['text'],
            font=("Arial", 14),
            background="#f0f0f0",
            wraplength=420,
            anchor="center",
            justify="left"  # или убери justify вовсе
        )

        q_label.pack(pady=(10, 10), padx=10, anchor="center")
        self.all_dynamic_labels.append(q_label)

        # ОТВЕТЫ по левому краю с отступом 20px
        self.selected_option.set(-1)
        self.radio_buttons = []
        for idx, option in enumerate(q["options"]):
            rb_frame = tk.Frame(self.scrollable_frame, background="#f0f0f0")
            rb_frame.pack(anchor="w", fill="x", padx=(20, 0), pady=2)
            rb = tk.Radiobutton(
                rb_frame,
                text=option,
                variable=self.selected_option,
                value=idx,
                font=("Arial", 12),
                anchor="w",
                wraplength=400,
                justify="left",
                background="#f0f0f0"
            )
            rb.pack(anchor="w", fill="x")
            self.radio_buttons.append(rb)
            self.all_dynamic_labels.append(rb)

        # Переключение между "Следующий" и "Завершить тест"
        if self.current_question_index == len(self.questions) - 1:
            self.next_button.config(text="Завершить тест", command=self.finish_test)
        else:
            self.next_button.config(text="Следующий", command=self.next_question)

        # 💡 ДОБАВЛЕНО — обновляем wraplength явно
        self.update_wraplength_now()



    def next_question(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
            return
        self.answers.append(sel)
        self.current_question_index += 1
        self.after(100, self.load_question)

    def finish_test(self):
        sel = self.selected_option.get()
        if sel == -1:
            messagebox.showwarning("Нет ответа", "Пожалуйста, выберите вариант ответа.", parent=self)
            return
        self.answers.append(sel)
        score = sum(
            ans == q["correct_options"]
            for ans, q in zip(self.answers, self.questions)
        )
        self.db.save_test_results(self.user_id, self.test_id, self.questions, self.answers, score)
        messagebox.showinfo("Тест завершён", f"Ваш результат: {score} из {len(self.questions)}.", parent=self)
        self.destroy()
        self.parent.deiconify()