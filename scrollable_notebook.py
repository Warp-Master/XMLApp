import tkinter as tk
from tkinter import ttk


class ScrollableNotebook(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.notebook = ttk.Notebook(self.canvas)

        self.notebook.bind("<Configure>", self.on_configure)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.create_window((0, 0), window=self.notebook, anchor="nw")

    # Метод для обновления области прокрутки при изменении размера Notebook
    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Метод для добавления новой вкладки в ScrollableNotebook
    def add(self, tab, text):
        self.notebook.add(tab, text=text)


class VerticalScrollableNotebook(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.notebook = ttk.Notebook(self.canvas)

        self.notebook.bind("<Configure>", self.on_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.notebook, anchor="nw")

    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def add(self, tab, text):
        self.notebook.add(tab, text=text)
