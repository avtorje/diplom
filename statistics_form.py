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
        self.geometry("900x600")
        self.parent = parent

        self.create_widgets()
        self.load_groups()

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
        tk.Checkbutton(top, text="Только провалившие (<60%)", variable=self.failed_only_var, command=self.load_results).pack(side=tk.LEFT, padx=10)

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
            time_min = int(r["elapsed_seconds"]) // 60 if r["elapsed_seconds"] else ""
            percent = r["score"] if r["score"] is not None else 0
            mark = calc_mark(percent) if r["score"] is not None else ""
            status = "Пройден" if r["score"] is not None else "Не пройден"
            # Фильтрация по провалившим
            if self.failed_only_var.get() and percent >= 60:
                continue
            item = (name, date, time_min, f"{percent}%", mark, status)
            iid = self.tree.insert("", tk.END, values=item)
            # Подсветка низких баллов
            if r["score"] is not None and percent < 60:
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
