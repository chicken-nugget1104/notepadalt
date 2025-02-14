import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText
import re

class NotepadAlternative:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad Alternative")
        self.root.geometry("800x600")
        
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill=tk.BOTH)
        
        self.tab_frames = []
        self.current_files = {}
        self.word_wrap = tk.BooleanVar(value=True)
        self.last_search_term = None
        
        self.create_menu()
        self.new_tab()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.new_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Find Next", command=self.find_next)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        #EVERYTHING STARTING WITH # NEEDS TO BE ADDED LATER! PROBABLY IN V2! UNLESS SOME CONTRIBUTER ADDS THEM FOR ME! lol
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.zoom_reset)
        #view_menu.add_command(label="CCZ (DEBUG ONLY)", command=self.whatisthecurrentzoom)
        view_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap, command=self.toggle_word_wrap)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        #settings_menu = tk.Menu(menu_bar, tearoff=0)
        #settings_menu.add_command(label="Font Settings", command=self.font_settings)
        #settings_menu.add_command(label="Toggle Spell Check", command=self.toggle_spell_check)
        #menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Go To Line", command=self.go_to_line, accelerator="Ctrl+G")
        tools_menu.add_command(label="Check Spelling", command=self.check_spelling, accelerator="Ctrl+P")
        tools_menu.add_command(label="About...", command=self.show_about)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)

        self.root.bind_all("<Control-p>", lambda event: self.check_spelling())
        self.root.bind_all("<Control-f>", lambda event: self.find_text())
        self.root.bind_all("<Control-g>", lambda event: self.go_to_line())
        self.root.bind_all("<Control-z>", lambda event: self.undo())
        self.root.bind_all("<Control-y>", lambda event: self.redo())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
    
    def new_tab(self):
        frame = tk.Frame(self.tabs)
        text_area = ScrolledText(frame, wrap="word", undo=True, font=("Arial", 12))
        text_area.pack(expand=True, fill=tk.BOTH)
        
        text_area.bind("<KeyRelease>", self.update_status)
        
        self.tabs.add(frame, text=f"Untitled {len(self.tab_frames) + 1}")
        self.tab_frames.append(text_area)
        self.current_files[text_area] = None
    
    def get_current_text_area(self):
        current_index = self.tabs.index(self.tabs.select())
        return self.tab_frames[current_index]

    def toggle_word_wrap(self):
        for text_area in self.tab_frames:
            text_area.config(wrap="word" if self.word_wrap.get() else "none")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Javascript Files", "*.js"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                text_area = self.get_current_text_area()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, file.read())
            self.current_files[text_area] = file_path
            self.update_status()
    
    def save_file(self):
        text_area = self.get_current_text_area()
        file_path = self.current_files.get(text_area)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get(1.0, tk.END))
        else:
            self.save_as_file()
    
    def save_as_file(self):
        text_area = self.get_current_text_area()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"),  ("Javascript Files", "*.js"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get(1.0, tk.END))
            self.current_files[text_area] = file_path
    
    def undo(self):
        self.get_current_text_area().edit_undo()
    
    def redo(self):
        self.get_current_text_area().edit_redo()

    def find_text(self):
        self.last_search_term = simpledialog.askstring("Find", "Enter text to search:")
        if self.last_search_term:
            text_area = self.get_current_text_area()
            content = text_area.get(1.0, tk.END)
            start_index = content.find(self.last_search_term)
            if start_index != -1:
                text_area.tag_add("highlight", "1.0 + {}c".format(start_index), "1.0 + {}c".format(start_index + len(self.last_search_term)))
                text_area.tag_config("highlight", background="yellow")
            else:
                messagebox.showinfo("Find", f"'{self.last_search_term}' not found.")
    
    def find_next(self):
        if self.last_search_term:
            text_area = self.get_current_text_area()
            content = text_area.get(1.0, tk.END)
            start_index = content.find(self.last_search_term)
            if start_index != -1:
                start_index = content.find(self.last_search_term, start_index + len(self.last_search_term))
                if start_index != -1:
                    text_area.tag_remove("highlight", "1.0", tk.END)
                    text_area.tag_add("highlight", "1.0 + {}c".format(start_index), "1.0 + {}c".format(start_index + len(self.last_search_term)))
                    text_area.tag_config("highlight", background="yellow")
                else:
                    messagebox.showinfo("Find", "No more occurrences found.")
            else:
                messagebox.showinfo("Find", f"'{self.last_search_term}' not found.")
        else:
            messagebox.showinfo("Find", "Please perform a search first.")

    def replace_text(self):
        if self.last_search_term is None:
            messagebox.showinfo("Replace", "Please perform a search first.")
            return
        
        replacement_term = simpledialog.askstring("Replace", "Enter text to replace with:")
        if replacement_term is not None:
            text_area = self.get_current_text_area()
            content = text_area.get(1.0, tk.END)
            new_content = content.replace(self.last_search_term, replacement_term)
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, new_content)
            text_area.tag_remove("highlight", "1.0", tk.END)

    def check_spelling(self):
        text_area = self.get_current_text_area()
        content = text_area.get(1.0, tk.END).strip()
        words = content.split()
        
        if not words:
            messagebox.showinfo("Spell Check", "There is no lines of text!")
            return
        
        misspelled = [word for word in words if not re.match(r'^[A-Za-z]+$', word)]
        if misspelled:
            messagebox.showinfo("Spell Check", f"Possible misspellings: {', '.join(misspelled)}")
        else:
            messagebox.showinfo("Spell Check", "We found no spelling errors!")

    def show_about(self):
        messagebox.showinfo("About", "Notepad Alternative v1.0.1\nCreated by silly goober\n2025-2026")

    def update_status(self, event=None):
        text_area = self.get_current_text_area()
        content = text_area.get(1.0, tk.END)
        words = len(content.split())
        self.root.title(f"Notepad Alternative - Word Count: {words}")

    def go_to_line(self):
        line_number_str = simpledialog.askstring("Go to Line", "Enter the line number:")
        if line_number_str is not None:
            try:
                line_number = int(line_number_str)
                text_area = self.get_current_text_area()
                total_lines = int(text_area.index('end-1c').split('.')[0]) - 1
                if line_number <= total_lines and line_number > 0:
                    text_area.yview_scroll(line_number - 1, "units")
                    text_area.mark_set("insert", f"{line_number}.0")
                    text_area.see(f"{line_number}.0")
                else:
                    messagebox.showerror("Go to Line", f"Line number {line_number} is out of range. There are {total_lines} lines.")
            except ValueError:
                messagebox.showerror("Go to Line", "Please enter a valid number.")

    def zoom_in(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        if current_size != 30:
            text_area.config(font=("Arial", current_size + 2))
    
    def zoom_out(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        if current_size != 6:
            text_area.config(font=("Arial", max(8, current_size - 2)))

    def whatisthecurrentzoom(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        messagebox.showinfo("Zoom", current_size)

    def zoom_reset(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        text_area.config(font=("Arial", 12))
    
    def on_exit(self):
        for text_area in self.tab_frames:
            if text_area.edit_modified():
                if messagebox.askyesno("Save Changes", "You have some unsaved changes. Save before exiting?"):
                    self.save_file()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadAlternative(root)
    root.mainloop()
