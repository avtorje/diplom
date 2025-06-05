import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database

def calc_mark(score):
    if score is None:
        return ""
    if score >= 90:
        return 5
    elif score >= 70:
        return 4
    elif score >= 50:
        return 3
    elif score >= 30:
        return 2
    else:
        return 1

class StatisticsForm(tk.Toplevel):
    def __init__(self, parent, admin_id):
        super().__init__(parent)
        self.db = Database()
        self.admin_id = admin_id
        self.title("Статистика")
        self.geometry("1000x600")
        self.parent = parent

        self.center_window()  # Центрирование окна

        self.create_widgets()
        self.load_groups()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 and height == 1:
            width = 1000
            height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top, text="Группа:").pack(side=tk.LEFT)
        self.group_cb = ttk.Combobox(top, state="readonly", width=25)
        self.group_cb.pack(side=tk.LEFT, padx=5)
        self.group_cb.bind("<<ComboboxSelected>>", self.on_group_selected)

        tk.Label(top, text="Тест:").pack(side=tk.LEFT, padx=(20, 0))
        self.test_cb = ttk.Combobox(top, state="readonly", width=30)
        self.test_cb.pack(side=tk.LEFT, padx=5)
        self.test_cb.bind("<<ComboboxSelected>>", self.on_test_selected)

        tk.Label(top, text="Поиск студента:").pack(side=tk.LEFT, padx=(20, 0))
        self.search_entry = tk.Entry(top, width=18)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.load_results())

        self.failed_only_var = tk.IntVar()
        tk.Checkbutton(top, text="Только провалившие (<50%)", variable=self.failed_only_var, command=self.load_results).pack(side=tk.LEFT, padx=10)

        # Режим
        self.mode_var = tk.StringVar(value="single")
        mode_frame = tk.Frame(self)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(mode_frame, text="Режим:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="По одному тесту", variable=self.mode_var, value="single", command=self.on_mode_change).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="По всем тестам", variable=self.mode_var, value="all", command=self.on_mode_change).pack(side=tk.LEFT)

        # Таблица
        columns = ("student", "date", "time", "percent", "mark", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, txt in zip(columns, ["Студент", "Дата", "Время (мин)", "Процент", "Оценка", "Статус"]):
            self.tree.heading(col, text=txt)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # Сводная информация
        self.summary_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.summary_label.pack(pady=5)

        # Кнопки
        btns = tk.Frame(self)
        btns.pack(fill=tk.X, pady=8)
        tk.Button(btns, text="Обновить", command=self.load_results).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Экспорт в Excel", command=self.export_excel).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text="Назад", command=self.go_back).pack(side=tk.RIGHT, padx=10)

    def load_groups(self):
        self.groups = self.db.get_teacher_groups(self.admin_id)
        self.group_cb["values"] = [g["name"] for g in self.groups]
        if self.groups:
            self.group_cb.current(0)
            self.on_group_selected()

    def on_group_selected(self, event=None):
        idx = self.group_cb.current()
        if idx < 0:
            self.test_cb["values"] = []
            return
        group_id = self.groups[idx]["id"]
        self.tests = self.db.get_teacher_tests_for_group(self.admin_id, group_id)
        self.test_cb["values"] = [t["name"] for t in self.tests]
        if self.tests:
            self.test_cb.current(0)
        self.load_results()

    def on_test_selected(self, event=None):
        self.load_results()

    def load_results(self):
        self.tree.delete(*self.tree.get_children())
        group_idx = self.group_cb.current()
        test_idx = self.test_cb.current()
        if group_idx < 0 or test_idx < 0:
            return
        group_id = self.groups[group_idx]["id"]
        test_id = self.tests[test_idx]["id"]
        search = self.search_entry.get().strip()
        rows = self.db.get_test_results_for_group(group_id, test_id, search_student=search)
        stats = []
        for r in rows:
            name = f"{r['last_name']} {r['first_name']}"
            date = r["date"][:10] if r["date"] else ""
            if r["elapsed_seconds"]:
                minutes = int(r["elapsed_seconds"]) // 60
                seconds = int(r["elapsed_seconds"]) % 60
                time_str = f"{minutes}:{seconds:02d}"
            else:
                time_str = ""
            percent = r["score"] if r["score"] is not None else 0
            mark = calc_mark(percent) if r["score"] is not None else ""
            status = "Пройден" if r["score"] is not None else "Не пройден"
            # Фильтрация по провалившим
            if self.failed_only_var.get() and percent >= 50:
                continue
            item = (name, date, time_str, f"{percent}%", mark, status)
            iid = self.tree.insert("", tk.END, values=item)
            # Подсветка низких баллов
            if r["score"] is not None and percent < 50:
                self.tree.item(iid, tags=("fail",))
            stats.append((percent, mark, status))
        self.tree.tag_configure("fail", background="#ffcccc")
        self.update_summary(stats, len(rows))

    def update_summary(self, stats, total):
        if not stats:
            self.summary_label.config(text="Нет данных")
            return
        marks = [m for _, m, s in stats if m != ""]
        percents = [p for p, _, s in stats if p is not None]
        passed = sum(1 for _, _, s in stats if s == "Пройден")
        failed = total - passed
        avg = round(sum(marks) / len(marks), 2) if marks else 0
        min_p = min(percents) if percents else 0
        max_p = max(percents) if percents else 0
        self.summary_label.config(
            text=f"Средний балл: {avg} | Прошли: {passed} из {total} | Мин. результат: {min_p}% | Макс.: {max_p}%"
        )

    def export_excel(self):
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Ошибка", "Для экспорта нужен пакет pandas.")
            return
        rows = [self.tree.item(i)["values"] for i in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Нет данных", "Нет данных для экспорта.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not file:
            return
        df = pd.DataFrame(rows, columns=["Студент", "Дата", "Время (мин)", "Процент", "Оценка", "Статус"])
        df.to_excel(file, index=False)
        messagebox.showinfo("Успех", "Данные экспортированы в Excel.")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

    def on_row_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item[0])["values"]
        student_name = values[0]
        # Здесь можно реализовать подробности ответа студента (например, открыть отдельное окно)
        messagebox.showinfo("Подробности", f"Подробности по студенту: {student_name}")

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "single":
            self.test_cb.config(state="readonly")
            self.tree["columns"] = ("student", "date", "time", "percent", "mark", "status")
            for col, txt in zip(self.tree["columns"], ["Студент", "Дата", "Время (мин)", "Процент", "Оценка", "Статус"]):
                self.tree.heading(col, text=txt)
                self.tree.column(col, anchor="center", width=120)
            self.load_results()
        else:
            self.test_cb.config(state="disabled")
            self.build_summary_table()

    def build_summary_table(self):
        self.tree.delete(*self.tree.get_children())
        group_idx = self.group_cb.current()
        if group_idx < 0:
            return
        group_id = self.groups[group_idx]["id"]
        students = self.db.get_students_by_group(group_id)
        tests = self.db.get_teacher_tests_for_group(self.admin_id, group_id)
        test_ids = [t["id"] for t in tests]
        test_names = [t["name"] for t in tests]
        # Получаем все результаты по группе и тестам
        results = self.db.fetch_all(
            "SELECT user_id, theme_id, score FROM TEST_SUMMARY WHERE theme_id IN ({})".format(
                ",".join("?" * len(test_ids))
            ), tuple(test_ids)
        ) if test_ids else []
        res_map = {(r["user_id"], r["theme_id"]): r["score"] for r in results}
        # Формируем столбцы
        columns = ["student"] + test_names + ["avg_percent", "avg_mark"]
        self.tree["columns"] = columns
        for col in columns:
            if col == "student":
                self.tree.heading(col, text="Студент")
                self.tree.column(col, anchor="center", width=140)
            elif col == "avg_percent":
                self.tree.heading(col, text="Средний %")
                self.tree.column(col, anchor="center", width=100)
            elif col == "avg_mark":
                self.tree.heading(col, text="Ср. оценка")
                self.tree.column(col, anchor="center", width=100)
            else:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)
        # Заполняем строки
        for s in students:
            row = [f"{s['last_name']} {s['first_name'][0]}"]
            scores = []
            marks = []
            for t in tests:
                score = res_map.get((s["id"], t["id"]))
                if score is not None:
                    row.append(f"{score}%")
                    scores.append(score)
                    marks.append(calc_mark(score))
                else:
                    row.append("—")
            avg_percent = round(sum(scores)/len(scores), 1) if scores else "—"
            avg_mark = round(sum(marks)/len(marks), 1) if marks else "—"
            row += [avg_percent, avg_mark]
            self.tree.insert("", tk.END, values=row)
        self.summary_label.config(text=f"Сводная таблица: {len(students)} студентов, {len(tests)} тестов")
