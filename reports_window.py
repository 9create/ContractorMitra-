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

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reports Dashboard - ContractorMitra")
        self.window.geometry("1200x700")
        
        # Variables
        self.report_type = tk.StringVar(value="sales")
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()
        
        # Set default dates
        today = datetime.now()
        first_day = today.replace(day=1)
        self.date_from.set(first_day.strftime("%Y-%m-%d"))
        self.date_to.set(today.strftime("%Y-%m-%d"))
        
        # Data storage
        self.current_data = []
        self.current_columns = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup reports window UI"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        tk.Label(main_frame, text="📊 REPORTS DASHBOARD", 
                font=("Arial", 20, "bold"), fg="#2c3e50").pack(pady=(0, 20))
        
        # Control Panel
        control_panel = tk.Frame(main_frame, relief=tk.GROOVE, bd=2, bg="#f8f9fa")
        control_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Report Type Section
        type_frame = tk.Frame(control_panel, bg="#f8f9fa")
        type_frame.pack(pady=10)
        
        tk.Label(type_frame, text="📋 Select Report:", font=("Arial", 11, "bold"), 
                bg="#f8f9fa").pack(side=tk.LEFT, padx=(10, 20))
        
        reports = [
            ("💰 Sales Report", "sales", "#3498db"),
            ("📊 Pending Payments", "pending", "#e74c3c"),
            ("👥 Customer Report", "customers", "#2ecc71"),
            ("📦 Material Consumption", "materials", "#f39c12"),
            ("📈 Monthly Summary", "monthly", "#9b59b6")
        ]
        
        for text, value, color in reports:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.report_type, 
                              value=value, font=("Arial", 10), bg="#f8f9fa",
                              command=self.on_report_change)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Date Range Section
        date_frame = tk.Frame(control_panel, bg="#f8f9fa")
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="📅 From:", font=("Arial", 10, "bold"), 
                bg="#f8f9fa").pack(side=tk.LEFT, padx=(10, 5))
        tk.Entry(date_frame, textvariable=self.date_from, width=12, 
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_frame, text="To:", font=("Arial", 10, "bold"), 
                bg="#f8f9fa").pack(side=tk.LEFT, padx=(10, 5))
        tk.Entry(date_frame, textvariable=self.date_to, width=12, 
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Quick Date Buttons
        quick_frame = tk.Frame(control_panel, bg="#f8f9fa")
        quick_frame.pack(pady=10)
        
        quick_periods = [
            ("Today", 0),
            ("Last 7 Days", 7),
            ("This Month", 30),
            ("Last Month", 60),
            ("This Year", 365)
        ]
        
        for text, days in quick_periods:
            tk.Button(quick_frame, text=text, width=12,
                     command=lambda d=days: self.set_quick_date(d),
                     bg="#34495e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        # Generate Button
        tk.Button(control_panel, text="🔍 GENERATE REPORT", 
                 command=self.generate_report,
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                 height=2, width=25).pack(pady=15)
        
        # Results Frame
        results_frame = tk.LabelFrame(main_frame, text="📑 Report Results", 
                                     font=("Arial", 12, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview Frame
        tree_frame = tk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, height=15)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Summary Frame
        self.summary_frame = tk.Frame(main_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=2)
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export Frame
        export_frame = tk.Frame(main_frame)
        export_frame.pack()
        
        tk.Button(export_frame, text="📊 Export to Excel", 
                 command=self.export_excel,
                 bg="#3498db", fg="white", width=15, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="📄 Export to PDF", 
                 command=self.export_pdf,
                 bg="#e67e22", fg="white", width=15, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="🖨️ Print", 
                 command=self.print_report,
                 bg="#95a5a6", fg="white", width=15, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="❌ Close", 
                 command=self.window.destroy,
                 bg="#e74c3c", fg="white", width=15, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def on_report_change(self):
        """Handle report type change"""
        self.generate_report()
    
    def set_quick_date(self, days):
        """Set quick date range"""
        today = datetime.now()
        self.date_to.set(today.strftime("%Y-%m-%d"))
        
        if days == 0:  # Today
            self.date_from.set(today.strftime("%Y-%m-%d"))
        elif days == 30:  # This month
            first_day = today.replace(day=1)
            self.date_from.set(first_day.strftime("%Y-%m-%d"))
        elif days == 60:  # Last month
            first_day_last = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last = today.replace(day=1) - timedelta(days=1)
            self.date_from.set(first_day_last.strftime("%Y-%m-%d"))
            self.date_to.set(last_day_last.strftime("%Y-%m-%d"))
        elif days == 365:  # This year
            first_day_year = today.replace(month=1, day=1)
            self.date_from.set(first_day_year.strftime("%Y-%m-%d"))
        else:  # Last N days
            from_date = today - timedelta(days=days)
            self.date_from.set(from_date.strftime("%Y-%m-%d"))
    
    def parse_currency(self, value):
        """Convert currency string to float"""
        if not value:
            return 0.0
        try:
            if isinstance(value, (int, float)):
                return float(value)
            return float(str(value).replace('₹', '').replace(',', '').replace(' ', ''))
        except:
            return 0.0
    
    def generate_report(self):
        """Generate selected report"""
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        self.current_data = []
        self.current_columns = []
        
        report_type = self.report_type.get()
        
        try:
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
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_sales_report(self):
        """Generate sales report"""
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT q.quote_no, q.date, c.name, q.subtotal, q.gst_amount, q.grand_total, q.status
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.date BETWEEN ? AND ? AND q.status NOT IN ('Cancelled')
            ORDER BY q.date DESC
        ''', (date_from, date_to))
        
        data = cursor.fetchall()
        conn.close()
        
        # Set columns
        columns = ("Quotation No", "Date", "Customer", "Subtotal (₹)", "GST (₹)", "Total (₹)", "Status")
        self.setup_treeview(columns)
        
        total_sales = 0
        total_gst = 0
        total_subtotal = 0
        
        for row in data:
            self.tree.insert("", "end", values=row)
            self.current_data.append(row)
            total_subtotal += self.parse_currency(row[3])
            total_gst += self.parse_currency(row[4])
            total_sales += self.parse_currency(row[5])
        
        # Summary
        summary_text = f"📊 SALES REPORT SUMMARY\n"
        summary_text += f"Period: {date_from} to {date_to}\n"
        summary_text += f"Total Invoices: {len(data)}\n"
        summary_text += f"Total Subtotal: ₹ {total_subtotal:,.2f}\n"
        summary_text += f"Total GST: ₹ {total_gst:,.2f}\n"
        summary_text += f"Total Sales: ₹ {total_sales:,.2f}"
        
        tk.Label(self.summary_frame, text=summary_text, font=("Arial", 11),
                justify=tk.LEFT, bg="#f0f0f0").pack(pady=10)
    
    def generate_pending_report(self):
        """Generate pending payments report"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT q.quote_no, q.date, c.name, q.grand_total, 
                   julianday('now') - julianday(q.date) as days_pending
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.status IN ('Sent', 'Draft')
            ORDER BY q.date ASC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        columns = ("Quotation No", "Date", "Customer", "Amount (₹)", "Days Pending")
        self.setup_treeview(columns)
        
        total_pending = 0
        overdue_count = 0
        total_overdue = 0
        
        for row in data:
            days = int(row[4]) if row[4] else 0
            values = (row[0], row[1], row[2], f"₹ {self.parse_currency(row[3]):,.2f}", f"{days} days")
            self.tree.insert("", "end", values=values)
            self.current_data.append(row)
            
            amount = self.parse_currency(row[3])
            total_pending += amount
            
            if days > 30:
                overdue_count += 1
                total_overdue += amount
        
        summary_text = f"💰 PENDING PAYMENTS REPORT\n"
        summary_text += f"Total Pending Invoices: {len(data)}\n"
        summary_text += f"Total Pending Amount: ₹ {total_pending:,.2f}\n"
        summary_text += f"Overdue (>30 days): {overdue_count} invoices\n"
        summary_text += f"Overdue Amount: ₹ {total_overdue:,.2f}"
        
        tk.Label(self.summary_frame, text=summary_text, font=("Arial", 11),
                justify=tk.LEFT, bg="#f0f0f0").pack(pady=10)
    
    def generate_customer_report(self):
        """Generate customer report"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, c.phone, c.email,
                   COUNT(q.id) as invoice_count,
                   COALESCE(SUM(q.grand_total), 0) as total_spent,
                   MAX(q.date) as last_purchase
            FROM customers c
            LEFT JOIN quotations q ON c.id = q.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        columns = ("Customer Name", "Phone", "Email", "Invoices", "Total Spent (₹)", "Last Purchase")
        self.setup_treeview(columns)
        
        total_customers = len(data)
        total_revenue = 0
        active_customers = 0
        today = datetime.now().date()
        
        for row in data:
            self.tree.insert("", "end", values=row)
            self.current_data.append(row)
            total_revenue += self.parse_currency(row[4])
            
            # Active in last 30 days
            if row[5]:
                last_date = datetime.strptime(row[5], '%Y-%m-%d').date()
                if (today - last_date).days <= 30:
                    active_customers += 1
        
        avg_revenue = total_revenue / total_customers if total_customers > 0 else 0
        
        summary_text = f"👥 CUSTOMER REPORT\n"
        summary_text += f"Total Customers: {total_customers}\n"
        summary_text += f"Active (30 days): {active_customers}\n"
        summary_text += f"Total Revenue: ₹ {total_revenue:,.2f}\n"
        summary_text += f"Average per Customer: ₹ {avg_revenue:,.2f}"
        
        tk.Label(self.summary_frame, text=summary_text, font=("Arial", 11),
                justify=tk.LEFT, bg="#f0f0f0").pack(pady=10)
    
    def generate_material_report(self):
        """Generate material consumption report"""
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT qi.item_name, qi.unit, 
                   SUM(qi.quantity) as total_qty,
                   SUM(qi.amount) as total_amount,
                   COUNT(DISTINCT q.id) as usage_count
            FROM quotation_items qi
            JOIN quotations q ON qi.quotation_id = q.id
            WHERE q.date BETWEEN ? AND ?
            GROUP BY qi.item_name, qi.unit
            ORDER BY total_qty DESC
        ''', (date_from, date_to))
        
        data = cursor.fetchall()
        conn.close()
        
        columns = ("Material Name", "Unit", "Quantity", "Total Value (₹)", "Used In (Quotations)")
        self.setup_treeview(columns)
        
        total_qty = 0
        total_value = 0
        unique_materials = len(data)
        
        for row in data:
            self.tree.insert("", "end", values=row)
            self.current_data.append(row)
            total_qty += self.parse_currency(row[2])
            total_value += self.parse_currency(row[3])
        
        summary_text = f"📦 MATERIAL CONSUMPTION REPORT\n"
        summary_text += f"Period: {date_from} to {date_to}\n"
        summary_text += f"Unique Materials: {unique_materials}\n"
        summary_text += f"Total Quantity: {total_qty:,.2f}\n"
        summary_text += f"Total Value: ₹ {total_value:,.2f}\n"
        summary_text += f"Average Value per Unit: ₹ {total_value/total_qty:,.2f}" if total_qty > 0 else ""
        
        tk.Label(self.summary_frame, text=summary_text, font=("Arial", 11),
                justify=tk.LEFT, bg="#f0f0f0").pack(pady=10)
    
    def generate_monthly_report(self):
        """Generate monthly summary report"""
        year = datetime.now().year
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strftime('%Y-%m', date) as month,
                   COUNT(*) as invoices,
                   COALESCE(SUM(grand_total), 0) as sales,
                   COALESCE(SUM(gst_amount), 0) as gst
            FROM quotations
            WHERE strftime('%Y', date) = ?
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
        ''', (str(year),))
        
        data = cursor.fetchall()
        conn.close()
        
        columns = ("Month", "Invoices", "Sales (₹)", "GST (₹)", "Net (₹)", "Avg per Invoice")
        self.setup_treeview(columns)
        
        total_invoices = 0
        total_sales = 0
        total_gst = 0
        best_month = {"sales": 0, "month": ""}
        
        for row in data:
            month, invoices, sales, gst = row
            sales_float = self.parse_currency(sales)
            gst_float = self.parse_currency(gst)
            net = sales_float - gst_float
            avg = sales_float / invoices if invoices > 0 else 0
            
            values = (month, invoices, f"₹ {sales_float:,.2f}", 
                     f"₹ {gst_float:,.2f}", f"₹ {net:,.2f}", f"₹ {avg:,.2f}")
            self.tree.insert("", "end", values=values)
            self.current_data.append(row)
            
            total_invoices += invoices
            total_sales += sales_float
            total_gst += gst_float
            
            if sales_float > best_month["sales"]:
                best_month = {"month": month, "sales": sales_float}
        
        summary_text = f"📈 MONTHLY SUMMARY REPORT - {year}\n"
        summary_text += f"Total Months: {len(data)}\n"
        summary_text += f"Total Invoices: {total_invoices}\n"
        summary_text += f"Total Sales: ₹ {total_sales:,.2f}\n"
        summary_text += f"Total GST: ₹ {total_gst:,.2f}\n"
        summary_text += f"Best Month: {best_month['month']} (₹ {best_month['sales']:,.2f})\n"
        summary_text += f"Monthly Average: ₹ {total_sales/len(data):,.2f}" if data else ""
        
        tk.Label(self.summary_frame, text=summary_text, font=("Arial", 11),
                justify=tk.LEFT, bg="#f0f0f0").pack(pady=10)
    
    def setup_treeview(self, columns):
        """Setup treeview columns"""
        self.current_columns = columns
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
    
    def export_excel(self):
        """Export report to Excel"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export. Generate a report first.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"report_{self.report_type.get()}_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if filename:
                df = pd.DataFrame(self.current_data, columns=self.current_columns)
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"Report exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def export_pdf(self):
        """Export report to PDF"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export. Generate a report first.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"report_{self.report_type.get()}_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if filename:
                doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
                story = []
                
                # Title
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30
                )
                
                title = Paragraph(f"ContractorMitra - {self.report_type.get().title()} Report", title_style)
                story.append(title)
                
                # Date
                date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10)
                date_text = Paragraph(f"Generated on: {datetime.now().strftime('%d-%b-%Y %H:%M')}", date_style)
                story.append(date_text)
                story.append(Spacer(1, 20))
                
                # Table
                table_data = [self.current_columns]
                for row in self.current_data[:100]:  # Limit to 100 rows
                    table_data.append([str(cell) for cell in row])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                
                story.append(table)
                doc.build(story)
                
                messagebox.showinfo("Success", f"Report exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def print_report(self):
        """Print report"""
        self.export_pdf()  # For now, just export to PDF
        messagebox.showinfo("Info", "Please use PDF export and print from your PDF viewer.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = ReportsWindow(root)
    root.mainloop()