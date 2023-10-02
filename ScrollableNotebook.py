import tkinter as tk
from tkinter import ttk


class ScrollableNotebook(ttk.Frame):
    def __init__(self, parent, wheelscroll=False, tabmenu=False, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.xLocation = 0
        self.notebookContent = ttk.Notebook(self, **kwargs)
        self.notebookContent.pack(fill="both", expand=True)
        self.notebookTab = ttk.Notebook(self, **kwargs)
        self.notebookTab.bind("<<NotebookTabChanged>>", self._tab_changer)
        if wheelscroll:
            self.notebookTab.bind("<MouseWheel>", self._wheelscroll)
        slide_frame = ttk.Frame(self)
        slide_frame.place(relx=1.0, x=0, y=1, anchor=tk.NE)
        self.menuSpace = 30
        if tabmenu:
            self.menuSpace = 50
            bottom_tab = ttk.Label(slide_frame, text="\u2630")
            bottom_tab.bind("<ButtonPress-1>", self._bottom_menu)
            bottom_tab.pack(side=tk.RIGHT)
        left_arrow = ttk.Label(slide_frame, text=" \u276E")
        left_arrow.bind("<ButtonPress-1>", self._left_slide_start)
        left_arrow.bind("<ButtonRelease-1>", self._slide_stop)
        left_arrow.pack(side=tk.LEFT)
        right_arrow = ttk.Label(slide_frame, text=" \u276F")
        right_arrow.bind("<ButtonPress-1>", self._right_slide_start)
        right_arrow.bind("<ButtonRelease-1>", self._slide_stop)
        right_arrow.pack(side=tk.RIGHT)
        self.notebookContent.bind("<Configure>", self._reset_slide)
        self.contentsManaged = []

    def _wheelscroll(self, event):
        if event.delta > 0:
            self._left_slide(event)
        else:
            self._right_slide(event)

    def _bottom_menu(self, event):
        tab_list_menu = tk.Menu(self, tearoff=0)
        for tab in self.notebookTab.tabs():
            tab_list_menu.add_command(label=self.notebookTab.tab(tab, option="text"),
                                      command=lambda: self.select(tab))
        try:
            tab_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            tab_list_menu.grab_release()

    def _tab_changer(self, event):
        try:
            self.notebookContent.select(self.notebookTab.index("current"))
        except:
            pass

    def _right_slide_start(self, event=None):
        if self._right_slide(event):
            self.timer = self.after(100, self._right_slide_start)

    def _right_slide(self, event):
        if self.notebookTab.winfo_width() > self.notebookContent.winfo_width() - self.menuSpace:
            if (self.notebookContent.winfo_width() - (
                    self.notebookTab.winfo_width() + self.notebookTab.winfo_x())) <= self.menuSpace + 5:
                self.xLocation -= 20
                self.notebookTab.place(x=self.xLocation, y=0)
                return True
        return False

    def _left_slide_start(self, event=None):
        if self._left_slide(event):
            self.timer = self.after(100, self._left_slide_start)

    def _left_slide(self, event):
        if not self.notebookTab.winfo_x() == 0:
            self.xLocation += 20
            self.notebookTab.place(x=self.xLocation, y=0)
            return True
        return False

    def _slide_stop(self, event):
        if getattr(self, 'timer', None) is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def _reset_slide(self, event=None):
        self.notebookTab.place(x=0, y=0)
        self.xLocation = 0

    def add(self, frame, **kwargs):
        if len(self.notebookTab.winfo_children()) != 0:
            self.notebookContent.add(frame, text="", state="hidden")
        else:
            self.notebookContent.add(frame, text="")
        self.notebookTab.add(ttk.Frame(self.notebookTab), **kwargs)
        self.contentsManaged.append(frame)

    def forget(self, tab_id):
        index = self.notebookTab.index(tab_id)
        self.notebookContent.forget(self.__content_tab_id(tab_id))
        self.notebookTab.forget(tab_id)
        self.contentsManaged[index].destroy()
        self.contentsManaged.pop(index)

    def hide(self, tab_id):
        self.notebookContent.hide(self.__content_tab_id(tab_id))
        self.notebookTab.hide(tab_id)

    def identify(self, x, y):
        return self.notebookTab.identify(x, y)

    def index(self, tab_id):
        return self.notebookTab.index(tab_id)

    def __content_tab_id(self, tab_id):
        return self.notebookContent.tabs()[self.notebookTab.tabs().index(tab_id)]

    def insert(self, pos, frame, **kwargs):
        self.notebookContent.insert(pos, frame, **kwargs)
        self.notebookTab.insert(pos, frame, **kwargs)

    def select(self, tab_id):
        # self.notebookContent.select(self.__ContentTabID(tab_id))
        self.notebookTab.select(tab_id)

    def tab(self, tab_id, option=None, **kwargs):
        kwargs_content = kwargs.copy()
        kwargs_content["text"] = ""  # important
        self.notebookContent.tab(self.__content_tab_id(tab_id), option=None, **kwargs_content)
        return self.notebookTab.tab(tab_id, option=None, **kwargs)

    def tabs(self):
        # return self.notebookContent.tabs()
        return self.notebookTab.tabs()

    def enable_traversal(self):
        self.notebookContent.enable_traversal()
        self.notebookTab.enable_traversal()
