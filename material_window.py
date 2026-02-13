"""
MATERIAL WINDOW - ContractorMitra
Modern Apple-style material management
Version: 3.0.0 (Clean UI Edition)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ModernStyle:
    """Modern Apple-like style constants"""
    BG_COLOR = "#f5f5f7"
    CARD_BG = "white"
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    ACCENT_BLUE = "#3498db"
    ACCENT_GREEN = "#2ecc71"
    ACCENT_ORANGE = "#f39c12"
    ACCENT_PURPLE = "#9b59b6"
    ACCENT_RED = "#e74c3c"
    ACCENT_TEAL = "#1abc9c"
    
    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)


class MaterialWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Material Management - ContractorMitra")
        self.window.geometry("1100x650")
        self.window.configure(bg=ModernStyle.BG_COLOR)
        
        self.center_window()
        self.setup_ui()
        self.load_materials()
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_modern_button(self, parent, text, command, color=ModernStyle.ACCENT_BLUE, width=120):
        btn_frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        canvas = tk.Canvas(btn_frame, width=width, height=35, 
                          highlightthickness=0, bg=ModernStyle.BG_COLOR)
        canvas.pack()
        
        def draw_rect(fill_color):
            canvas.delete("all")
            canvas.create_rounded_rect(2, 2, width-2, 33, 8, fill=fill_color, outline="")
            canvas.create_text(width//2, 18, text=text, fill="white", font=ModernStyle.FONT_SMALL)
        
        def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
            points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, 
                     x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, 
                     x1, y1+r, x1, y1]
            canvas.create_polygon(points, smooth=True, **kwargs)
        
        canvas.create_rounded_rect = create_rounded_rect.__get__(canvas)
        draw_rect(color)
        
        def on_enter(e): draw_rect(self.darken_color(color))
        def on_leave(e): draw_rect(color)
        
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", lambda e: command())
        return btn_frame
    
    def darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r, g, b = max(0, r-20), max(0, g-20), max(0, b-20)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return 'break'
    
    def show_paste_menu(self, event):
        widget = event.widget
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_text(widget))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return 'break'
    
    def paste_text(self, widget):
        try:
            text = self.window.clipboard_get()
            widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass
    
    def setup_ui(self):
        main_frame = tk.Frame(self.window, bg=ModernStyle.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="📦 Materials", 
                        font=ModernStyle.FONT_HEADER,
                        fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR)
        title.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        search_label = tk.Label(search_frame, text="🔍 Search:", 
                               font=ModernStyle.FONT_NORMAL,
                               fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR)
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=ModernStyle.FONT_NORMAL,
                               relief=tk.FLAT, highlightthickness=1,
                               highlightcolor=ModernStyle.ACCENT_BLUE,
                               highlightbackground="#ddd", width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.on_search)
        
        add_btn = self.create_modern_button(search_frame, "+ Add Material", 
                                          self.add_material, ModernStyle.ACCENT_GREEN)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = self.create_modern_button(search_frame, "🔄 Refresh", 
                                               self.load_materials, ModernStyle.ACCENT_BLUE)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        self.setup_treeview(main_frame)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        button_frame.pack(fill=tk.X, pady=15)
        
        buttons = [
            ("✏️ Edit", self.edit_material, ModernStyle.ACCENT_BLUE),
            ("🗑️ Delete", self.delete_material, ModernStyle.ACCENT_RED),
            ("📎 Import Excel", self.import_excel, ModernStyle.ACCENT_PURPLE),
            ("📊 Export Excel", self.export_excel, ModernStyle.ACCENT_ORANGE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        
        for text, cmd, color in buttons:
            btn = self.create_modern_button(button_frame, text, cmd, color)
            btn.pack(side=tk.LEFT, padx=5)
    
    def setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background="white",
                       foreground=ModernStyle.TEXT_PRIMARY,
                       rowheight=30,
                       fieldbackground="white",
                       font=ModernStyle.FONT_NORMAL)
        style.configure("Treeview.Heading",
                       background=ModernStyle.BG_COLOR,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       font=("SF Pro Text", 11, "bold"))
        style.map("Treeview", background=[("selected", ModernStyle.ACCENT_BLUE)])
        
        columns = ("ID", "Material Name", "Category", "Unit", "Rate (Rs.)", "GST %")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", 
                                 height=15, style="Treeview")
        
        column_widths = [50, 250, 150, 80, 120, 80]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_materials(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category, default_unit, default_rate, default_gst FROM materials ORDER BY name")
            materials = cursor.fetchall()
            conn.close()
            
            for m in materials:
                self.tree.insert("", "end", values=(
                    m[0], m[1], m[2] or "-", m[3] or "-", 
                    f"Rs. {m[4]:,.2f}" if m[4] else "Rs. 0.00",
                    f"{m[5]}%" if m[5] else "0%"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load materials: {str(e)}")
    
    def on_search(self, event=None):
        search_term = self.search_var.get().lower()
        self.load_materials()
        if not search_term:
            return
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if not any(search_term in str(v).lower() for v in values[1:3]):
                self.tree.delete(item)
    
    def add_material(self):
        # Simplified for brevity - will be implemented in next phase
        messagebox.showinfo("Coming Soon", "Add Material form will be modernized in Phase 3")
    
    def edit_material(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a material to edit")
            return
        messagebox.showinfo("Coming Soon", "Edit Material will be modernized in Phase 3")
    
    def delete_material(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a material to delete")
            return
        messagebox.showinfo("Coming Soon", "Delete Material will be modernized in Phase 3")
    
    def import_excel(self):
        messagebox.showinfo("Coming Soon", "Excel Import will be modernized in Phase 3")
    
    def export_excel(self):
        messagebox.showinfo("Coming Soon", "Excel Export will be modernized in Phase 3")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = MaterialWindow(root)
    root.mainloop()