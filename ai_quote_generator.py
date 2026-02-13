"""
AI QUOTE GENERATOR - ContractorMitra
FULLY PRODUCTION READY + MODERN APPLE UI
Version: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from datetime import datetime
import os

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
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)

class AIQuoteGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("AI Quote Generator - ContractorMitra")
        self.window.geometry("1100x750")
        self.window.configure(bg=ModernStyle.BG_COLOR)

        self.items = []
        self.selected_customer_id = None
        self.customer_name = None
        self.customer_phone = None
        self.customer_address = None
        self.customer_gstin = None

        self.center_window()
        self.setup_ui()
        self.load_materials()
        self.load_customers()

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
        tk.Label(header, text="🤖 AI Quote Generator", font=ModernStyle.FONT_HEADER,
                 fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR).pack()
        tk.Label(header, text="Pure AI – Rule Based Intelligent Quotation",
                 font=ModernStyle.FONT_NORMAL, fg=ModernStyle.TEXT_SECONDARY,
                 bg=ModernStyle.BG_COLOR).pack()

        # Customer Card
        cust_card = tk.Frame(main, bg="white", relief=tk.FLAT)
        cust_card.pack(fill=tk.X, pady=(0,20))
        inner_cust = tk.Frame(cust_card, bg="white")
        inner_cust.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(inner_cust, text="👤 Customer", font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(anchor=tk.W, pady=(0,10))

        row = tk.Frame(inner_cust, bg="white")
        row.pack(fill=tk.X)
        tk.Label(row, text="Select Customer:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(side=tk.LEFT, padx=(0,10))

        self.customer_combo = ttk.Combobox(row, width=50, font=ModernStyle.FONT_NORMAL)
        self.customer_combo.pack(side=tk.LEFT, padx=(0,10))
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_select)

        self.create_modern_button(row, "+ New Customer", self.open_customer_window,
                                  ModernStyle.ACCENT_GREEN, 130).pack(side=tk.LEFT)

        self.customer_info_var = tk.StringVar(value="👤 No customer selected")
        tk.Label(inner_cust, textvariable=self.customer_info_var,
                 font=ModernStyle.FONT_SMALL, fg=ModernStyle.ACCENT_BLUE,
                 bg="white").pack(anchor=tk.W, pady=(10,0))

        # Project Description Card
        desc_card = tk.Frame(main, bg="white", relief=tk.FLAT)
        desc_card.pack(fill=tk.X, pady=(0,20))
        inner_desc = tk.Frame(desc_card, bg="white")
        inner_desc.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(inner_desc, text="📝 Project Description", font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(anchor=tk.W, pady=(0,10))

        self.project_desc = tk.Text(inner_desc, height=5, font=ModernStyle.FONT_NORMAL,
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground="#ddd")
        self.project_desc.pack(fill=tk.X)

        examples = ("📌 EXAMPLES:\n"
                    "• 5000 sqft factory wiring, 20 LED lights, 15 sockets, 2 fans, 3 phase MCB\n"
                    "• 2 BHK flat wiring, 10 lights, 8 sockets, 4 fans, modular switches\n"
                    "• 100m 25sqmm copper cable, 2 industrial MCB 63A, 1 distribution board")
        tk.Label(inner_desc, text=examples, font=ModernStyle.FONT_SMALL,
                 fg=ModernStyle.TEXT_SECONDARY, bg="white", justify=tk.LEFT).pack(pady=(10,0), anchor=tk.W)

        # Generate Button
        btn_frame = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        btn_frame.pack(pady=10)
        self.create_modern_button(btn_frame, "⚡ GENERATE QUOTATION ⚡",
                                  self.generate_ai_quote, ModernStyle.ACCENT_GREEN, 280).pack()

        # Items Treeview
        tree_card = tk.Frame(main, bg="white", relief=tk.FLAT)
        tree_card.pack(fill=tk.BOTH, expand=True, pady=(0,20))
        inner_tree = tk.Frame(tree_card, bg="white")
        inner_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(inner_tree, text="📋 Quotation Items", font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(anchor=tk.W, pady=(0,10))

        self.setup_treeview(inner_tree)

        # Totals
        total_frame = tk.Frame(inner_tree, bg="white")
        total_frame.pack(fill=tk.X, pady=(10,0))

        self.subtotal_var = tk.StringVar(value="Rs. 0.00")
        self.gst_var = tk.StringVar(value="Rs. 0.00")
        self.total_var = tk.StringVar(value="Rs. 0.00")

        tk.Label(total_frame, text="SUBTOTAL:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        tk.Label(total_frame, textvariable=self.subtotal_var, font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.ACCENT_GREEN, bg="white").pack(side=tk.LEFT, padx=(0,20))

        tk.Label(total_frame, text="GST (18%):", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        tk.Label(total_frame, textvariable=self.gst_var, font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.ACCENT_ORANGE, bg="white").pack(side=tk.LEFT, padx=(0,20))

        tk.Label(total_frame, text="GRAND TOTAL:", font=ModernStyle.FONT_NORMAL,
                 fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(side=tk.LEFT, padx=(0,5))
        tk.Label(total_frame, textvariable=self.total_var, font=ModernStyle.FONT_TITLE,
                 fg=ModernStyle.ACCENT_RED, bg="white").pack(side=tk.LEFT)

        # Action Buttons
        action_row = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        action_row.pack(fill=tk.X, pady=10)

        actions = [
            ("💾 Save Quotation", self.save_quotation, ModernStyle.ACCENT_BLUE),
            ("📄 Generate PDF", self.generate_pdf, ModernStyle.ACCENT_ORANGE),
            ("🔄 Reset All", self.clear_all, ModernStyle.TEXT_SECONDARY),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        for txt, cmd, col in actions:
            self.create_modern_button(action_row, txt, cmd, col, 140).pack(side=tk.LEFT, padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="✅ Ready. Select customer and describe project.")
        tk.Label(main, textvariable=self.status_var, font=ModernStyle.FONT_SMALL,
                 fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR,
                 anchor=tk.W).pack(fill=tk.X, pady=(10,0))

    def setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=ModernStyle.TEXT_PRIMARY,
                        rowheight=28, fieldbackground="white", font=ModernStyle.FONT_NORMAL)
        style.configure("Treeview.Heading", background=ModernStyle.BG_COLOR,
                        foreground=ModernStyle.TEXT_PRIMARY, font=("SF Pro Text", 11, "bold"))
        style.map("Treeview", background=[("selected", ModernStyle.ACCENT_BLUE)])

        cols = ("Item", "Description", "Qty", "Unit", "Rate (Rs.)", "Amount (Rs.)", "GST%")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=6, style="Treeview")
        widths = [120,250,60,70,100,110,60]
        for col,w in zip(cols,widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)

        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # ---------- LOAD DATA ----------
    def load_materials(self):
        try:
            conn = sqlite3.connect('contractormitra.db')
            cur = conn.cursor()
            cur.execute("SELECT name, default_rate, default_unit FROM materials")
            self.materials = cur.fetchall()
            conn.close()
            self.material_dict = {m[0].lower(): (m[1], m[2]) for m in self.materials}
        except:
            self.materials = []
            self.material_dict = {}

    def load_customers(self):
        try:
            conn = sqlite3.connect('contractormitra.db')
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, address, gstin FROM customers ORDER BY name")
            cust = cur.fetchall()
            conn.close()
            self.customer_details = {}
            cust_list = []
            for c in cust:
                disp = f"{c[1]} - {c[2] if c[2] else 'No Phone'}"
                cust_list.append(disp)
                self.customer_details[disp] = {
                    'id':c[0], 'name':c[1], 'phone':c[2] or '',
                    'address':c[3] or '', 'gstin':c[4] or ''
                }
            self.customer_combo['values'] = cust_list
        except Exception as e:
            self.status_var.set(f"❌ Error loading customers")

    def on_customer_select(self, event):
        sel = self.customer_combo.get()
        if sel and sel in self.customer_details:
            d = self.customer_details[sel]
            self.selected_customer_id = d['id']
            self.customer_name = d['name']
            self.customer_phone = d['phone']
            self.customer_address = d['address']
            self.customer_gstin = d['gstin']
            info = f"✓ {self.customer_name}"
            if self.customer_phone: info += f" | 📞 {self.customer_phone}"
            if self.customer_gstin: info += f" | GST: {self.customer_gstin}"
            self.customer_info_var.set(info)
            self.status_var.set(f"✅ Customer: {self.customer_name}")

    def open_customer_window(self):
        try:
            from customer_window import CustomerWindow
            cw = CustomerWindow(self.window, mode='add')
            self.window.wait_window(cw.window)
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- AI RULE ENGINE ----------
    def generate_ai_quote(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "❌ Select a customer first")
            return
        desc = self.project_desc.get("1.0", tk.END).strip()
        if not desc:
            messagebox.showwarning("Warning", "❌ Enter project description")
            return

        self.status_var.set("⏳ AI processing...")
        self.window.update()

        for i in self.tree.get_children():
            self.tree.delete(i)
        self.items = []

        d = desc.lower()
        added = 0

        # 1. Wires
        if 'wire' in d or 'cable' in d:
            qty = self.extract_qty(d, ['wire','cable'])
            if qty>0:
                self.add_item("1.5 sq.mm Copper Wire", "PVC insulated", qty, "meter", 48.0)
                added+=1
                if 'power' in d or '3 phase' in d:
                    self.add_item("2.5 sq.mm Copper Wire", "Heavy duty", qty//2, "meter", 65.0)
                    added+=1

        # 2. Lights
        if 'light' in d or 'led' in d:
            qty = self.extract_qty(d, ['light','led'])
            if qty>0:
                self.add_item("LED Panel Light 18W", "LED panel", qty, "piece", 450.0)
                added+=1

        # 3. Fans
        if 'fan' in d:
            qty = self.extract_qty(d, ['fan'])
            if qty>0:
                self.add_item("Ceiling Fan", "1200mm with regulator", qty, "piece", 1500.0)
                added+=1

        # 4. Sockets
        if 'socket' in d:
            qty = self.extract_qty(d, ['socket'])
            if qty>0:
                self.add_item("15A Socket", "power socket", qty, "piece", 150.0)
                self.add_item("5A Socket", "switch socket", qty, "piece", 120.0)
                added+=2

        # 5. Switches
        if 'switch' in d or 'modular' in d:
            qty = self.extract_qty(d, ['switch','modular'])
            if qty==0:
                qty = self.extract_qty(d, ['socket']) + 5
            self.add_item("Modular Switch 1-Gang", "modular switch", qty, "piece", 180.0)
            added+=1

        # 6. MCB / DB
        if 'mcb' in d or 'distribution' in d:
            self.add_item("6A MCB", "SP MCB", 4, "piece", 200.0)
            self.add_item("Distribution Box 8-way", "DB", 1, "piece", 800.0)
            added+=2
            if '3 phase' in d or 'industrial' in d:
                self.add_item("Industrial MCB 63A", "3 phase MCB", 1, "piece", 850.0)
                added+=1

        # 7. Conduit
        if 'conduit' in d or 'pipe' in d:
            qty = self.extract_qty(d, ['conduit','pipe'])
            if qty>0:
                self.add_item("20mm PVC Conduit", "conduit pipe", qty, "meter", 30.0)
                added+=1

        # 8. Labour
        area = self.extract_qty(d, ['sqft','square'])
        if area>0:
            pts = max(5, area//150)
        else:
            pts = max(5, len(self.items))
        self.add_item("Electrical Labour", "installation labour", pts, "point", 300.0)
        added+=1

        self.calc_totals()

        if added>0:
            self.status_var.set(f"✅ AI generated {added} items")
            messagebox.showinfo("Success", f"{added} items generated\nSubtotal: {self.subtotal_var.get()}")
        else:
            self.status_var.set("❌ No items matched – be more descriptive")

    def extract_qty(self, text, keys):
        q=0
        for k in keys:
            m = re.findall(r'(\d+)\s*'+re.escape(k), text)
            for x in m:
                q+=int(x)
        return q

    def add_item(self, name, desc, qty, unit, rate):
        if qty<=0:
            return
        for item in self.items:
            if item['name']==name and item['rate']==rate:
                item['quantity']+=qty
                item['amount']=item['quantity']*rate
                self.refresh_tree()
                self.status_var.set(f"🔄 Updated {name} +{qty}")
                return
        amt = qty*rate
        self.items.append({'name':name,'description':desc,'quantity':qty,
                           'unit':unit,'rate':rate,'amount':amt})
        self.tree.insert("","end", values=(name[:20], desc[:30], qty, unit,
                                           f"Rs. {rate:,.2f}", f"Rs. {amt:,.2f}", "18%"))
        self.status_var.set(f"✅ Added {name} x{qty}")

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for it in self.items:
            self.tree.insert("","end", values=(it['name'][:20], it['description'][:30],
                                               it['quantity'], it['unit'],
                                               f"Rs. {it['rate']:,.2f}",
                                               f"Rs. {it['amount']:,.2f}", "18%"))

    def calc_totals(self):
        sub = sum(i['amount'] for i in self.items)
        gst = sub*0.18
        tot = sub+gst
        self.subtotal_var.set(f"Rs. {sub:,.2f}")
        self.gst_var.set(f"Rs. {gst:,.2f}")
        self.total_var.set(f"Rs. {tot:,.2f}")

    # ---------- SAVE ----------
    def save_quotation(self):
        if not self.selected_customer_id:
            messagebox.showwarning("Warning","Select customer")
            return
        if not self.items:
            messagebox.showwarning("Warning","Generate items first")
            return
        try:
            conn = sqlite3.connect('contractormitra.db')
            cur = conn.cursor()
            sub = sum(i['amount'] for i in self.items)
            gst = sub*0.18
            total = sub+gst
            dstr = datetime.now().strftime('%Y%m%d')
            cur.execute("SELECT COUNT(*) FROM quotations WHERE quote_no LIKE ?", (f"QT-{dstr}-%",))
            cnt = cur.fetchone()[0]+1
            qno = f"QT-{dstr}-{cnt:03d}"
            cur.execute('''
                INSERT INTO quotations (quote_no, date, customer_id, subtotal, gst_amount, grand_total, status)
                VALUES (?,?,?,?,?,?,?)
            ''', (qno, datetime.now().strftime('%Y-%m-%d'), self.selected_customer_id,
                  sub, gst, total, 'Draft'))
            qid = cur.lastrowid
            for it in self.items:
                cur.execute('''
                    INSERT INTO quotation_items (quotation_id, item_name, description, quantity, unit, rate, amount)
                    VALUES (?,?,?,?,?,?,?)
                ''', (qid, it['name'], it['description'], it['quantity'],
                      it['unit'], it['rate'], it['amount']))
            conn.commit()
            conn.close()
            self.status_var.set(f"✅ Quotation {qno} saved")
            messagebox.showinfo("Success", f"Quotation {qno} saved")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- PDF ----------
    def generate_pdf(self):
        if not self.items:
            messagebox.showwarning("Warning","Generate items first")
            return
        try:
            from pdf_generator import PDFGenerator
            sub = sum(i['amount'] for i in self.items)
            gst = sub*0.18
            total = sub+gst
            data = {
                'quote_no': f"AI-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'date': datetime.now().strftime('%d-%b-%Y'),
                'customer_name': self.customer_name or "Customer",
                'customer_phone': self.customer_phone or "",
                'customer_address': self.customer_address or "",
                'customer_gstin': self.customer_gstin or "",
                'subtotal': sub,
                'gst_amount': gst,
                'grand_total': total,
                'items': self.items
            }
            pdf = PDFGenerator()
            fname = f"quotation_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            self.status_var.set("⏳ Generating PDF...")
            self.window.update()
            ok = pdf.generate_quotation_pdf_from_dict(data, fname)
            if ok:
                self.status_var.set(f"✅ PDF saved: {fname}")
                if messagebox.askyesno("Open PDF", "Open PDF now?"):
                    os.startfile(fname)
            else:
                messagebox.showerror("Error","PDF generation failed")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- RESET ----------
    def clear_all(self):
        self.project_desc.delete("1.0", tk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.items = []
        self.selected_customer_id = None
        self.customer_name = None
        self.customer_phone = None
        self.customer_address = None
        self.customer_gstin = None
        self.customer_combo.set('')
        self.customer_info_var.set("👤 No customer selected")
        self.subtotal_var.set("Rs. 0.00")
        self.gst_var.set("Rs. 0.00")
        self.total_var.set("Rs. 0.00")
        self.status_var.set("✅ Reset complete")
        self.load_customers()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AIQuoteGenerator(root)
    root.mainloop()