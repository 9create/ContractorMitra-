"""
PENDING PAYMENTS WINDOW - ContractorMitra
Modern Apple-style pending payments tracker
Version: 3.0.0 (Clean UI Edition)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

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


class PendingWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Pending Payments - ContractorMitra")
        self.window.geometry("1100x650")
        self.window.configure(bg=ModernStyle.BG_COLOR)
        
        self.center_window()
        self.setup_ui()
        self.load_payments()
    
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
        
        title = tk.Label(header_frame, text="💰 Pending Payments", 
                        font=ModernStyle.FONT_HEADER,
                        fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR)
        title.pack(side=tk.LEFT)
        
        # Summary card
        summary_card = tk.Frame(main_frame, bg="white", relief=tk.FLAT)
        summary_card.pack(fill=tk.X, pady=(0, 20))
        
        summary_inner = tk.Frame(summary_card, bg="white")
        summary_inner.pack(fill=tk.X, padx=20, pady=15)
        
        self.total_pending_var = tk.StringVar(value="Rs. 0.00")
        self.total_overdue_var = tk.StringVar(value="Rs. 0.00")
        
        pending_label = tk.Label(summary_inner, text="Total Pending:", 
                               font=ModernStyle.FONT_NORMAL,
                               fg=ModernStyle.TEXT_SECONDARY, bg="white")
        pending_label.pack(side=tk.LEFT, padx=(0, 5))
        
        pending_value = tk.Label(summary_inner, textvariable=self.total_pending_var,
                               font=ModernStyle.FONT_TITLE,
                               fg=ModernStyle.ACCENT_RED, bg="white")
        pending_value.pack(side=tk.LEFT, padx=(0, 20))
        
        overdue_label = tk.Label(summary_inner, text="Overdue:", 
                               font=ModernStyle.FONT_NORMAL,
                               fg=ModernStyle.TEXT_SECONDARY, bg="white")
        overdue_label.pack(side=tk.LEFT, padx=(0, 5))
        
        overdue_value = tk.Label(summary_inner, textvariable=self.total_overdue_var,
                               font=ModernStyle.FONT_TITLE,
                               fg=ModernStyle.ACCENT_ORANGE, bg="white")
        overdue_value.pack(side=tk.LEFT)
        
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
        
        add_btn = self.create_modern_button(search_frame, "+ Add Payment", 
                                          self.add_payment, ModernStyle.ACCENT_GREEN)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = self.create_modern_button(search_frame, "🔄 Refresh", 
                                               self.load_payments, ModernStyle.ACCENT_BLUE)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        self.setup_treeview(main_frame)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        button_frame.pack(fill=tk.X, pady=15)
        
        buttons = [
            ("✅ Mark Paid", self.mark_as_paid, ModernStyle.ACCENT_GREEN),
            ("👁️ View Details", self.view_details, ModernStyle.ACCENT_BLUE),
            ("🗑️ Delete", self.delete_payment, ModernStyle.ACCENT_RED),
            ("📊 Export", self.export_excel, ModernStyle.ACCENT_PURPLE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        
        for text, cmd, color in buttons:
            btn = self.create_modern_button(button_frame, text, cmd, color, 110)
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
        
        columns = ("ID", "Customer", "Invoice #", "Due Date", "Amount", "Paid", "Pending", "Status")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", 
                                 height=15, style="Treeview")
        
        column_widths = [50, 200, 100, 100, 120, 120, 120, 100]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Demo data - replace with actual DB query
        demo_data = [
            (1, "Rajesh Electricals", "INV-001", "2026-03-15", 25000, 10000, 15000, "Partial"),
            (2, "Gupta Enterprises", "INV-002", "2026-02-28", 18000, 0, 18000, "Pending"),
            (3, "Sharma Construction", "INV-003", "2026-02-10", 32000, 32000, 0, "Paid"),
        ]
        
        total_pending = 0
        total_overdue = 0
        today = datetime.now().date()
        
        for row in demo_data:
            due_date = datetime.strptime(row[3], "%Y-%m-%d").date()
            pending = row[6]
            total_pending += pending
            
            if due_date < today and row[7] in ["Pending", "Partial"]:
                total_overdue += pending
            
            self.tree.insert("", "end", values=row)
        
        self.total_pending_var.set(f"Rs. {total_pending:,.2f}")
        self.total_overdue_var.set(f"Rs. {total_overdue:,.2f}")
    
    def on_search(self, event=None):
        search_term = self.search_var.get().lower()
        self.load_payments()
        if not search_term:
            return
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if not any(search_term in str(v).lower() for v in values[1:3]):
                self.tree.delete(item)
    
    def add_payment(self):
        messagebox.showinfo("Coming Soon", "Add Payment form will be modernized in Phase 3")
    
    def mark_as_paid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to mark as paid")
            return
        messagebox.showinfo("Coming Soon", "Mark as Paid will be modernized in Phase 3")
    
    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to view")
            return
        messagebox.showinfo("Coming Soon", "View Details will be modernized in Phase 3")
    
    def delete_payment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to delete")
            return
        messagebox.showinfo("Coming Soon", "Delete Payment will be modernized in Phase 3")
    
    def export_excel(self):
        messagebox.showinfo("Coming Soon", "Excel Export will be modernized in Phase 3")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = PendingWindow(root)
    root.mainloop()