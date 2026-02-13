"""
MATERIAL WINDOW - ContractorMitra
FULLY PRODUCTION READY + Modern Apple UI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from tkinter import filedialog
from datetime import datetime

class ModernStyle:
    BG_COLOR = "#f5f5f7"
    CARD_BG = "white"
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    ACCENT_BLUE = "#3498db"
    ACCENT_GREEN = "#2ecc71"
    ACCENT_ORANGE = "#f39c12"
    ACCENT_RED = "#e74c3c"
    ACCENT_PURPLE = "#9b59b6"

    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)

class MaterialWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Material Management - ContractorMitra")
        self.window.geometry("1200x700")
        self.window.configure(bg=ModernStyle.BG_COLOR)

        self.center_window()
        self.setup_ui()
        self.load_materials()

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f'{w}x{h}+{x}+{y}')

    def create_modern_button(self, parent, text, command, color, width=140):
        frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        canvas = tk.Canvas(frame, width=width, height=35, highlightthickness=0, bg=ModernStyle.BG_COLOR)
        canvas.pack()

        def draw_rect(fill):
            canvas.delete("all")
            points = [10,2, width-10,2, width-2,10, width-2,25, width-10,33, 10,33, 2,25, 2,10]
            canvas.create_polygon(points, smooth=True, fill=fill)
            canvas.create_text(width//2, 18, text=text, fill="white", font=ModernStyle.FONT_SMALL)

        draw_rect(color)

        def on_enter(e): draw_rect(self.darken(color))
        def on_leave(e): draw_rect(color)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", lambda e: command())
        return frame

    def darken(self, c):
        c = c.lstrip('#')
        r,g,b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        return f"#{max(0,r-20):02x}{max(0,g-20):02x}{max(0,b-20):02x}"

    def setup_ui(self):
        main = tk.Frame(self.window, bg=ModernStyle.BG_COLOR)
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Header
        header = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        header.pack(fill=tk.X, pady=(0,20))
        tk.Label(header, text="📦 Materials", font=ModernStyle.FONT_HEADER,
                 fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT)

        # Search + Add
        search_row = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        search_row.pack(fill=tk.X, pady=(0,15))

        tk.Label(search_row, text="🔍 Search:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT, padx=(0,10))

        self.search_var = tk.StringVar()
        tk.Entry(search_row, textvariable=self.search_var, font=ModernStyle.FONT_NORMAL,
                 relief=tk.FLAT, highlightthickness=1, highlightbackground="#ddd", width=30).pack(side=tk.LEFT, padx=(0,10))
        self.search_var.trace('w', lambda *a: self.load_materials())

        self.create_modern_button(search_row, "+ Add Material", self.add_material, ModernStyle.ACCENT_GREEN).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(search_row, "🔄 Refresh", self.load_materials, ModernStyle.ACCENT_BLUE).pack(side=tk.LEFT, padx=5)

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=ModernStyle.TEXT_PRIMARY,
                        rowheight=30, fieldbackground="white", font=ModernStyle.FONT_NORMAL)
        style.configure("Treeview.Heading", background=ModernStyle.BG_COLOR,
                        foreground=ModernStyle.TEXT_PRIMARY, font=("SF Pro Text", 11, "bold"))
        style.map("Treeview", background=[("selected", ModernStyle.ACCENT_BLUE)])

        cols = ("ID", "Material Name", "Category", "Unit", "Rate (Rs.)", "GST %")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=14, style="Treeview")
        widths = [50,300,150,80,120,80]
        for col,w in zip(cols,widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        scroll = ttk.Scrollbar(main, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        btn_row = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        btn_row.pack(fill=tk.X, pady=15)

        btns = [
            ("✏️ Edit", self.edit_material, ModernStyle.ACCENT_BLUE),
            ("🗑️ Delete", self.delete_material, ModernStyle.ACCENT_RED),
            ("📎 Import Excel", self.import_excel, ModernStyle.ACCENT_PURPLE),
            ("📊 Export Excel", self.export_excel, ModernStyle.ACCENT_ORANGE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        for txt,cmd,col in btns:
            self.create_modern_button(btn_row, txt, cmd, col).pack(side=tk.LEFT, padx=5)

    # ---------- DATABASE OPERATIONS ----------
    def load_materials(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, default_unit, default_rate, default_gst FROM materials ORDER BY name")
        data = cur.fetchall()
        conn.close()
        search = self.search_var.get().lower()
        for row in data:
            if search and search not in str(row[1]).lower() and search not in str(row[2]).lower():
                continue
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2] or "-", row[3] or "-",
                f"Rs. {row[4]:,.2f}" if row[4] else "Rs. 0.00",
                f"{row[5]}%" if row[5] else "18%"
            ))

    def add_material(self):
        win = tk.Toplevel(self.window)
        win.title("Add Material")
        win.geometry("400x350")
        win.configure(bg="white")
        tk.Label(win, text="➕ Add Material", font=ModernStyle.FONT_TITLE, bg="white").pack(pady=10)

        fields = {}
        for label, key in [("Material Name *", "name"), ("Category", "cat"), ("Unit", "unit"), ("Rate (Rs.)", "rate"), ("GST %", "gst")]:
            f = tk.Frame(win, bg="white")
            f.pack(pady=5)
            tk.Label(f, text=label, width=15, anchor='w', bg="white").pack(side=tk.LEFT)
            e = tk.Entry(f, width=25)
            e.pack(side=tk.LEFT)
            fields[key] = e

        def save():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "Material Name required")
                return
            try:
                conn = sqlite3.connect('contractormitra.db')
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO materials (name, category, default_unit, default_rate, default_gst)
                    VALUES (?,?,?,?,?)
                ''', (name, fields['cat'].get(), fields['unit'].get(),
                      float(fields['rate'].get() or 0), float(fields['gst'].get() or 18)))
                conn.commit()
                conn.close()
                win.destroy()
                self.load_materials()
                messagebox.showinfo("Success", "Material added")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save, bg=ModernStyle.ACCENT_GREEN, fg="white").pack(pady=10)

    def edit_material(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a material")
            return
        vals = self.tree.item(sel[0])['values']
        mid = vals[0]

        win = tk.Toplevel(self.window)
        win.title("Edit Material")
        win.geometry("400x350")
        win.configure(bg="white")
        tk.Label(win, text="✏️ Edit Material", font=ModernStyle.FONT_TITLE, bg="white").pack(pady=10)

        fields = {}
        for label, key, default in [("Material Name", "name", vals[1]), ("Category", "cat", vals[2]), ("Unit", "unit", vals[3]), ("Rate", "rate", vals[4]), ("GST %", "gst", vals[5])]:
            f = tk.Frame(win, bg="white")
            f.pack(pady=5)
            tk.Label(f, text=label, width=15, anchor='w', bg="white").pack(side=tk.LEFT)
            e = tk.Entry(f, width=25)
            e.insert(0, str(default).replace("Rs.","").replace("%","").strip())
            e.pack(side=tk.LEFT)
            fields[key] = e

        def update():
            try:
                conn = sqlite3.connect('contractormitra.db')
                cur = conn.cursor()
                cur.execute('''
                    UPDATE materials SET name=?, category=?, default_unit=?, default_rate=?, default_gst=?
                    WHERE id=?
                ''', (fields['name'].get(), fields['cat'].get(), fields['unit'].get(),
                      float(fields['rate'].get() or 0), float(fields['gst'].get() or 18), mid))
                conn.commit()
                conn.close()
                win.destroy()
                self.load_materials()
                messagebox.showinfo("Success", "Updated")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Update", command=update, bg=ModernStyle.ACCENT_BLUE, fg="white").pack(pady=10)

    def delete_material(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a material")
            return
        if not messagebox.askyesno("Confirm", "Delete selected material?"):
            return
        mid = self.tree.item(sel[0])['values'][0]
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM materials WHERE id=?", (mid,))
        conn.commit()
        conn.close()
        self.load_materials()
        messagebox.showinfo("Success", "Deleted")

    def import_excel(self):
        file = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx")])
        if not file:
            return
        try:
            df = pd.read_excel(file)
            conn = sqlite3.connect('contractormitra.db')
            for _,row in df.iterrows():
                conn.execute('''
                    INSERT OR IGNORE INTO materials (name, category, default_unit, default_rate, default_gst)
                    VALUES (?,?,?,?,?)
                ''', (row[0], row[1] if len(row)>1 else "", row[2] if len(row)>2 else "",
                      float(row[3]) if len(row)>3 else 0, float(row[4]) if len(row)>4 else 18))
            conn.commit()
            conn.close()
            self.load_materials()
            messagebox.showinfo("Success", "Imported")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")

    def export_excel(self):
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not file:
            return
        conn = sqlite3.connect('contractormitra.db')
        df = pd.read_sql_query("SELECT name, category, default_unit, default_rate, default_gst FROM materials", conn)
        conn.close()
        df.to_excel(file, index=False)
        messagebox.showinfo("Success", f"Exported to {file}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = MaterialWindow(root)
    root.mainloop()