import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from edit_test_form import EditTestForm
from group_select_dialog import GroupSelectDialog

class ManageTestsForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.parent = parent
        self.title("Управление тестами")
        self.geometry("400x400")
        self.center_window()
        self.create_widgets()
        self.load_tests()

    def create_widgets(self):
        tk.Label(self, text="Управление тестами", font=("Arial", 16)).pack(pady=10)
        self.tests_listbox = tk.Listbox(self)
        self.tests_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        buttons = [
            ("Добавить тест", self.add_test),
            ("Редактировать тест", lambda: self.modify_test(EditTestForm)),
            ("Удалить тест", self.delete_test),
            ("Назад", self.go_back)
        ]
        for text, cmd in buttons:
            tk.Button(self, text=text, command=cmd).pack(pady=5)

    def load_tests(self):
        self.tests_listbox.delete(0, tk.END)
        self.tests = self.db.get_all_tests()
        for idx, (test_id, name, *rest) in enumerate(self.tests, 1):
            # rest может содержать timer_seconds, если get_all_tests возвращает это поле
            timer = rest[0] if rest else None
            timer_str = f" (таймер: {timer//60} мин)" if timer and timer > 0 else ""
            self.tests_listbox.insert(tk.END, f"{idx}. {name}{timer_str}")

    def get_selected_test_id(self):
        selected = self.tests_listbox.curselection()
        return self.tests[selected[0]][0] if selected else None

    def add_test(self):
        test_name = simpledialog.askstring("Добавить тест", "Введите название нового теста:")
        if not test_name:
            return

        groups = self.db.get_groups()
        if not groups:
            messagebox.showerror("Ошибка", "Нет доступных групп.")
            return

        dlg = GroupSelectDialog(self, groups)
        self.wait_window(dlg)
        if not dlg.selected:
            messagebox.showwarning("Внимание", "Не выбраны группы. Тест не будет создан.")
            return

        group_ids = [groups[i][0] for i in dlg.selected]

        try:
            # Добавляем тест без таймера по умолчанию
            test_id = self.db.add_test(test_name, timer_seconds=None)
            self.db.add_test_groups(test_id, group_ids)
            self.load_tests()
            messagebox.showinfo("Успешно", f"Тест '{test_name}' успешно добавлен для выбранных групп.")

            # Открыть окно редактирования теста (добавления вопросов и настройки таймера)
            self.withdraw()  # скрыть главное окно, если нужно
            EditTestForm(self, test_id).mainloop()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def modify_test(self, form_class):
        test_id = self.get_selected_test_id()
        if not test_id:
            messagebox.showerror("Ошибка", "Выберите тест для редактирования.")
            return
        self.withdraw()
        form_class(self, test_id).mainloop()

    def delete_test(self):
        test_id = self.get_selected_test_id()
        if not test_id:
            messagebox.showerror("Ошибка", "Выберите тест для удаления.")
            return
        if messagebox.askyesno("Удалить тест", "Вы уверены, что хотите удалить этот тест?"):
            self.db.delete_test(test_id)
            self.load_tests()

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