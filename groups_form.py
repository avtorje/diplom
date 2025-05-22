import tkinter as tk
from tkinter import simpledialog, messagebox
from database import Database

class GroupsForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление группами")
        self.geometry("400x300")
        self.parent = parent
        self.create_widgets()
        self.load_groups()

    def create_widgets(self):
        tk.Label(self, text="Список групп", font=("Arial", 14)).pack(pady=10)
        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Button(self, text="Добавить группу", command=self.add_group).pack(pady=5)
        tk.Button(self, text="Редактировать группу", command=self.edit_group).pack(pady=5)
        tk.Button(self, text="Удалить группу", command=self.delete_group).pack(pady=5)

    def load_groups(self):
        self.groups_listbox.delete(0, tk.END)
        groups = self.db.get_groups()
        for group in groups:
            self.groups_listbox.insert(tk.END, f"{group[0]}: {group[1]}")

    def add_group(self):
        name = simpledialog.askstring("Имя группы", "Введите название группы:", parent=self)
        code = simpledialog.askstring("Код группы", "Введите код группы:", parent=self)
        if name and code:
            try:
                self.db.add_group(name, code)
                self.load_groups()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def edit_group(self):
        selected = self.groups_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите группу для редактирования.")
            return
        group_id = int(self.groups_listbox.get(selected[0]).split(":")[0])
        name = simpledialog.askstring("Имя группы", "Новое название:", parent=self)
        code = simpledialog.askstring("Код группы", "Новый код:", parent=self)
        if name and code:
            self.db.edit_group(group_id, name, code)
            self.load_groups()

    def delete_group(self):
        selected = self.groups_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите группу для удаления.")
            return
        group_id = int(self.groups_listbox.get(selected[0]).split(":")[0])
        if messagebox.askyesno("Удалить группу", "Вы уверены?"):
            self.db.delete_group(group_id)
            self.load_groups()