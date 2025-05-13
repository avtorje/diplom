import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from edit_test_form import EditTestForm


class ManageTestsForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление тестами")
        self.geometry("400x300")  # Установить размеры окна
        self.center_window()  # Вызвать метод центрирования окна
        self.parent = parent
        self.create_widgets()
        self.load_tests()

    def create_widgets(self):
        tk.Label(self, text="Управление тестами", font=("Arial", 16)).pack(pady=10)

        self.tests_listbox = tk.Listbox(self)
        self.tests_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Button(self, text="Добавить тест", command=self.add_test).pack(pady=5)
        tk.Button(self, text="Редактировать тест", command=self.edit_test).pack(pady=5)
        tk.Button(self, text="Удалить тест", command=self.delete_test).pack(pady=5)
        tk.Button(self, text="Назад", command=self.go_back).pack(pady=5)

    def load_tests(self):
        self.tests_listbox.delete(0, tk.END)
        tests = self.db.get_all_tests()
        for test in tests:
            self.tests_listbox.insert(tk.END, f"{test[0]}: {test[1]}")

    def add_test(self):
        test_name = simpledialog.askstring("Добавить тест", "Введите название нового теста:")
        if test_name:
            try:
                self.db.add_test(test_name)
                self.load_tests()
                messagebox.showinfo("Успешно", f"Тест '{test_name}' успешно добавлен.")
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

    def edit_test(self):
        selected = self.tests_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тест для редактирования.")
            return

        test_id = int(self.tests_listbox.get(selected[0]).split(":")[0])
        self.withdraw()
        EditTestForm(self, test_id).mainloop()

    def delete_test(self):
        selected = self.tests_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите тест для удаления.")
            return

        test_id = int(self.tests_listbox.get(selected[0]).split(":")[0])
        if messagebox.askyesno("Удалить тест", "Вы уверены, что хотите удалить этот тест?"):
            self.db.delete_test(test_id)
            self.load_tests()

    def go_back(self):
        self.destroy()
        self.parent.deiconify()

    def center_window(self):
        """Центрирует окно на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")