"""
REPORTS WINDOW - ContractorMitra
Modern Apple-style reports dashboard
Version: 3.0.0 (Clean UI Edition)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

class ModernStyle:
    BG_COLOR = "#f5f5f7"
    CARD_BG = "white"
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    ACCENT_BLUE = "#3498db"
    ACCENT_GREEN = "#2ecc71"
    ACCENT_ORANGE = "#f39c12"
    ACCENT_PURPLE = "#9b59b6"
    ACCENT_RED = "#e74c3c"
    
    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)


class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reports Dashboard - ContractorMitra")
        self.window.geometry("1200x700")
        self.window.configure(bg=ModernStyle.BG_COLOR)
        
        self.report_type = tk.StringVar(value="sales")
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()
        
        today = datetime.now()
        first_day = today.replace(day=1)
        self.date_from.set(first_day.strftime("%Y-%m-%d"))
        self.date_to.set(today.strftime("%Y-%m-%d"))
        
        self.current_data = []
        self.current_columns = []
        
        self.center_window()
        self.setup_ui()
    
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
    
    def setup_ui(self):
        main_frame = tk.Frame(self.window, bg=ModernStyle.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="📊 Reports Dashboard", 
                        font=ModernStyle.FONT_HEADER,
                        fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR)
        title.pack(side=tk.LEFT)
        
        # Controls card
        controls_card = tk.Frame(main_frame, bg="white", relief=tk.FLAT)
        controls_card.pack(fill=tk.X, pady=(0, 20))
        
        controls_inner = tk.Frame(controls_card, bg="white")
        controls_inner.pack(fill=tk.X, padx=20, pady=20)
        
        # Report type
        type_frame = tk.Frame(controls_inner, bg="white")
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        type_label = tk.Label(type_frame, text="Report Type:", 
                            font=ModernStyle.FONT_NORMAL,
                            fg=ModernStyle.TEXT_PRIMARY, bg="white")
        type_label.pack(side=tk.LEFT, padx=(0, 15))
        
        reports = [
            ("💰 Sales", "sales"),
            ("📊 Pending", "pending"),
            ("👥 Customers", "customers"),
            ("📦 Materials", "materials"),
            ("📈 Monthly", "monthly")
        ]
        
        for text, value in reports:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.report_type,
                              value=value, font=ModernStyle.FONT_NORMAL,
                              bg="white", activebackground="white",
                              selectcolor="white", command=self.generate_report)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Date range
        date_frame = tk.Frame(controls_inner, bg="white")
        date_frame.pack(fill=tk.X, pady=(0, 15))
        
        date_label = tk.Label(date_frame, text="Date Range:", 
                            font=ModernStyle.FONT_NORMAL,
                            fg=ModernStyle.TEXT_PRIMARY, bg="white")
        date_label.pack(side=tk.LEFT, padx=(0, 15))
        
        from_label = tk.Label(date_frame, text="From:", 
                            font=ModernStyle.FONT_SMALL,
                            fg=ModernStyle.TEXT_SECONDARY, bg="white")
        from_label.pack(side=tk.LEFT, padx=(10, 5))
        
        from_entry = tk.Entry(date_frame, textvariable=self.date_from,
                            font=ModernStyle.FONT_NORMAL, width=12,
                            relief=tk.FLAT, highlightthickness=1,
                            highlightcolor=ModernStyle.ACCENT_BLUE,
                            highlightbackground="#ddd")
        from_entry.pack(side=tk.LEFT, padx=5)
        
        to_label = tk.Label(date_frame, text="To:", 
                          font=ModernStyle.FONT_SMALL,
                          fg=ModernStyle.TEXT_SECONDARY, bg="white")
        to_label.pack(side=tk.LEFT, padx=(10, 5))
        
        to_entry = tk.Entry(date_frame, textvariable=self.date_to,
                          font=ModernStyle.FONT_NORMAL, width=12,
                          relief=tk.FLAT, highlightthickness=1,
                          highlightcolor=ModernStyle.ACCENT_BLUE,
                          highlightbackground="#ddd")
        to_entry.pack(side=tk.LEFT, padx=5)
        
        # Quick dates
        quick_frame = tk.Frame(controls_inner, bg="white")
        quick_frame.pack(fill=tk.X)
        
        periods = [
            ("Today", 0),
            ("Last 7 Days", 7),
            ("This Month", 30),
            ("Last Month", 60),
            ("This Year", 365)
        ]
        
        for text, days in periods:
            btn = self.create_modern_button(quick_frame, text, 
                                          lambda d=days: self.set_quick_date(d),
                                          ModernStyle.TEXT_SECONDARY, 100)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        self.setup_treeview(main_frame)
        
        # Export buttons
        export_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        export_frame.pack(fill=tk.X, pady=15)
        
        buttons = [
            ("📊 Export Excel", self.export_excel, ModernStyle.ACCENT_GREEN),
            ("📄 Export PDF", self.export_pdf, ModernStyle.ACCENT_ORANGE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        
        for text, cmd, color in buttons:
            btn = self.create_modern_button(export_frame, text, cmd, color, 130)
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
        
        self.tree = ttk.Treeview(parent, show="headings", height=15, style="Treeview")
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def set_quick_date(self, days):
        today = datetime.now()
        self.date_to.set(today.strftime("%Y-%m-%d"))
        if days == 0:
            self.date_from.set(today.strftime("%Y-%m-%d"))
        elif days == 30:
            self.date_from.set(today.replace(day=1).strftime("%Y-%m-%d"))
        elif days == 60:
            first = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last = today.replace(day=1) - timedelta(days=1)
            self.date_from.set(first.strftime("%Y-%m-%d"))
            self.date_to.set(last.strftime("%Y-%m-%d"))
        elif days == 365:
            self.date_from.set(today.replace(month=1, day=1).strftime("%Y-%m-%d"))
        else:
            self.date_from.set((today - timedelta(days=days)).strftime("%Y-%m-%d"))
        self.generate_report()
    
    def generate_report(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_data = []
        
        report_type = self.report_type.get()
        if report_type == "sales":
            self.generate_sales_report()
        elif report_type == "pending":
            self.generate_pending_report()
        elif report_type == "customers":
            self.generate_customer_report()
        elif report_type == "materials":
            self.generate_material_report()
        elif report_type == "monthly":
            self.generate_monthly_report()
    
    def generate_sales_report(self):
        columns = ("Invoice #", "Date", "Customer", "Amount")
        self.setup_report_columns(columns)
        # Add your sales query here
        messagebox.showinfo("Coming Soon", "Sales report data will be populated in Phase 3")
    
    def generate_pending_report(self):
        columns = ("Invoice #", "Date", "Customer", "Amount", "Days")
        self.setup_report_columns(columns)
        messagebox.showinfo("Coming Soon", "Pending report data will be populated in Phase 3")
    
    def generate_customer_report(self):
        columns = ("Customer", "Phone", "Invoices", "Total")
        self.setup_report_columns(columns)
        messagebox.showinfo("Coming Soon", "Customer report data will be populated in Phase 3")
    
    def generate_material_report(self):
        columns = ("Material", "Unit", "Quantity", "Amount")
        self.setup_report_columns(columns)
        messagebox.showinfo("Coming Soon", "Material report data will be populated in Phase 3")
    
    def generate_monthly_report(self):
        columns = ("Month", "Invoices", "Sales", "GST", "Net")
        self.setup_report_columns(columns)
        messagebox.showinfo("Coming Soon", "Monthly report data will be populated in Phase 3")
    
    def setup_report_columns(self, columns):
        self.current_columns = columns
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
    
    def export_excel(self):
        messagebox.showinfo("Coming Soon", "Excel export will be modernized in Phase 3")
    
    def export_pdf(self):
        messagebox.showinfo("Coming Soon", "PDF export will be modernized in Phase 3")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = ReportsWindow(root)
    root.mainloop()