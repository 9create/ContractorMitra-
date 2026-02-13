"""
PENDING PAYMENTS WINDOW - ContractorMitra
FULLY PRODUCTION READY + MODERN APPLE UI
Version: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
    ACCENT_RED = "#e74c3c"
    ACCENT_PURPLE = "#9b59b6"

    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)

class PendingWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Pending Payments - ContractorMitra")
        self.window.geometry("1200x700")
        self.window.configure(bg=ModernStyle.BG_COLOR)

        self.center_window()
        self.setup_ui()
        self.load_payments()

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
        tk.Label(header, text="💰 Pending Payments", font=ModernStyle.FONT_HEADER,
                 fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT)

        # Summary Card
        card = tk.Frame(main, bg="white", relief=tk.FLAT)
        card.pack(fill=tk.X, pady=(0,20))

        inner = tk.Frame(card, bg="white")
        inner.pack(fill=tk.X, padx=20, pady=15)

        self.total_pending_var = tk.StringVar(value="Rs. 0.00")
        self.total_overdue_var = tk.StringVar(value="Rs. 0.00")

        tk.Label(inner, text="Total Pending:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_SECONDARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        tk.Label(inner, textvariable=self.total_pending_var, font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.ACCENT_RED, bg="white").pack(side=tk.LEFT, padx=(0,20))

        tk.Label(inner, text="Overdue:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_SECONDARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        tk.Label(inner, textvariable=self.total_overdue_var, font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.ACCENT_ORANGE, bg="white").pack(side=tk.LEFT)

        # Search + Action Row
        row1 = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        row1.pack(fill=tk.X, pady=(0,15))

        tk.Label(row1, text="🔍 Search:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR).pack(side=tk.LEFT, padx=(0,10))

        self.search_var = tk.StringVar()
        tk.Entry(row1, textvariable=self.search_var, font=ModernStyle.FONT_NORMAL,
                 relief=tk.FLAT, highlightthickness=1, highlightbackground="#ddd", width=30).pack(side=tk.LEFT, padx=(0,10))
        self.search_var.trace('w', lambda *a: self.load_payments())

        self.create_modern_button(row1, "+ Add Payment", self.add_payment, ModernStyle.ACCENT_GREEN).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(row1, "🔄 Refresh", self.load_payments, ModernStyle.ACCENT_BLUE).pack(side=tk.LEFT, padx=5)

        # Treeview
        self.setup_treeview(main)

        # Action Buttons
        row2 = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        row2.pack(fill=tk.X, pady=15)

        actions = [
            ("✅ Mark Paid", self.mark_as_paid, ModernStyle.ACCENT_GREEN),
            ("👁️ Details", self.view_details, ModernStyle.ACCENT_BLUE),
            ("🗑️ Delete", self.delete_payment, ModernStyle.ACCENT_RED),
            ("📊 Export Excel", self.export_excel, ModernStyle.ACCENT_PURPLE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        for txt, cmd, col in actions:
            self.create_modern_button(row2, txt, cmd, col, 120).pack(side=tk.LEFT, padx=5)

    def setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=ModernStyle.TEXT_PRIMARY,
                        rowheight=30, fieldbackground="white", font=ModernStyle.FONT_NORMAL)
        style.configure("Treeview.Heading", background=ModernStyle.BG_COLOR,
                        foreground=ModernStyle.TEXT_PRIMARY, font=("SF Pro Text", 11, "bold"))
        style.map("Treeview", background=[("selected", ModernStyle.ACCENT_BLUE)])

        cols = ("ID", "Customer", "Quotation", "Due Date", "Amount", "Paid", "Pending", "Status")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=14, style="Treeview")
        widths = [50,200,100,100,120,120,120,100]
        for col,w in zip(cols,widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # ---------- DATABASE OPERATIONS ----------
    def load_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT p.id, c.name, p.quotation_id, p.due_date,
                   p.amount, p.paid_amount, p.pending_amount, p.status
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.id
            ORDER BY p.due_date
        ''')
        rows = cur.fetchall()
        conn.close()

        total_pending = 0
        total_overdue = 0
        today = datetime.now().date()
        search = self.search_var.get().lower()

        for r in rows:
            if search and search not in str(r[1]).lower():
                continue
            due = datetime.strptime(r[3], "%Y-%m-%d").date()
            pending = r[6]
            total_pending += pending
            if due < today and r[7] in ("pending","partial"):
                total_overdue += pending

            self.tree.insert("", "end", values=(
                r[0], r[1], r[2] or "-", r[3],
                f"Rs. {r[4]:,.2f}", f"Rs. {r[5]:,.2f}",
                f"Rs. {r[6]:,.2f}", r[7].title()
            ))

        self.total_pending_var.set(f"Rs. {total_pending:,.2f}")
        self.total_overdue_var.set(f"Rs. {total_overdue:,.2f}")

    # ---------- ADD PAYMENT ----------
    def add_payment(self):
        win = tk.Toplevel(self.window)
        win.title("Add Payment")
        win.geometry("450x450")
        win.configure(bg="white")
        tk.Label(win, text="➕ Add Payment", font=ModernStyle.FONT_TITLE, bg="white").pack(pady=10)

        # Customer dropdown
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM customers ORDER BY name")
        cust_list = cur.fetchall()
        conn.close()
        cust_names = [f"{c[1]} (ID:{c[0]})" for c in cust_list]
        cust_var = tk.StringVar()
        tk.Label(win, text="Customer *", bg="white").pack()
        cust_menu = ttk.Combobox(win, textvariable=cust_var, values=cust_names, width=40)
        cust_menu.pack(pady=5)

        fields = {}
        for label,key in [("Quotation #","qt"), ("Amount *","amt"), ("Paid","paid"), ("Due Date *","due")]:
            f = tk.Frame(win, bg="white")
            f.pack(pady=5)
            tk.Label(f, text=label, width=12, anchor='w', bg="white").pack(side=tk.LEFT)
            e = tk.Entry(f, width=25)
            e.pack(side=tk.LEFT)
            if key=="due":
                e.insert(0, datetime.now().strftime("%Y-%m-%d"))
            if key=="paid":
                e.insert(0, "0")
            fields[key] = e

        def save():
            if not cust_var.get():
                messagebox.showerror("Error","Select customer")
                return
            try:
                cust_id = int(cust_var.get().split("ID:")[1].replace(")",""))
                amt = float(fields['amt'].get() or 0)
                paid = float(fields['paid'].get() or 0)
                pending = amt - paid
                status = "paid" if pending<=0 else "partial" if paid>0 else "pending"
                conn = sqlite3.connect('contractormitra.db')
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO payments (customer_id, quotation_id, amount, paid_amount, pending_amount, due_date, status)
                    VALUES (?,?,?,?,?,?,?)
                ''', (cust_id, fields['qt'].get() or None, amt, paid, pending, fields['due'].get(), status))
                conn.commit()
                conn.close()
                win.destroy()
                self.load_payments()
                messagebox.showinfo("Success","Payment added")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save, bg=ModernStyle.ACCENT_GREEN, fg="white").pack(pady=10)

    # ---------- MARK AS PAID ----------
    def mark_as_paid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning","Select a payment")
            return
        vals = self.tree.item(sel[0])['values']
        pid = vals[0]
        if not messagebox.askyesno("Confirm","Mark this payment as paid?"):
            return
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            UPDATE payments SET status='paid', paid_amount=amount, pending_amount=0, payment_date=?
            WHERE id=?
        ''', (datetime.now().strftime("%Y-%m-%d"), pid))
        conn.commit()
        conn.close()
        self.load_payments()
        messagebox.showinfo("Success","Payment marked as paid")

    # ---------- VIEW DETAILS ----------
    def view_details(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning","Select a payment")
            return
        vals = self.tree.item(sel[0])['values']
        pid = vals[0]
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT p.*, c.name, c.phone, c.email
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE p.id=?
        ''', (pid,))
        p = cur.fetchone()
        conn.close()
        if not p:
            return

        win = tk.Toplevel(self.window)
        win.title("Payment Details")
        win.geometry("500x450")
        win.configure(bg="white")
        tk.Label(win, text="🧾 Payment Details", font=ModernStyle.FONT_TITLE, bg="white").pack(pady=10)

        details = [
            ("Payment ID:", p[0]),
            ("Customer:", p[13]),
            ("Phone:", p[14] or "-"),
            ("Email:", p[15] or "-"),
            ("Quotation:", p[2] or "-"),
            ("Amount:", f"Rs. {p[4]:,.2f}"),
            ("Paid:", f"Rs. {p[5]:,.2f}"),
            ("Pending:", f"Rs. {p[6]:,.2f}"),
            ("Due Date:", p[7]),
            ("Payment Date:", p[8] or "Not paid"),
            ("Status:", p[9].title()),
            ("Reference:", p[10] or "-"),
            ("Remarks:", p[11] or "-")
        ]
        for lab, val in details:
            f = tk.Frame(win, bg="white")
            f.pack(fill=tk.X, padx=20, pady=2)
            tk.Label(f, text=lab, width=15, anchor='w', bg="white", font=ModernStyle.FONT_SMALL).pack(side=tk.LEFT)
            tk.Label(f, text=val, anchor='w', bg="white", font=ModernStyle.FONT_SMALL).pack(side=tk.LEFT, padx=10)

        tk.Button(win, text="Close", command=win.destroy, bg=ModernStyle.TEXT_SECONDARY, fg="white").pack(pady=10)

    # ---------- DELETE ----------
    def delete_payment(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning","Select a payment")
            return
        if not messagebox.askyesno("Confirm","Permanently delete this payment?"):
            return
        pid = self.tree.item(sel[0])['values'][0]
        conn = sqlite3.connect('contractormitra.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM payments WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        self.load_payments()
        messagebox.showinfo("Success","Payment deleted")

    # ---------- EXPORT EXCEL ----------
    def export_excel(self):
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
        if not file:
            return
        data = []
        for child in self.tree.get_children():
            vals = self.tree.item(child)['values']
            data.append(vals)
        if not data:
            messagebox.showwarning("No Data","Nothing to export")
            return
        cols = ("ID","Customer","Quotation","Due Date","Amount","Paid","Pending","Status")
        df = pd.DataFrame(data, columns=cols)
        df.to_excel(file, index=False)
        messagebox.showinfo("Success",f"Exported to {file}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = PendingWindow(root)
    root.mainloop()