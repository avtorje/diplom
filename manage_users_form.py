import tkinter as tk
from tkinter import messagebox
from database import Database
from group_users_form import GroupUsersForm

class ManageUsersForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.title("Управление пользователями")
        self.center_window(500, 500)
        self.parent = parent
        self.create_widgets()
        self.load_users()

    def center_window(self, width=500, height=500):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        tk.Label(self, text="Главный администратор", font=("Arial", 14, "bold")).pack(pady=5)
        self.main_admin_listbox = tk.Listbox(self, height=1)
        self.main_admin_listbox.pack(fill=tk.X, pady=2)

        tk.Label(self, text="Управление по группам", font=("Arial", 14)).pack(pady=5)
        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.groups_listbox.bind("<<ListboxSelect>>", self.on_group_select)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Управление группами", command=self.open_groups_form).pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Назад", command=self.go_back).pack(pady=5, fill=tk.X)

    def load_users(self):
        self.main_admin_listbox.delete(0, tk.END)
        main_admin = self.db.get_main_admin()
        if main_admin:
            self.main_admin_listbox.insert(tk.END, f"{main_admin[1]} (Главный админ)")

        self.groups_listbox.delete(0, tk.END)
        self.groups = self.db.get_groups()
        for group in self.groups:
            self.groups_listbox.insert(tk.END, f"{group[0]}: {group[1]}")
        if self.groups:
            self.groups_listbox.select_set(0)
            self.on_group_select(None)

    def on_group_select(self, event=None):
        selection = self.groups_listbox.curselection()
        if not selection:
            return
        group_id = self.groups[selection[0]][0]
        GroupUsersForm(self, group_id)

    def open_groups_form(self):
        from groups_form import GroupsForm
        GroupsForm(self)

    def go_back(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()
