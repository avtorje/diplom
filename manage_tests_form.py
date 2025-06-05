import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from edit_test_form import EditTestForm

class ManageTestsForm(tk.Toplevel):
    def __init__(self, parent, current_user_id):
        super().__init__(parent)
        self.db = Database()
        self.parent = parent
        self.current_user_id = current_user_id
        self.groups = self.db.get_available_groups_for_admin(self.current_user_id)
        if not self.groups:
            messagebox.showerror("Ошибка", "Нет доступных групп для управления тестами.")
            self.destroy()
            return
        self.selected_group_idx = 0
        self.title("Управление тестами")
        self.geometry("500x450")
        self.center_window()
        self.create_widgets()
        self.load_tests_for_selected_group()

    def create_widgets(self):
        # Вкладки групп сверху
        self.tabs_frame = tk.Frame(self)
        self.tabs_frame.pack(fill=tk.X, pady=5)
        self.tab_buttons = []
        for idx, group in enumerate(self.groups):
            btn = tk.Button(self.tabs_frame, text=group["name"], relief="raised",
                            command=lambda i=idx: self.on_group_tab(i))
            btn.pack(side=tk.LEFT, padx=3)
            self.tab_buttons.append(btn)
        self.update_tab_highlight()

        # Список тестов
        self.tests_listbox = tk.Listbox(self)
        self.tests_listbox.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        # Кнопки управления
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Добавить тест", command=self.add_test).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать тест", command=self.edit_test).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить тест", command=self.delete_test).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Назад", command=self.go_back).pack(side=tk.RIGHT, padx=5)

    def on_group_tab(self, idx):
        self.selected_group_idx = idx
        self.update_tab_highlight()
        self.load_tests_for_selected_group()

    def update_tab_highlight(self):
        for i, btn in enumerate(self.tab_buttons):
            btn.config(relief="sunken" if i == self.selected_group_idx else "raised")

    def load_tests_for_selected_group(self):
        self.tests_listbox.delete(0, tk.END)
        group_id = self.groups[self.selected_group_idx]["id"]
        self.current_tests = self.db.get_tests_for_group(group_id)
        for idx, test in enumerate(self.current_tests, 1):
            timer = test.get("timer_seconds")
            timer_str = f" (Время: {timer // 60} мин)" if timer and timer > 0 else ""
            self.tests_listbox.insert(tk.END, f"{idx}. {test['name']}{timer_str}")

    def get_selected_test(self):
        selected = self.tests_listbox.curselection()
        return self.current_tests[selected[0]] if selected else None

    def add_test(self):
        test_name = simpledialog.askstring("Добавить тест", "Введите название нового теста:")
        if not test_name:
            return
        timer = simpledialog.askinteger("Время", "Введите время (минуты), 0 или пусто — без ограничения:", minvalue=0)
        timer_seconds = None if not timer else timer * 60

        # Можно выбрать сразу несколько групп, но только из доступных
        from group_select_dialog import GroupSelectDialog
        groups = self.db.get_available_groups_for_admin(self.current_user_id)
        dlg = GroupSelectDialog(self, groups)
        self.wait_window(dlg)
        if not dlg.selected:
            messagebox.showwarning("Внимание", "Не выбраны группы. Тест не будет создан.")
            return
        group_ids = [groups[i]["id"] for i in dlg.selected]
        try:
            test_id = self.db.add_test_with_groups(test_name, self.current_user_id, group_ids, timer_seconds)
            self.load_tests_for_selected_group()
            messagebox.showinfo("Успешно", f"Тест '{test_name}' успешно добавлен для выбранных групп.")
            # Открыть форму редактирования (добавления вопросов)
            self.withdraw()
            EditTestForm(self, test_id, self.current_user_id).mainloop()
            self.deiconify()
            self.load_tests_for_selected_group()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_test(self):
        test = self.get_selected_test()
        if not test:
            messagebox.showerror("Ошибка", "Выберите тест для редактирования.")
            return
        # EditTestForm должен позволять изменять группы назначения и время, с учётом ограничений!
        self.withdraw()
        EditTestForm(self, test["id"], self.current_user_id).mainloop()
        self.deiconify()
        self.load_tests_for_selected_group()

    def delete_test(self):
        test = self.get_selected_test()
        if not test:
            messagebox.showerror("Ошибка", "Выберите тест для удаления.")
            return
        group_id = self.groups[self.selected_group_idx]["id"]
        if messagebox.askyesno("Удалить тест", "Удалить этот тест только из выбранной группы? (Если тест не назначен ни в одну группу, он будет удалён полностью)"):
            try:
                self.db.remove_test_from_group(test["id"], group_id, self.current_user_id)
                self.load_tests_for_selected_group()
            except PermissionError as e:
                messagebox.showerror("Ошибка", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить тест: {e}")

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")