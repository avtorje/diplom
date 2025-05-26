import tkinter as tk
from tkinter import simpledialog, messagebox
from database import Database
from group_users_form import GroupUsersForm

class GroupsForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление группами")
        self.center_window(400, 400)
        self.parent = parent
        self.create_widgets()
        self.load_groups()

    def center_window(self, width=400, height=400):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        tk.Label(self, text="Список групп", font=("Arial", 14)).pack(pady=10)
        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.groups_listbox.bind("<<ListboxSelect>>", self.open_group_users)
        btns = [
            ("Добавить группу", self.add_or_edit_group),
            ("Редактировать группу", lambda: self.add_or_edit_group(edit=True)),
            ("Удалить группу", self.delete_group),
            ("Закрыть", self.destroy)
        ]
        for text, cmd in btns:
            tk.Button(self, text=text, command=cmd).pack(pady=5)

    def load_groups(self):
        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for group in self.groups:
            self.groups_listbox.insert(tk.END, f"{group[0]}: {group[1]}")

    def get_selected_group_id(self):
        idx = self.groups_listbox.curselection()
        if not idx:
            return None
        return self.groups[idx[0]][0]

    def open_group_users(self, event):
        group_id = self.get_selected_group_id()
        if group_id:
            GroupUsersForm(self, group_id)

    def add_or_edit_group(self, edit=False):
        group_id = self.get_selected_group_id() if edit else None
        if edit and not group_id:
            messagebox.showerror("Ошибка", "Выберите группу для редактирования.")
            return
        name = simpledialog.askstring("Имя группы", "Введите название группы:", parent=self)
        code = simpledialog.askstring("Код группы", "Введите код группы:", parent=self)
        if name and code:
            try:
                if edit:
                    self.db.edit_group(group_id, name, code)
                else:
                    self.db.add_group(name, code)
                self.load_groups()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_group(self):
        group_id = self.get_selected_group_id()
        if not group_id:
            messagebox.showerror("Ошибка", "Выберите группу для удаления.")
            return
        if messagebox.askyesno("Удалить группу", "Вы уверены?"):
            self.db.delete_group(group_id)
            self.load_groups()