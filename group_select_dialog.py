import tkinter as tk

# =========================
# Класс диалога выбора групп
# =========================
class GroupSelectDialog(tk.Toplevel):

    # --- Инициализация и построение интерфейса ---
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
            self.listbox.insert(tk.END, group["name"])
        self.listbox.pack(padx=10, pady=8, fill=tk.BOTH, expand=True)

        btns = tk.Frame(self)
        btns.pack(pady=8)
        tk.Button(btns, text="OK", width=10, command=self.ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Отмена", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5)

        self.center_window()

    # --- Вспомогательные методы интерфейса ---
    def center_window(self):
        # Центрирует окно относительно родителя или экрана
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

    # --- Обработка событий пользователя ---
    def ok(self):
        # Сохраняет выбранные индексы и закрывает окно
        self.selected = list(self.listbox.curselection())
        self.destroy()

    def cancel(self):
        # Отменяет выбор и закрывает окно
        self.selected = []
        self.destroy()