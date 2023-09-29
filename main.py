import os
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, simpledialog

from ttkthemes import ThemedTk

from switch import Switch
from scrollable_notebook import ScrollableNotebook


class StartFrame(ttk.Frame):
    def __init__(self, container, controller, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.controller = controller

        # Левая часть
        self.switch_frame = ttk.Frame(self)
        self.switch_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        self.switch = Switch(self.switch_frame)
        self.switch.grid(row=0, column=0, padx=5, pady=5)

        self.switch_label = ttk.Label(self.switch_frame, text="Выбрать другую директорию")
        self.switch_label.grid(row=0, column=1, padx=5, pady=5)
        self.switch.bind('<<SwitchToggled>>', lambda e: self.toggle_dir_choice())

        self.dir_entry = ttk.Entry(self, state='disabled')
        self.dir_entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.dir_button = ttk.Button(self, text="Выбрать папку", command=self.choose_directory, state='disabled')
        self.dir_button.grid(row=2, column=0, padx=5, pady=5)

        self.file_listbox = tk.Listbox(self, width=25)
        self.file_listbox.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Button(self, text="Start", command=self.start).grid(row=4, column=0, padx=5, pady=5)

        self.theme_combobox = ttk.Combobox(self, values=self.controller.available_themes)
        if self.controller.available_themes:
            self.theme_combobox.set(self.controller.available_themes[0])
        self.theme_combobox.grid(row=4, column=1, padx=65, pady=5, ipady=2, rowspan=4, sticky='w')

        self.apply_button = ttk.Button(self, text="Применить", command=self.apply_theme)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='e')

        self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

        # Конфигурация grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def generate_tex(self):
        self.controller.generate_file(self.controller.start_frame.file_treeview, )

    def apply_theme(self):
        selected_theme = self.theme_combobox.get()  # Получаем выбранную тему
        if selected_theme:
            self.controller.root.set_theme(selected_theme)  # Применяем выбранную тему

    def toggle_dir_choice(self):
        if self.switch.is_on:  # Используйте свойство is_on нового виджета Switch
            self.dir_entry.config(state='normal')
            self.dir_button.config(state='normal')
        else:
            self.dir_entry.config(state='disabled')
            self.dir_button.config(state='disabled')
            self.populate_file_list(os.path.dirname(os.path.abspath(__file__)))

    def choose_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder_selected)
            self.populate_file_list(folder_selected)

    def populate_file_list(self, directory):
        self.file_listbox.delete(0, tk.END)
        for file in os.listdir(directory):
            if file.endswith(".xml"):
                self.file_listbox.insert(tk.END, file)

    def start(self):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        directory = self.dir_entry.get()

        if not selected_file:
            messagebox.showerror("Ошибка", "Файл не выбран.")
            return

        if not directory:
            directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(directory, selected_file)

        self.controller.start_analysis(file_path)


def generate_file(tree, tree_title):
    filetypes = [("TeX files", "*.tex"), ("Text", "*.txt")]
    file_path = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=filetypes)
    if not file_path:
        return

    def write_row(f, rid):
        f.write('\t'.join((
            tree.item(rid, 'text'),
            *tree.item(rid, 'values')
        ))+'\n')

    with open(file_path, 'w') as file:
        file.write(f"{tree_title}\n")
        for rowid in tree.get_children():
            write_row(file, rowid)


class XMLApp:
    def __init__(self, root):
        self.tab_control = ttk.Notebook(root)
        self.menu = None
        self.file_menu = None
        self.root = root
        self.available_themes = self.root.get_themes()
        self.root.set_theme('blue')
        self.root.title("XML Viewer")
        self.root.geometry("700x330")
        self.root.resizable(False, False)
        self.start_frame = StartFrame(self.root, self)  # Обратите внимание, что мы передаем self как controller
        self.start_frame.pack(expand=tk.YES, fill=tk.BOTH)

    def copy_selected_value(self, event):
        rowid = event.widget.focus()
        line = '\t'.join((
            event.widget.item(rowid, 'text'),
            *event.widget.item(rowid, 'values')
        ))
        if line:
            self.root.clipboard_append(line)
            self.root.update()

    @staticmethod
    def edit_value(event):
        rowid = event.widget.focus()  # Получаем выделенный элемент
        column = event.widget.identify_column(event.x)  # Определяем, в каком столбце произошел клик
        col_num = int(column[1:])  # Получаем номер столбца

        new_value = simpledialog.askstring("Edit Value", f"Enter new value")
        if new_value is not None and new_value.strip():
            line = [event.widget.item(rowid, 'text'), *event.widget.item(rowid, 'values')]
            line[col_num] = new_value
            event.widget.item(rowid, text=line[0], values=line[1:])

    def start_analysis(self, file_path):
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")
        result_window.geometry("1200x500")
        result_window.resizable(True, True)

        # Создаем Canvas и Scrollbar для горизонтальной прокрутки
        # canvas = tk.Canvas(result_window)
        # scrollbar = ttk.Scrollbar(result_window, orient="horizontal", command=canvas.xview)
        # frame = ttk.Frame(canvas)
        #
        # canvas.config(xscrollcommand=scrollbar.set)
        # scrollbar.pack(side="bottom", fill=X)
        # canvas.pack(side="left", fill=BOTH, expand=True)
        # canvas.create_window((0, 0), window=frame, anchor="nw")

        root_note = ScrollableNotebook(result_window, wheelscroll=True, tabmenu=True)
        root_note.pack(expand=tk.YES, fill=tk.BOTH)

        # frame.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))

        if not file_path:
            print("No file selected.")
            return

        try:
            root = ET.parse(file_path).getroot()
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            return

        # self.add_treeview(root, "Full Tree", tab_control)  # Здесь создается вкладка с полным деревом
        self.populate_root_notebook(root, root_note)

    def populate_root_notebook(self, xml_root, tab_control):
        namespaces = {'tr': 'urn:IEEE-1636.1:2011:01:TestResults'}

        for elem in xml_root.findall('.//tr:ResultSet', namespaces=namespaces):
            for child in elem.findall('./*', namespaces=namespaces):
                tag = child.tag.split('}')[-1]
                if tag in ('TestGroup', 'Test'):
                    name = child.get('callerName', child.get('name', 'Unknown'))
                    if name != "Unknown":
                        self.add_root_tab(child, name, tab_control)

    def add_root_tab(self, xml_element, tab_name: str, notebook: ttk.Notebook):
        # Создаем новый Frame для каждой вкладки
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        # Создаем новый Notebook внутри frame
        sub_notebook = ScrollableNotebook(frame, wheelscroll=True, tabmenu=True)
        sub_notebook.pack(expand=True, fill='both')  # Используем pack для размещения Notebook внутри Frame

        # Теперь для каждого дочернего элемента xml_element добавим вкладку в sub_notebook
        for child in xml_element:
            child_name = child.get('callerName', child.get('name', 'Unknown'))
            if child_name != "Unknown":
                self.add_treeview_tab(child, child_name, sub_notebook)

    def add_treeview_tab(self, xml_element, tab_name, notebook):
        # Создаем Frame для каждой вкладки
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        tree = ttk.Treeview(frame, columns=("status", "value", "valid_values"))
        tree.pack(expand=tk.YES, fill=tk.BOTH)

        tree.column("#0", width=270, minwidth=270)
        tree.column("status", width=150, minwidth=150)
        tree.column("value", width=150, minwidth=150)
        tree.column("valid_values", width=150, minwidth=150)

        tree.heading("#0", text="Treeview")
        tree.heading("status", text="Status")
        tree.heading("value", text="Value")
        tree.heading("valid_values", text="Valid Values")

        tree.bind("<Button-3>", self.copy_selected_value)
        tree.bind("<Control-c>", self.copy_selected_value)
        tree.bind("<Double-1>", self.edit_value)
        tree.bind("<Control-e>", self.edit_value)

        self.populate_tree(tree, xml_element)

        generate_button = ttk.Button(frame, text="Generate", command=lambda: generate_file(tree, tab_name))
        generate_button.pack()

        self.populate_tree(tree, xml_element)

    # Метод для добавления элементов в дерево
    def populate_tree(self, tree, elem, parent="", level=1):
        namespaces = {
            "tr": "urn:IEEE-1636.1:2011:01:TestResults",
            "c": "urn:IEEE-1671:2010:Common"
        }

        for child in elem:
            name = child.attrib.get('callerName', child.attrib.get('name', 'Unknown'))

            # Извлечение значения атрибута 'value' из тега 'tr:Outcome'
            outcome = child.find('./tr:Outcome', namespaces=namespaces)
            status = outcome.get('value') if outcome is not None else 'N/A'

            # Извлечение данных из тега 'tr:TestResult'
            test_result_elems = child.findall('.//tr:TestResult', namespaces=namespaces)
            for test_result in test_result_elems:
                value_elem = test_result.find("./tr:TestData/c:Datum", namespaces=namespaces)
                value = value_elem.get("value") if value_elem is not None else 'N/A'

                low_limit_elem = test_result.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='GE']/c:Datum", namespaces=namespaces)
                low_limit = low_limit_elem.get("value") if low_limit_elem is not None else ' '

                high_limit_elem = test_result.find(
                    "./tr:TestLimits/tr:Limits/c:LimitPair/c:Limit[@comparator='LE']/c:Datum", namespaces=namespaces)
                high_limit = high_limit_elem.get("value") if high_limit_elem is not None else ' '

                valid_values_str = f"{low_limit} < > {high_limit}"

                if name == "Unknown":
                    continue

                inserted_id = tree.insert(parent, tk.END, text=name, values=(
                    status, value, valid_values_str))  # Добавление статуса, значения и допустимых значений в дерево
                self.populate_tree(tree, child, parent=inserted_id, level=level + 1)


def main():
    root = ThemedTk()  # Используем ThemedTk вместо стандартного Tk
    XMLApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()  # Теперь main() вызывается только при прямом запуске файла
