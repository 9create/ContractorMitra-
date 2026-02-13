"""
REPORTS WINDOW - ContractorMitra
FULLY PRODUCTION READY + MODERN APPLE UI
Version: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

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
    ACCENT_TEAL = "#1abc9c"

    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_SUBTITLE = ("SF Pro Display", 14)
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reports Dashboard - ContractorMitra")
        self.window.geometry("1300x750")
        self.window.configure(bg=ModernStyle.BG_COLOR)

        self.report_type = tk.StringVar(value="sales")
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()

        today = datetime.now()
        first = today.replace(day=1)
        self.date_from.set(first.strftime("%Y-%m-%d"))
        self.date_to.set(today.strftime("%Y-%m-%d"))

        self.current_data = []
        self.current_columns = []

        self.center_window()
        self.setup_ui()
        self.generate_report()

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f'{w}x{h}+{x}+{y}')

    # ---------- MODERN BUTTON ----------
    def create_modern_button(self, parent, text, command, color=ModernStyle.ACCENT_BLUE, width=140):
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

    # ---------- UI ----------
    def setup_ui(self):
        main = tk.Frame(self.window, bg=ModernStyle.BG_COLOR)
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Header
        header = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        header.pack(fill=tk.X, pady=(0,20))
        tk.Label(header, text="📊 Reports Dashboard", font=ModernStyle.FONT_HEADER,
                 fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT)

        # Controls Card
        card = tk.Frame(main, bg="white", relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0,20))

        inner = tk.Frame(card, bg="white")
        inner.pack(fill=tk.X, padx=20, pady=15)

        # Report Type Row
        row1 = tk.Frame(inner, bg="white")
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Report Type:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(side=tk.LEFT, padx=(0,20))

        reports = [
            ("💰 Sales", "sales"),
            ("📊 Pending", "pending"),
            ("👥 Customers", "customers"),
            ("📦 Materials", "materials"),
            ("📈 Monthly", "monthly")
        ]
        for txt, val in reports:
            rb = tk.Radiobutton(row1, text=txt, variable=self.report_type, value=val,
                                font=ModernStyle.FONT_NORMAL, bg="white", selectcolor="white",
                                activebackground="white", command=self.generate_report)
            rb.pack(side=tk.LEFT, padx=10)

        # Date Range Row
        row2 = tk.Frame(inner, bg="white")
        row2.pack(fill=tk.X, pady=10)

        tk.Label(row2, text="From:", font=ModernStyle.FONT_SMALL,
                 fg=ModernStyle.TEXT_SECONDARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        e1 = tk.Entry(row2, textvariable=self.date_from, width=12,
                      font=ModernStyle.FONT_NORMAL, relief=tk.FLAT,
                      highlightthickness=1, highlightbackground="#ddd")
        e1.pack(side=tk.LEFT, padx=5)

        tk.Label(row2, text="To:", font=ModernStyle.FONT_SMALL,
                 fg=ModernStyle.TEXT_SECONDARY, bg="white").pack(side=tk.LEFT, padx=(10,5))
        e2 = tk.Entry(row2, textvariable=self.date_to, width=12,
                      font=ModernStyle.FONT_NORMAL, relief=tk.FLAT,
                      highlightthickness=1, highlightbackground="#ddd")
        e2.pack(side=tk.LEFT, padx=5)

        # Quick Date Buttons
        row3 = tk.Frame(inner, bg="white")
        row3.pack(fill=tk.X, pady=5)
        periods = [("Today",0), ("7 Days",7), ("This Month",30), ("Last Month",60), ("This Year",365)]
        for txt, days in periods:
            btn = self.create_modern_button(row3, txt, lambda d=days: self.set_quick_date(d),
                                            ModernStyle.TEXT_SECONDARY, 100)
            btn.pack(side=tk.LEFT, padx=5)

        # Treeview
        self.setup_treeview(main)

        # Summary + Export Row
        row4 = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        row4.pack(fill=tk.X, pady=10)

        self.summary_var = tk.StringVar(value="")
        tk.Label(row4, textvariable=self.summary_var, font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.ACCENT_BLUE, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT, padx=5)

        self.create_modern_button(row4, "📊 Excel", self.export_excel, ModernStyle.ACCENT_GREEN, 100).pack(side=tk.RIGHT, padx=5)
        self.create_modern_button(row4, "📄 PDF", self.export_pdf, ModernStyle.ACCENT_ORANGE, 100).pack(side=tk.RIGHT, padx=5)
        self.create_modern_button(row4, "❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY, 100).pack(side=tk.RIGHT, padx=5)

    def setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=ModernStyle.TEXT_PRIMARY,
                        rowheight=30, fieldbackground="white", font=ModernStyle.FONT_NORMAL)
        style.configure("Treeview.Heading", background=ModernStyle.BG_COLOR,
                        foreground=ModernStyle.TEXT_PRIMARY, font=("SF Pro Text", 11, "bold"))
        style.map("Treeview", background=[("selected", ModernStyle.ACCENT_BLUE)])

        self.tree = ttk.Treeview(parent, show="headings", height=14, style="Treeview")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

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

    # ---------- REPORT GENERATORS (ALL REAL DATA) ----------
    def generate_report(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.current_data = []
        self.current_columns = []
        rtype = self.report_type.get()
        if rtype == "sales":
            self.generate_sales()
        elif rtype == "pending":
            self.generate_pending()
        elif rtype == "customers":
            self.generate_customers()
        elif rtype == "materials":
            self.generate_materials()
        elif rtype == "monthly":
            self.generate_monthly()

    # ---------- 1. SALES REPORT ----------
    def generate_sales(self):
        cols = ("Invoice #", "Date", "Customer", "Subtotal", "GST", "Total", "Status")
        self._set_cols(cols)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT q.quote_no, q.date, c.name, q.subtotal, q.gst_amount, q.grand_total, q.status
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.date BETWEEN ? AND ?
            ORDER BY q.date DESC
        ''', (self.date_from.get(), self.date_to.get()))
        rows = cur.fetchall()
        conn.close()
        total_sales = 0
        for r in rows:
            total_sales += r[5] or 0
            self.tree.insert("", "end", values=r)
            self.current_data.append(r)
        self.summary_var.set(f"Total Sales: Rs. {total_sales:,.2f}  |  Invoices: {len(rows)}")

    # ---------- 2. PENDING PAYMENTS REPORT ----------
    def generate_pending(self):
        cols = ("Invoice #", "Date", "Customer", "Amount", "Status")
        self._set_cols(cols)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT q.quote_no, q.date, c.name, q.grand_total, q.status
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.status IN ('Draft','Sent') AND q.date BETWEEN ? AND ?
            ORDER BY q.date
        ''', (self.date_from.get(), self.date_to.get()))
        rows = cur.fetchall()
        conn.close()
        total = 0
        for r in rows:
            total += r[3] or 0
            self.tree.insert("", "end", values=r)
            self.current_data.append(r)
        self.summary_var.set(f"Total Pending: Rs. {total:,.2f}")

    # ---------- 3. CUSTOMER REPORT ----------
    def generate_customers(self):
        cols = ("Customer", "Phone", "Email", "Invoices", "Total Spent")
        self._set_cols(cols)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT c.name, c.phone, c.email,
                   COUNT(q.id),
                   COALESCE(SUM(q.grand_total),0)
            FROM customers c
            LEFT JOIN quotations q ON c.id = q.customer_id
            GROUP BY c.id
            ORDER BY 5 DESC
        ''')
        rows = cur.fetchall()
        conn.close()
        total_spent = 0
        for r in rows:
            total_spent += r[4]
            self.tree.insert("", "end", values=r)
            self.current_data.append(r)
        self.summary_var.set(f"Total Revenue: Rs. {total_spent:,.2f} | Customers: {len(rows)}")

    # ---------- 4. MATERIAL CONSUMPTION REPORT ----------
    def generate_materials(self):
        cols = ("Material", "Unit", "Quantity", "Total Value")
        self._set_cols(cols)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT qi.item_name, qi.unit,
                   SUM(qi.quantity),
                   SUM(qi.amount)
            FROM quotation_items qi
            JOIN quotations q ON qi.quotation_id = q.id
            WHERE q.date BETWEEN ? AND ?
            GROUP BY qi.item_name
            ORDER BY 4 DESC
        ''', (self.date_from.get(), self.date_to.get()))
        rows = cur.fetchall()
        conn.close()
        total_val = 0
        for r in rows:
            total_val += r[3]
            self.tree.insert("", "end", values=r)
            self.current_data.append(r)
        self.summary_var.set(f"Total Material Value: Rs. {total_val:,.2f}")

    # ---------- 5. MONTHLY SUMMARY REPORT ----------
    def generate_monthly(self):
        cols = ("Month", "Invoices", "Sales", "GST", "Net")
        self._set_cols(cols)
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT strftime('%Y-%m', date),
                   COUNT(*),
                   COALESCE(SUM(grand_total),0),
                   COALESCE(SUM(gst_amount),0)
            FROM quotations
            WHERE date BETWEEN ? AND ?
            GROUP BY 1
            ORDER BY 1 DESC
        ''', (self.date_from.get(), self.date_to.get()))
        rows = cur.fetchall()
        conn.close()
        total_sales = 0
        for r in rows:
            net = r[2] - r[3]
            total_sales += r[2]
            display = (r[0], r[1], f"Rs. {r[2]:,.2f}", f"Rs. {r[3]:,.2f}", f"Rs. {net:,.2f}")
            self.tree.insert("", "end", values=display)
            self.current_data.append(r)
        self.summary_var.set(f"Total Sales: Rs. {total_sales:,.2f}")

    def _set_cols(self, cols):
        self.current_columns = cols
        self.tree['columns'] = cols
        self.tree['show'] = 'headings'
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)

    # ---------- EXPORT ----------
    def export_excel(self):
        if not self.current_data:
            messagebox.showwarning("No Data", "Generate a report first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not file:
            return
        df = pd.DataFrame(self.current_data, columns=self.current_columns)
        df.to_excel(file, index=False)
        messagebox.showinfo("Success", f"Exported to {file}")

    def export_pdf(self):
        if not self.current_data:
            messagebox.showwarning("No Data", "Generate a report first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not file:
            return
        doc = SimpleDocTemplate(file, pagesize=landscape(A4))
        story = []
        styles = getSampleStyleSheet()
        story.append(Paragraph("ContractorMitra - Report", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        data = [self.current_columns] + [list(map(str,r)) for r in self.current_data]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(ModernStyle.ACCENT_BLUE)),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]))
        story.append(t)
        doc.build(story)
        messagebox.showinfo("Success", f"Exported to {file}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = ReportsWindow(root)
    root.mainloop()