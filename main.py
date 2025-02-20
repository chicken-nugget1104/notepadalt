import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font, ttk
from tkinter.scrolledtext import ScrolledText
import re
import json
import requests
import webbrowser
import logging
import os

VERSION = "1.2.0"

logging.basicConfig(filename="naerrorlog.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

class NotepadAlternative:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Notepad Alternative")
            self.root.geometry("800x600")
        
            self.tabs = ttk.Notebook(root)
            self.tabs.pack(expand=True, fill=tk.BOTH)
        
            self.tab_frames = []
            self.current_files = {}
            self.last_search_term = None

	    # Update Checker
            self.check_for_updates()
        
            # Theme shenanagins (took so long to make...)
            self.loaded_theme = "Light"
            self.current_theme = tk.StringVar(value=self.loaded_theme)
            self.themes = {
                "Light": {"bg": "white", "fg": "black", "insert": "black", "select": "lightblue"},
                "Dark": {"bg": "#1E1E1E", "fg": "#D4D4D4", "insert": "#D4D4D4", "select": "#3C3C3C"},
                "Solarized Light": {"bg": "#FDF6E3", "fg": "#657B83", "insert": "#586E75", "select": "#EEE8D5"},
                "Solarized Dark": {"bg": "#002B36", "fg": "#839496", "insert": "#93A1A1", "select": "#073642"},
                "Cooler Dark": {"bg": "#282c34", "fg": "#abb2bf", "insert": "#abb2bf", "select": "#3e4451"},
                "DOS Classic": {"bg": "#000000", "fg": "#FFFFFF", "insert": "#FFFFFF", "select": "#808080"},
                "Command Prompt": {"bg": "#1B1B1B", "fg": "#39FF14", "insert": "#00FF00", "select": "#008000"},
                "Gruvbox Light": {"bg": "#fbf1c7", "fg": "#3c3836", "insert": "#3c3836", "select": "#d5c4a1"},
                "Gruvbox Dark": {"bg": "#282828", "fg": "#ebdbb2", "insert": "#ebdbb2", "select": "#504945"},
                "Midnight": {"bg": "#121212", "fg": "#AFAFAF", "insert": "#C0C0C0", "select": "#292929"},
                "Nord": {"bg": "#2E3440", "fg": "#D8DEE9", "insert": "#88C0D0", "select": "#4C566A"}
            }
            self.style = ttk.Style()

            # SETTINGS
            self.word_wrap = tk.BooleanVar(value=True)
            self.show_line_numbers = tk.BooleanVar(value=False)
            self.line_numbers = None
            self.current_font = "Arial"

            self.create_menu()
            self.load_config()
            self.apply_theme()
            self.new_tab()
        
            self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        except Exception as e:
            logger.error(f"An error occurred while initializing the application: {e}")
            logger.error("Traceback:", exc_info=True)
            self.root.quit()

    def check_for_updates(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/chicken-nugget1104/notepadalt/refs/heads/main/versionnumber.txt")
            latest_version = response.text.strip()
            
            if VERSION.endswith("-DEV"):
                return
            
            if VERSION != latest_version:
                if messagebox.askyesno("Update Available", "Oh noes! You're running a (possibly) outdated version! Wanna update?"):
                    webbrowser.open(f"https://github.com/chicken-nugget1104/notepadalt/releases/tag/{latest_version}")
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.new_tab)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Find Next", command=self.find_next, accelerator="F3")
        #DOESNT WORK
        #edit_menu.add_command(label="Find Previous", command=self.find_previous)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        edit_menu.add_command(label="Go To Line", command=self.go_to_line, accelerator="Ctrl+G")
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        #EVERYTHING STARTING WITH # NEEDS TO BE ADDED LATER! PROBABLY IN V2! UNLESS SOME CONTRIBUTER ADDS THEM FOR ME! lol
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl+")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.zoom_reset, accelerator="Ctrl+R")
        if VERSION.endswith("-DEV"):
            view_menu.add_command(label="CCZ (DEBUG ONLY)", command=self.whatisthecurrentzoom)
        menu_bar.add_cascade(label="View", menu=view_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        for theme in self.themes.keys():
            theme_menu.add_radiobutton(label=theme, variable=self.current_theme, command=self.apply_theme)
        
        settings_menu.add_cascade(label="Themes", menu=theme_menu)
        settings_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap, command=self.toggle_word_wrap)
        settings_menu.add_command(label="Change Font", command=self.change_font)
        #settings_menu.add_checkbutton(label="Show Line Numbers", onvalue=True, offvalue=False, variable=self.show_line_numbers, command=self.toggle_line_numbers)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Check Spelling", command=self.check_spelling, accelerator="Ctrl+P")
        tools_menu.add_command(label="Remove Extra Spaces", command=self.remove_extra_spaces)
        tools_menu.add_command(label="About...", command=self.show_about)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)

        self.root.bind_all("<Control-p>", lambda event: self.check_spelling())
        self.root.bind_all("<Control-f>", lambda event: self.find_text())
        self.root.bind_all("<F3>", lambda event: self.find_next())
        self.root.bind_all("<Control-g>", lambda event: self.go_to_line())
        self.root.bind_all("<Control-z>", lambda event: self.undo())
        self.root.bind_all("<Control-y>", lambda event: self.redo())
        self.root.bind_all("<Control-s>", lambda event: self.save_file())
        self.root.bind_all("<Control-o>", lambda event: self.open_file())
        self.root.bind_all("<Control-plus>", lambda event: self.zoom_in())
        self.root.bind_all("<Control-equal>", lambda event: self.zoom_in())
        self.root.bind_all("<Control-minus>", lambda event: self.zoom_out())
        self.root.bind_all("<Control-r>", lambda event: self.zoom_reset())
        self.root.bind_all("<Control-MouseWheel>", lambda event: self.zoom_in() if event.delta > 0 else self.zoom_out())
    
    def new_tab(self):
        frame = tk.Frame(self.tabs)
        text_area = ScrolledText(frame, wrap="word", undo=True, font=(self.current_font, 12))
        text_area.pack(expand=True, fill=tk.BOTH)
        
        text_area.bind("<KeyRelease>", self.update_status)
        
        tab_name = f"Untitled {len(self.tab_frames) + 1}"
        self.tabs.add(frame, text=tab_name)
        self.tab_frames.append(text_area)
        self.current_files[text_area] = None
    
    def get_current_text_area(self):
        if not self.tab_frames:
            return None
        current_index = self.tabs.index(self.tabs.select())
        return self.tab_frames[current_index]

    def update_tab_title(self, text_area, file_path):
        tab_name = file_path.split("/")[-1]
        self.tabs.tab(self.tab_frames.index(text_area), text=tab_name)

    def toggle_word_wrap(self):
        for text_area in self.tab_frames:
            text_area.config(wrap="word" if self.word_wrap.get() else "none")
        self.save_config()

    def toggle_line_numbers(self):
        if self.show_line_numbers.get():
            if not self.line_numbers:
                text_area = self.get_current_text_area()
                self.line_numbers = tk.Text(text_area, width=2, padx=5, takefocus=0, border=0, state="disabled")
                self.line_numbers.pack(side="left", fill="y")
                text_area.pack_configure(padx=(5, 0))
            self.update_line_numbers()
        else:
            if self.line_numbers:
                text_area = self.get_current_text_area()
                self.line_numbers.pack_forget()
                self.line_numbers = None
                text_area.pack_configure(padx=(0, 0))
    
    def update_line_numbers(self):
        if self.line_numbers:
            text_area = self.get_current_text_area()
            self.line_numbers.config(state="normal")
            self.line_numbers.delete(1.0, tk.END)
            line_count = text_area.index(tk.END).split(".")[0]
            self.line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, int(line_count))))
            self.line_numbers.config(state="disabled")
            self.root.after(100, self.update_line_numbers)
    
    #FILE HELPERS
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Javascript Files", "*.js"), ("Haxe Files", "*.hx"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    text_area = self.get_current_text_area()
                    text_area.delete(1.0, tk.END)
                    text_area.insert(tk.END, file.read())
                self.current_files[text_area] = file_path
                self.update_tab_title(text_area, file_path)
                self.update_status()
            except Exception as e:
                logger.error(f"Error opening file: {e}")
                messagebox.showerror("Error", "Failed to open the file.")
    
    def save_file(self):
        text_area = self.get_current_text_area()
        file_path = self.current_files.get(text_area)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get(1.0, tk.END))
                self.update_tab_title(text_area, file_path)
                text_area.edit_modified(False)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        text_area = self.get_current_text_area()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Javascript Files", "*.js"), ("Haxe Files", "*.hx"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get(1.0, tk.END))
                text_area.edit_modified(False)
            self.current_files[text_area] = file_path
            self.update_tab_title(text_area, file_path)

    def get_file_extension(self, text_area):
        text_area = self.get_current_text_area()
        current_file = self.current_files.get(text_area)
        if current_file:
            return os.path.splitext(current_file)[1]
        return ""

    def setup_syntax_highlighting(self, text_area):
        file_extension = self.get_file_extension(text_area)
        
        if file_extension in [".haxe"]:
            text_area.tag_configure("keyword", foreground="blue")
            text_area.tag_configure("comment", foreground="green")
            text_area.tag_configure("string", foreground="red")
            self.add_haxe_highlighting(text_area)

    def highlight_pattern(self, text_area, pattern, tag_name):
        start = "1.0"
        while True:
            start = text_area.search(pattern, start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(text_area.get(start, start + '1c'))}c"
            text_area.tag_add(tag_name, start, end)
            start = end

    def add_haxe_highlighting(self, text_area):
        haxe_keywords = r'\b(?:class|function|var|new|this|if|else|return)\b'
        haxe_comments = r'//.*|/\*[\s\S]*?\*/'
        haxe_strings = r'"[^"]*"'
        
        self.highlight_pattern(text_area, haxe_keywords, "keyword")
        self.highlight_pattern(text_area, haxe_comments, "comment")
        self.highlight_pattern(text_area, haxe_strings, "string")
    
    def undo(self):
        self.get_current_text_area().edit_undo()
    
    def redo(self):
        self.get_current_text_area().edit_redo()

    def remove_extra_spaces(self):
        text_area = self.get_current_text_area()
        text = text_area.get("1.0", "end-1c")
        cleaned_text = "\n".join(line.rstrip() for line in text.splitlines())
        if text != cleaned_text:
            text_area.delete("1.0", "end")
            text_area.insert("1.0", cleaned_text)

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

    def find_previous(self):
        if self.last_search_term:
            text_area = self.get_current_text_area()
            content = text_area.get(1.0, tk.END)
            current_index = text_area.index(tk.INSERT)
            last_index = content.rfind(self.last_search_term, 0, content.find(self.last_search_term, content.index(current_index)))

            if last_index != -1:
                text_area.tag_remove("highlight", "1.0", tk.END)
                text_area.tag_add("highlight", "1.0 + {}c".format(last_index), "1.0 + {}c".format(last_index + len(self.last_search_term)))
                text_area.tag_config("highlight", background="yellow")
            else:
                messagebox.showinfo("Find", "No previous occurrences found.")
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
            messagebox.showinfo("Spell Check", "There is no lines of text! Please write at least 1 word!")
            return
        
        misspelled = [word for word in words if not re.match(r'^[A-Za-z]+$', word)]
        if misspelled:
            misspelled_text = ', '.join(misspelled)
            messagebox.showinfo("Spell Check", f"Possible misspellings: {misspelled_text}")
        else:
            messagebox.showinfo("Spell Check", "We found no spelling errors!")

    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Choose Font")
        
        font_list = [f for f in font.families() if re.match(r'^[A-Za-z0-9]+$', f)]
        font_var = tk.StringVar(value=self.current_font[0])
        
        font_listbox = tk.Listbox(font_window, listvariable=tk.StringVar(value=font_list), height=10)
        font_listbox.pack(fill="both", expand=True)
        
        def set_font():
            selected_font = font_listbox.get(tk.ACTIVE)
            if selected_font:
                self.current_font = selected_font
                for text_area in self.tab_frames:
                    text_area.config(font=(self.current_font, 12))
                print(f"{self.current_font}")
                self.save_config()
                print("Saved config")
                font_window.destroy()
        
        tk.Button(font_window, text="Apply", command=set_font).pack()

    def show_about(self):
        messagebox.showinfo("About", f"Notepad Alternative v{VERSION}\nCreated by silly goober\n2025-2026")

    def update_status(self, event=None):
        text_area = self.get_current_text_area()
        content = text_area.get(1.0, tk.END)
        words = len(content.split())
        letters = len(content.replace(" ", "").replace("\n", ""))
        self.root.title(f"Notepad Alternative v{VERSION} - Word Count: {words} - Letter Count: {letters}")

    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
                self.word_wrap.set(config_data.get("word_wrap", True))
                self.current_font = config_data.get("font", "Arial")
        except (FileNotFoundError, json.JSONDecodeError):
            self.word_wrap.set(True)
            self.current_font = "Arial"

    def save_config(self):
        try:
            word_wrap_value = self.word_wrap.get()
            with open("config.json", "w") as config_file:
                json.dump({"word_wrap": word_wrap_value, "font": self.current_font}, config_file, indent=4)
        except Exception as e:
            logger.error(f"Error saving theme config: {e}")

    def apply_theme(self):
        theme_name = self.current_theme.get()
        if theme_name in self.themes:
            theme = self.themes[theme_name]
        else:
            theme = self.themes["Light"]
        for text_area in self.tab_frames:
            text_area.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"], selectbackground=theme["select"])
        self.root.config(bg=theme["bg"])
        self.style.configure("TNotebook.Tab", background=theme["bg"])
        self.style.configure("TNotebook", background=theme["bg"])

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
        if current_size != 28:
            text_area.config(font=(self.current_font, current_size + 2))
    
    def zoom_out(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        if current_size != 8:
            text_area.config(font=(self.current_font, max(8, current_size - 2)))

    def whatisthecurrentzoom(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        messagebox.showinfo("Zoom", current_size)

    def zoom_reset(self):
        text_area = self.get_current_text_area()
        current_size = int(text_area.cget("font").split()[1])
        text_area.config(font=(self.current_font, 12))
    
    def on_exit(self):
        for text_area in self.tab_frames:
            if text_area.edit_modified():
                if messagebox.askyesno("Save Changes", "You have some unsaved changes. Save before exiting?"):
                    self.save_file()
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadAlternative(root)
    root.mainloop()

