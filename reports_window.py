import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import calendar

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reports - ContractorMitra")
        self.window.geometry("1100x700")
        
        # Variables
        self.report_type = tk.StringVar(value="sales")
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()
        
        # Set default dates (current month)
        today = datetime.now()
        first_day = today.replace(day=1)
        self.date_from.set(first_day.strftime("%Y-%m-%d"))
        self.date_to.set(today.strftime("%Y-%m-%d"))
        
        # Initialize
        self.setup_ui()
    
    def setup_ui(self):
        """Setup reports window UI"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        tk.Label(main_frame, text="REPORTS DASHBOARD", 
                font=("Arial", 18, "bold"), fg="#2c3e50").pack(pady=(0, 20))
        
        # Report type selection frame
        type_frame = tk.LabelFrame(main_frame, text="Select Report Type", font=("Arial", 12, "bold"))
        type_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Report type buttons
        types_frame = tk.Frame(type_frame)
        types_frame.pack(padx=10, pady=10)
        
        reports = [
            ("💰 Sales Report", "sales", "#3498db"),
            ("📊 Pending Payments", "pending", "#e74c3c"),
            ("👥 Customer Report", "customers", "#2ecc71"),
            ("📦 Material Consumption", "materials", "#f39c12"),
            ("📈 Monthly Summary", "monthly", "#9b59b6")
        ]
        
        for text, value, color in reports:
            rb = tk.Radiobutton(types_frame, text=text, variable=self.report_type, 
                              value=value, font=("Arial", 10), bg="#f8f9fa")
            rb.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Date range frame
        date_frame = tk.LabelFrame(main_frame, text="Select Date Range", font=("Arial", 12, "bold"))
        date_frame.pack(fill=tk.X, pady=(0, 20))
        
        date_inner = tk.Frame(date_frame)
        date_inner.pack(padx=10, pady=10)
        
        tk.Label(date_inner, text="From:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(date_inner, textvariable=self.date_from, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(date_inner, text="To:").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(date_inner, textvariable=self.date_to, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        # Quick date buttons
        quick_frame = tk.Frame(date_inner)
        quick_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
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
                     bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=2)
        
        # Generate button
        tk.Button(main_frame, text="🔍 Generate Report", 
                 command=self.generate_report, bg="#27ae60", fg="white",
                 font=("Arial", 11, "bold"), height=2, width=20).pack(pady=10)
        
        # Results frame
        results_frame = tk.LabelFrame(main_frame, text="Report Results", font=("Arial", 12, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview for results
        self.tree = ttk.Treeview(results_frame, height=15)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Summary frame
        self.summary_frame = tk.Frame(main_frame, bg="#f8f9fa", relief=tk.RIDGE, borderwidth=2)
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export buttons
        export_frame = tk.Frame(main_frame)
        export_frame.pack()
        
        tk.Button(export_frame, text="📄 Export to Excel", 
                 command=self.export_excel, bg="#3498db", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="🖨️ Print Report", 
                 command=self.print_report, bg="#f39c12", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="❌ Close", 
                 command=self.window.destroy, bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=5)
    
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
    
    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_type.get()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
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
        
        # Get sales data
        cursor.execute('''
            SELECT q.quote_no, q.date, c.name, q.subtotal, q.gst_amount, q.grand_total, q.status
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.date BETWEEN ? AND ?
            ORDER BY q.date DESC
        ''', (date_from, date_to))
        
        sales = cursor.fetchall()
        
        # Set columns
        columns = ("Quotation No", "Date", "Customer", "Subtotal (₹)", "GST (₹)", "Total (₹)", "Status")
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Customer", width=150)
        self.tree.column("Quotation No", width=120)
        
        # Add data
        total_sales = 0
        total_gst = 0
        for sale in sales:
            self.tree.insert("", "end", values=sale)
            total_sales += sale[6] if sale[6] else 0  # grand_total
            total_gst += sale[5] if sale[5] else 0  # gst_amount
        
        conn.close()
        
        # Show summary
        tk.Label(self.summary_frame, text=f"📊 SALES REPORT SUMMARY", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        tk.Label(self.summary_frame, 
                text=f"Period: {date_from} to {date_to} | Total Invoices: {len(sales)} | " +
                     f"Total Sales: ₹ {total_sales:,.2f} | Total GST: ₹ {total_gst:,.2f}",
                font=("Arial", 10)).pack()
    
    def generate_pending_report(self):
        """Generate pending payments report"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        # Get pending payments (draft/sent quotations)
        cursor.execute('''
            SELECT q.quote_no, q.date, c.name, q.grand_total, q.status
            FROM quotations q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.status IN ('Draft', 'Sent')
            ORDER BY q.grand_total DESC
        ''')
        
        pending = cursor.fetchall()
        
        # Set columns
        columns = ("Quotation No", "Date", "Customer", "Amount (₹)", "Status")
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Customer", width=150)
        
        # Add data
        total_pending = 0
        for item in pending:
            self.tree.insert("", "end", values=item)
            total_pending += item[3] if item[3] else 0
        
        conn.close()
        
        # Show summary
        tk.Label(self.summary_frame, text=f"💰 PENDING PAYMENTS REPORT", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        tk.Label(self.summary_frame, 
                text=f"Total Pending Invoices: {len(pending)} | " +
                     f"Total Pending Amount: ₹ {total_pending:,.2f}",
                font=("Arial", 10)).pack()
    
    def generate_customer_report(self):
        """Generate customer report"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        # Get customer data with sales summary
        cursor.execute('''
            SELECT c.name, c.phone, COUNT(q.id) as invoice_count, 
                   SUM(q.grand_total) as total_spent,
                   MAX(q.date) as last_purchase
            FROM customers c
            LEFT JOIN quotations q ON c.id = q.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
        ''')
        
        customers = cursor.fetchall()
        
        # Set columns
        columns = ("Customer Name", "Phone", "Total Invoices", "Total Spent (₹)", "Last Purchase")
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Customer Name", width=150)
        
        # Add data
        total_customers = len(customers)
        total_revenue = 0
        for cust in customers:
            self.tree.insert("", "end", values=cust)
            total_revenue += cust[3] if cust[3] else 0
        
        conn.close()
        
        # Show summary
        tk.Label(self.summary_frame, text=f"👥 CUSTOMER REPORT", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        tk.Label(self.summary_frame, 
                text=f"Total Customers: {total_customers} | " +
                     f"Total Revenue: ₹ {total_revenue:,.2f} | " +
                     f"Avg per Customer: ₹ {total_revenue/max(total_customers,1):,.2f}",
                font=("Arial", 10)).pack()
    
    def generate_material_report(self):
        """Generate material consumption report"""
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        # Get material consumption
        cursor.execute('''
            SELECT qi.item_name, qi.unit, 
                   SUM(qi.quantity) as total_quantity,
                   SUM(qi.amount) as total_amount
            FROM quotation_items qi
            JOIN quotations q ON qi.quotation_id = q.id
            WHERE q.date BETWEEN ? AND ?
            GROUP BY qi.item_name, qi.unit
            ORDER BY total_quantity DESC
        ''', (date_from, date_to))
        
        materials = cursor.fetchall()
        
        # Set columns
        columns = ("Material Name", "Unit", "Total Quantity", "Total Amount (₹)")
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Material Name", width=200)
        
        # Add data
        total_items = 0
        total_value = 0
        for mat in materials:
            self.tree.insert("", "end", values=mat)
            total_items += mat[2] if mat[2] else 0
            total_value += mat[3] if mat[3] else 0
        
        conn.close()
        
        # Show summary
        tk.Label(self.summary_frame, text=f"📦 MATERIAL CONSUMPTION REPORT", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        tk.Label(self.summary_frame, 
                text=f"Period: {date_from} to {date_to} | " +
                     f"Unique Materials: {len(materials)} | " +
                     f"Total Quantity: {total_items} | " +
                     f"Total Value: ₹ {total_value:,.2f}",
                font=("Arial", 10)).pack()
    
    def generate_monthly_report(self):
        """Generate monthly summary report"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        
        # Get monthly sales data
        cursor.execute('''
            SELECT strftime('%Y-%m', date) as month,
                   COUNT(*) as invoice_count,
                   SUM(grand_total) as total_sales,
                   SUM(gst_amount) as total_gst
            FROM quotations
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
        ''')
        
        monthly = cursor.fetchall()
        
        # Set columns
        columns = ("Month", "Invoices", "Total Sales (₹)", "GST (₹)", "Net (₹)")
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add data
        total_invoices = 0
        total_sales = 0
        total_gst = 0
        
        for month_data in monthly:
            month, invoices, sales, gst = month_data
            net = sales - gst if sales and gst else 0
            self.tree.insert("", "end", values=(month, invoices, sales, gst, net))
            
            total_invoices += invoices if invoices else 0
            total_sales += sales if sales else 0
            total_gst += gst if gst else 0
        
        conn.close()
        
        # Show summary
        tk.Label(self.summary_frame, text=f"📈 MONTHLY SUMMARY REPORT", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        tk.Label(self.summary_frame, 
                text=f"Total Months: {len(monthly)} | " +
                     f"Total Invoices: {total_invoices} | " +
                     f"Total Sales: ₹ {total_sales:,.2f} | " +
                     f"Avg Monthly: ₹ {total_sales/max(len(monthly),1):,.2f}",
                font=("Arial", 10)).pack()
    
    def export_excel(self):
        """Export report to Excel"""
        messagebox.showinfo("Info", "Excel export will be implemented in next version")
    
    def print_report(self):
        """Print report"""
        messagebox.showinfo("Info", "Print functionality will be implemented in next version")