import tkinter as tk

class GroupSelectDialog(tk.Toplevel):
    def __init__(self, parent, groups):
        super().__init__(parent)
        self.title("Выбор групп")
        self.selected = []
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        tk.Label(self, text="Выберите группы для теста:").pack(pady=8)
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        for group in groups:
            self.listbox.insert(tk.END, group["name"])  # заменено group[1] -> group["name"]
        self.listbox.pack(padx=10, pady=8, fill=tk.BOTH, expand=True)

        btns = tk.Frame(self)
        btns.pack(pady=8)
        tk.Button(btns, text="OK", width=10, command=self.ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Отмена", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5)

        self.center_window()  # Центрирование окна

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if self.master:
            x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (w // 2)
            y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (h // 2)
        else:
            x = (self.winfo_screenwidth() // 2) - (w // 2)
            y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def ok(self):
        self.selected = list(self.listbox.curselection())
        self.destroy()

    def cancel(self):
        self.selected = []
        self.destroy()