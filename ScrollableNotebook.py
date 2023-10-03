import tkinter as tk
from tkinter import ttk


class ScrollableNotebook(ttk.Frame):
    def __init__(self, parent, wheelscroll=False, tabmenu=False, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.xLocation = 0
        self.notebook_content = ttk.Notebook(self, **kwargs)
        self.notebook_content.pack(fill="both", expand=True)
        self.notebook_tab = ttk.Notebook(self, **kwargs)
        self.notebook_tab.bind("<<NotebookTabChanged>>", self._tab_changer)
        if wheelscroll:
            self.notebook_tab.bind("<MouseWheel>", self._wheelscroll)
        slide_frame = ttk.Frame(self)
        slide_frame.place(relx=1.0, x=0, y=1, anchor=tk.NE)
        self.menu_space = 30
        if tabmenu:
            self.menu_space = 50
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
        self.notebook_content.bind("<Configure>", self._reset_slide)
        self.contents_managed = []

    def _wheelscroll(self, event):
        if event.delta > 0:
            self._left_slide(event)
        else:
            self._right_slide(event)

    def _bottom_menu(self, event):
        tab_list_menu = tk.Menu(self, tearoff=0)
        for tab in self.notebook_tab.tabs():
            tab_list_menu.add_command(label=self.notebook_tab.tab(tab, option="text"),
                                      command=lambda: self.select(tab))
        try:
            tab_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            tab_list_menu.grab_release()

    def _tab_changer(self, event):
        try:
            self.notebook_content.select(self.notebook_tab.index("current"))
        except:
            pass

    def _right_slide_start(self, event=None):
        if self._right_slide(event):
            self.timer = self.after(100, self._right_slide_start)

    def _right_slide(self, event):
        if self.notebook_tab.winfo_width() > self.notebook_content.winfo_width() - self.menu_space:
            if (self.notebook_content.winfo_width() - (
                    self.notebook_tab.winfo_width() + self.notebook_tab.winfo_x())) <= self.menu_space + 5:
                self.xLocation -= 20
                self.notebook_tab.place(x=self.xLocation, y=0)
                return True
        return False

    def _left_slide_start(self, event=None):
        if self._left_slide(event):
            self.timer = self.after(100, self._left_slide_start)

    def _left_slide(self, event):
        if not self.notebook_tab.winfo_x() == 0:
            self.xLocation += 20
            self.notebook_tab.place(x=self.xLocation, y=0)
            return True
        return False

    def _slide_stop(self, event):
        if getattr(self, 'timer', None) is not None:
            self.after_cancel(self.timer)
            self.timer = None

    def _reset_slide(self, event=None):
        self.notebook_tab.place(x=0, y=0)
        self.xLocation = 0

    def add(self, frame, **kwargs):
        if len(self.notebook_tab.winfo_children()) != 0:
            self.notebook_content.add(frame, text="", state="hidden")
        else:
            self.notebook_content.add(frame, text="")
        self.notebook_tab.add(ttk.Frame(self.notebook_tab), **kwargs)
        self.contents_managed.append(frame)

    def forget(self, tab_id):
        index = self.notebook_tab.index(tab_id)
        self.notebook_content.forget(self.__content_tab_id(tab_id))
        self.notebook_tab.forget(tab_id)
        self.contents_managed[index].destroy()
        self.contents_managed.pop(index)

    def hide(self, tab_id):
        self.notebook_content.hide(self.__content_tab_id(tab_id))
        self.notebook_tab.hide(tab_id)

    def identify(self, x, y):
        return self.notebook_tab.identify(x, y)

    def index(self, tab_id):
        return self.notebook_tab.index(tab_id)

    def __content_tab_id(self, tab_id):
        return self.notebook_content.tabs()[self.notebook_tab.tabs().index(tab_id)]

    def insert(self, pos, frame, **kwargs):
        self.notebook_content.insert(pos, frame, **kwargs)
        self.notebook_tab.insert(pos, frame, **kwargs)

    def select(self, tab_id):
        # self.notebook_content.select(self.__ContentTabID(tab_id))
        self.notebook_tab.select(tab_id)

    def tab(self, tab_id, option=None, **kwargs):
        kwargs_content = kwargs.copy()
        kwargs_content["text"] = ""  # important
        self.notebook_content.tab(self.__content_tab_id(tab_id), option=None, **kwargs_content)
        return self.notebook_tab.tab(tab_id, option=None, **kwargs)

    def tabs(self):
        # return self.notebook_content.tabs()
        return self.notebook_tab.tabs()

    def enable_traversal(self):
        self.notebook_content.enable_traversal()
        self.notebook_tab.enable_traversal()
