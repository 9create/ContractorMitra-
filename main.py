import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from tkinter import scrolledtext
import os

# Create images directory if not exists
if not os.path.exists('images'):
    os.makedirs('images')

class ContractorMitra:
    def __init__(self, root):
        self.root = root
        self.root.title("ContractorMitra v1.0 - Desktop Application")
        self.root.geometry("1200x700")
        self.root.state('zoomed')  # Start maximized
        
        # Set icon (optional)
        # self.root.iconbitmap('icon.ico')
        
        # Variables
        self.current_customer_id = None
        self.quotation_items = []
        
        # Colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        # Initialize
        self.create_database()
        self.setup_ui()
        
        # Show welcome
        self.show_welcome()
        
    def create_database(self):
        """Create SQLite database with all tables"""
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    gstin TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Quotations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_no TEXT UNIQUE NOT NULL,
                    customer_id INTEGER,
                    date DATE,
                    subtotal REAL DEFAULT 0,
                    transport REAL DEFAULT 0,
                    loading REAL DEFAULT 0,
                    other_charges REAL DEFAULT 0,
                    gst_amount REAL DEFAULT 0,
                    grand_total REAL DEFAULT 0,
                    status TEXT DEFAULT 'Draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Quotation items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotation_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quotation_id INTEGER,
                    item_name TEXT NOT NULL,
                    unit TEXT,
                    quantity REAL DEFAULT 1,
                    rate REAL DEFAULT 0,
                    gst_percent REAL DEFAULT 18,
                    amount REAL DEFAULT 0,
                    FOREIGN KEY (quotation_id) REFERENCES quotations (id)
                )
            ''')
            
            # Materials table (for quick selection)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    default_unit TEXT,
                    default_rate REAL,
                    default_gst REAL
                )
            ''')
            
            # Insert sample materials if empty
            cursor.execute("SELECT COUNT(*) FROM materials")
            if cursor.fetchone()[0] == 0:
                sample_materials = [
                    ('1.5 sq.mm Copper Wire', 'Wires', 'meter', 45.0, 18.0),
                    ('2.5 sq.mm Copper Wire', 'Wires', 'meter', 65.0, 18.0),
                    ('Modular Switch 1-Gang', 'Switches', 'piece', 180.0, 18.0),
                    ('Modular Switch 2-Gang', 'Switches', 'piece', 250.0, 18.0),
                    ('5A Socket', 'Sockets', 'piece', 120.0, 18.0),
                    ('15A Socket', 'Sockets', 'piece', 150.0, 18.0),
                    ('20mm PVC Conduit', 'Conduits', 'meter', 30.0, 18.0),
                    ('Electrical Labour', 'Labour', 'point', 300.0, 0.0),
                    ('Installation Labour', 'Labour', 'hour', 200.0, 0.0),
                    ('LED Panel Light 18W', 'Lighting', 'piece', 450.0, 18.0),
                    ('Ceiling Fan', 'Fans', 'piece', 1500.0, 18.0),
                    ('6A MCB', 'Protection', 'piece', 200.0, 18.0),
                    ('Distribution Box 8-way', 'Protection', 'piece', 800.0, 18.0)
                ]
                cursor.executemany('''
                    INSERT INTO materials (name, category, default_unit, default_rate, default_gst)
                    VALUES (?, ?, ?, ?, ?)
                ''', sample_materials)
            
            conn.commit()
            conn.close()
            print("Database created successfully!")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create database: {str(e)}")
    
    def setup_ui(self):
        """Setup main UI components"""
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg=self.colors['light'])
        
        # Create menu
        self.create_menu()
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Quotation", command=self.new_quotation, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Quotation", command=self.open_quotation, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_document, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Customers Menu
        customer_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Customers", menu=customer_menu)
        customer_menu.add_command(label="Add New Customer", command=self.add_customer)
        customer_menu.add_command(label="View All Customers", command=self.view_customers)
        customer_menu.add_command(label="Search Customer", command=self.search_customer)
        
        # Materials Menu
        material_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Materials", menu=material_menu)
        material_menu.add_command(label="Manage Materials", command=self.manage_materials)
        material_menu.add_command(label="Add New Material", command=self.add_material)
        
        # Reports Menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Sales Report", command=self.sales_report)
        reports_menu.add_command(label="Pending Payments", command=self.pending_payments)
        reports_menu.add_command(label="Material Stock", command=self.material_stock)
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calculator", command=self.open_calculator)
        tools_menu.add_command(label="Backup Database", command=self.backup_database)
        tools_menu.add_command(label="Restore Database", command=self.restore_database)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.user_manual)
        help_menu.add_command(label="About", command=self.about_dialog)
        
        # Bind shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_quotation())
        self.root.bind('<Control-o>', lambda e: self.open_quotation())
        self.root.bind('<Control-p>', lambda e: self.print_document())
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add clock
        self.clock_label = tk.Label(self.status_bar, text="", anchor=tk.E)
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        self.update_clock()
    
    def update_clock(self):
        """Update clock in status bar"""
        current_time = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)
    
    def show_welcome(self):
        """Show welcome screen"""
        # Clear any existing frames
        for widget in self.root.winfo_children():
            if widget not in [self.status_bar]:
                widget.destroy()
        
        # Welcome frame
        welcome_frame = tk.Frame(self.root, bg=self.colors['light'])
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title area
        title_frame = tk.Frame(welcome_frame, bg=self.colors['primary'], height=150)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="ContractorMitra", 
                font=("Arial", 36, "bold"), bg=self.colors['primary'], fg="white").pack(pady=30)
        
        tk.Label(title_frame, text="Professional Quotation & Billing Software for Electrical & Civil Contractors",
                font=("Arial", 14), bg=self.colors['primary'], fg="#bdc3c7").pack()
        
        # Quick actions frame
        actions_frame = tk.Frame(welcome_frame, bg=self.colors['light'])
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Action buttons grid
        buttons_data = [
            ("📝 New Quotation", self.new_quotation, self.colors['secondary']),
            ("👥 Add Customer", self.add_customer, self.colors['success']),
            ("📊 View Reports", self.sales_report, self.colors['warning']),
            ("📦 Manage Materials", self.manage_materials, "#9b59b6"),
            ("💰 Pending Payments", self.pending_payments, self.colors['danger']),
            ("🛠️ Calculator", self.open_calculator, "#16a085")
        ]
        
        row, col = 0, 0
        for text, command, color in buttons_data:
            btn = tk.Button(actions_frame, text=text, command=command,
                          font=("Arial", 12, "bold"), bg=color, fg="white",
                          height=3, width=20, cursor="hand2")
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.darken_color(b.cget('bg'))))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Configure grid
        for i in range(3):
            actions_frame.columnconfigure(i, weight=1)
        for i in range(2):
            actions_frame.rowconfigure(i, weight=1)
        
        # Recent activities
        recent_frame = tk.LabelFrame(welcome_frame, text="Recent Activities", 
                                    font=("Arial", 12, "bold"), bg=self.colors['light'])
        recent_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # Sample recent activities
        activities = [
            "Today: Created quotation QT-2024-001 for ₹25,000",
            "Yesterday: Customer Rajesh paid ₹15,000",
            "Dec 10: Added 5 new materials to database"
        ]
        
        for activity in activities:
            tk.Label(recent_frame, text=f"• {activity}", 
                    bg=self.colors['light'], font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=2)
    
    def darken_color(self, color):
        """Darken a color for hover effect"""
        # Simple darkening for demo
        return color
    
    # ========== MAIN FUNCTIONALITY METHODS ==========
    
    def new_quotation(self):
        """Open new quotation window"""
        from quotation_window import QuotationWindow
        QuotationWindow(self.root)
    
    def add_customer(self):
        """Open add customer window"""
        from customer_window import CustomerWindow
        CustomerWindow(self.root, mode='add')
    
    def view_customers(self):
        """Open view customers window"""
        from customer_window import CustomerWindow
        CustomerWindow(self.root, mode='view')
    
    def search_customer(self):
        """Search customer dialog"""
        messagebox.showinfo("Info", "Customer search functionality will be implemented here")
    
    def manage_materials(self):
        """Manage materials window"""
        from material_window import MaterialWindow
        MaterialWindow(self.root)
    
    def add_material(self):
        """Add new material"""
        messagebox.showinfo("Info", "Add material functionality will be implemented here")
    
    def sales_report(self):
        """Sales report window"""
        from reports_window import ReportsWindow
        ReportsWindow(self.root)
    
    def pending_payments(self):
        """Pending payments window"""
        messagebox.showinfo("Info", "Pending payments functionality will be implemented here")
    
    def material_stock(self):
        """Material stock window"""
        messagebox.showinfo("Info", "Material stock functionality will be implemented here")
    
    def open_calculator(self):
        """Open calculator"""
        import subprocess
        try:
            subprocess.Popen('calc.exe')  # Windows
        except:
            messagebox.showinfo("Calculator", "Use your system calculator")
    
    def backup_database(self):
        """Backup database"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            import shutil
            try:
                shutil.copy2('contractormitra.db', filename)
                messagebox.showinfo("Success", f"Database backed up to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_database(self):
        """Restore database"""
        if messagebox.askyesno("Confirm", "This will overwrite current database. Continue?"):
            filename = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            if filename:
                import shutil
                try:
                    shutil.copy2(filename, 'contractormitra.db')
                    messagebox.showinfo("Success", "Database restored successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def open_quotation(self):
        """Open existing quotation"""
        messagebox.showinfo("Info", "Open quotation functionality will be implemented here")
    
    def print_document(self):
        """Print current document"""
        messagebox.showinfo("Info", "Print functionality will be implemented here")
    
    def user_manual(self):
        """Show user manual"""
        manual_text = """ContractorMitra User Manual

1. New Quotation:
   - Press Ctrl+N or click New Quotation
   - Select customer or add new
   - Add items from material database
   - Save as draft or generate PDF

2. Customer Management:
   - Add new customers with GST details
   - View all customers
   - Search customers by name/phone

3. Materials Database:
   - Pre-loaded electrical items
   - Add your own materials
   - Quick selection in quotations

4. Reports:
   - Sales reports
   - Pending payments
   - Material consumption

For support: contact@contractormitra.com"""
        
        manual_window = tk.Toplevel(self.root)
        manual_window.title("User Manual")
        manual_window.geometry("600x400")
        
        text_area = scrolledtext.ScrolledText(manual_window, wrap=tk.WORD, width=70, height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, manual_text)
        text_area.config(state=tk.DISABLED)
    
    def about_dialog(self):
        """Show about dialog"""
        about_text = f"""ContractorMitra v1.0

Professional Quotation & Billing Software
for Electrical & Civil Contractors

Developed with Python & Tkinter
Database: SQLite

Features:
✓ Smart Quotation Generation
✓ Customer Management
✓ Material Database
✓ GST Compliant Invoices
✓ Desktop Application (Works Offline)

© 2024 ContractorMitra. All rights reserved."""
        
        messagebox.showinfo("About ContractorMitra", about_text)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = ContractorMitra(root)
    app.run()