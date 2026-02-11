import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
# Line 5 ke baad yeh add karo:
from pdf_generator import PDFGenerator
from tkinter import filedialog
import os
class QuotationWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("New Quotation - ContractorMitra")
        self.window.geometry("1300x800")
        
        # Variables
        self.quote_no = self.generate_quote_number()
        self.items = []
        self.item_counter = 0
        
        # Initialize
        self.setup_ui()
        self.load_customers()
        
    def generate_quote_number(self):
        """Generate automatic quotation number"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM quotations")
        count = cursor.fetchone()[0]
        conn.close()
        
        year = datetime.now().year
        month = datetime.now().strftime("%m")
        return f"QT-{year}{month}-{str(count+1).zfill(3)}"
    
    def setup_ui(self):
        """Setup quotation window UI"""
        # Main container with scrollbar
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="CREATE NEW QUOTATION", 
                font=("Arial", 18, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        
        tk.Label(header_frame, text=f"Quotation No: {self.quote_no}", 
                font=("Arial", 12, "bold"), fg="#e74c3c").pack(side=tk.RIGHT)
        
        # Customer selection frame
        customer_frame = tk.LabelFrame(main_frame, text="Customer Details", font=("Arial", 12, "bold"))
        customer_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Customer selection
        tk.Label(customer_frame, text="Select Customer:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=40)
        self.customer_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Button(customer_frame, text="+ New Customer", command=self.add_new_customer,
                 bg="#27ae60", fg="white").grid(row=0, column=2, padx=10, pady=10)
        
        # Items frame
        items_frame = tk.LabelFrame(main_frame, text="Items & Materials", font=("Arial", 12, "bold"))
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create Treeview for items
        columns = ("#", "Item Description", "Unit", "Quantity", "Rate (₹)", "GST %", "Amount (₹)")
        self.tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("#", width=50)
        self.tree.column("Item Description", width=300)
        self.tree.column("Amount (₹)", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Add item frame
        add_frame = tk.Frame(items_frame)
        add_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(add_frame, text="Quick Add:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(add_frame, textvariable=self.item_var, width=40)
        self.item_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.item_combo.bind('<<ComboboxSelected>>', self.on_item_selected)
        
        tk.Button(add_frame, text="+ Add Item", command=self.add_item_manual,
                 bg="#3498db", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(add_frame, text="Remove Selected", command=self.remove_item,
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT)
        
        # Load materials for combo
        self.load_materials()
        
        # Charges frame
        charges_frame = tk.LabelFrame(main_frame, text="Additional Charges", font=("Arial", 12, "bold"))
        charges_frame.pack(fill=tk.X, pady=(0, 20))
        
        charges = [
            ("Transport Charges (₹):", "transport"),
            ("Loading/Unloading (₹):", "loading"),
            ("Other Charges (₹):", "other")
        ]
        
        self.charge_vars = {}
        for i, (label, key) in enumerate(charges):
            tk.Label(charges_frame, text=label).grid(row=0, column=i*2, padx=10, pady=10, sticky=tk.W)
            var = tk.DoubleVar(value=0.0)
            self.charge_vars[key] = var
            tk.Entry(charges_frame, textvariable=var, width=15).grid(row=0, column=i*2+1, padx=(0, 20), pady=10)
        
        # Totals frame
        totals_frame = tk.Frame(main_frame, bg="#f8f9fa", relief=tk.RIDGE, borderwidth=2)
        totals_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.subtotal_var = tk.StringVar(value="₹ 0.00")
        self.gst_var = tk.StringVar(value="₹ 0.00")
        self.total_var = tk.StringVar(value="₹ 0.00")
        
        tk.Label(totals_frame, text="Subtotal:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        tk.Label(totals_frame, textvariable=self.subtotal_var, font=("Arial", 11, "bold")).grid(row=0, column=1, padx=20, pady=10, sticky=tk.W)
        
        tk.Label(totals_frame, text="GST Amount:", font=("Arial", 11)).grid(row=0, column=2, padx=20, pady=10, sticky=tk.W)
        tk.Label(totals_frame, textvariable=self.gst_var, font=("Arial", 11, "bold")).grid(row=0, column=3, padx=20, pady=10, sticky=tk.W)
        
        tk.Label(totals_frame, text="Grand Total:", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=20, pady=10, sticky=tk.W)
        tk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 14, "bold"), fg="#e74c3c").grid(row=0, column=5, padx=20, pady=10, sticky=tk.W)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        buttons = [
            ("Calculate Total", self.calculate_total, "#3498db"),
            ("Save as Draft", self.save_draft, "#f39c12"),
            ("Generate PDF", self.generate_pdf, "#27ae60"),
            ("Print", self.print_quotation, "#9b59b6"),
            ("Close", self.window.destroy, "#95a5a6")
        ]
        
        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command,
                     bg=color, fg="white", height=2, width=15).pack(side=tk.LEFT, padx=5, pady=5)
    
    def load_customers(self):
        """Load customers into combobox"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone FROM customers ORDER BY name")
        customers = cursor.fetchall()
        conn.close()
        
        customer_list = [f"{name} ({phone})" for _, name, phone in customers]
        self.customer_combo['values'] = customer_list
    
    def load_materials(self):
        """Load materials into combobox"""
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, default_unit, default_rate, default_gst FROM materials ORDER BY name")
        materials = cursor.fetchall()
        conn.close()
        
        material_list = [name for name, _, _, _ in materials]
        self.item_combo['values'] = material_list
    
    def on_item_selected(self, event):
        """When material is selected from dropdown"""
        material_name = self.item_var.get()
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT default_unit, default_rate, default_gst FROM materials WHERE name = ?", (material_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            unit, rate, gst = result
            # Open dialog to enter quantity
            self.add_item_with_details(material_name, unit, rate, gst)
    
    def add_item_with_details(self, name, unit, rate, gst):
        """Add item with details"""
        # Create dialog for quantity
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Item")
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Item: {name}", font=("Arial", 10, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="Quantity:").pack()
        qty_var = tk.DoubleVar(value=1.0)
        tk.Entry(dialog, textvariable=qty_var).pack(pady=5)
        
        tk.Label(dialog, text="Rate (₹):").pack()
        rate_var = tk.DoubleVar(value=rate)
        tk.Entry(dialog, textvariable=rate_var).pack(pady=5)
        
        tk.Label(dialog, text="GST %:").pack()
        gst_var = tk.DoubleVar(value=gst)
        tk.Entry(dialog, textvariable=gst_var).pack(pady=5)
        
        def add_and_close():
            quantity = qty_var.get()
            item_rate = rate_var.get()
            item_gst = gst_var.get()
            amount = quantity * item_rate
            
            self.item_counter += 1
            self.tree.insert("", "end", values=(
                self.item_counter,
                name,
                unit,
                f"{quantity:.2f}",
                f"{item_rate:.2f}",
                f"{item_gst:.0f}%",
                f"{amount:.2f}"
            ))
            
            self.items.append({
                'name': name,
                'unit': unit,
                'quantity': quantity,
                'rate': item_rate,
                'gst': item_gst,
                'amount': amount
            })
            
            dialog.destroy()
            self.calculate_total()
        
        tk.Button(dialog, text="Add to Quotation", command=add_and_close,
                 bg="#27ae60", fg="white").pack(pady=20)
    
    def add_item_manual(self):
        """Add item manually"""
        self.add_item_with_details("Custom Item", "piece", 0.0, 18.0)
    
    def remove_item(self):
        """Remove selected item"""
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.calculate_total()
    
    def calculate_total(self):
        """Calculate totals"""
        subtotal = 0.0
        gst_total = 0.0
        
        # Calculate from tree items
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            amount = float(values[6])  # Amount column
            gst_percent = float(values[5].replace('%', ''))  # GST column
            
            subtotal += amount
            gst_total += (amount * gst_percent / 100)
        
        # Add additional charges
        transport = self.charge_vars['transport'].get()
        loading = self.charge_vars['loading'].get()
        other = self.charge_vars['other'].get()
        
        subtotal += transport + loading + other
        grand_total = subtotal + gst_total
        
        # Update display
        self.subtotal_var.set(f"₹ {subtotal:,.2f}")
        self.gst_var.set(f"₹ {gst_total:,.2f}")
        self.total_var.set(f"₹ {grand_total:,.2f}")
    
    def save_draft(self):
        """Save quotation as draft"""
        customer = self.customer_var.get()
        if not customer:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        # Get customer ID from selection
        customer_id = None
        if '(' in customer:
            phone = customer.split('(')[1].replace(')', '')
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
            result = cursor.fetchone()
            if result:
                customer_id = result[0]
            conn.close()
        
        # Calculate totals
        self.calculate_total()
        subtotal = float(self.subtotal_var.get().replace('₹', '').replace(',', '').strip())
        gst_amount = float(self.gst_var.get().replace('₹', '').replace(',', '').strip())
        grand_total = float(self.total_var.get().replace('₹', '').replace(',', '').strip())
        
        # Save to database
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            # Insert quotation
            cursor.execute('''
                INSERT INTO quotations (quote_no, customer_id, date, subtotal, transport, 
                                      loading, other_charges, gst_amount, grand_total, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.quote_no, customer_id, datetime.now().date(), subtotal,
                  self.charge_vars['transport'].get(), self.charge_vars['loading'].get(),
                  self.charge_vars['other'].get(), gst_amount, grand_total, 'Draft'))
            
            quotation_id = cursor.lastrowid
            self.current_quotation_id = quotation_id  # ← YEH LINE ADD KARO
            # Insert items
            for child in self.tree.get_children():
                values = self.tree.item(child)['values']
                cursor.execute('''
                    INSERT INTO quotation_items (quotation_id, item_name, unit, quantity, 
                                               rate, gst_percent, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (quotation_id, values[1], values[2], 
                      float(values[3]), float(values[4]), 
                      float(values[5].replace('%', '')), 
                      float(values[6])))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Quotation {self.quote_no} saved as draft!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
        def generate_pdf(self):
        """Generate PDF of quotation"""
        # Check if PDF generator is available
        try:
            from pdf_generator import PDFGenerator
        except ImportError:
            messagebox.showwarning("PDF Feature Not Available", 
                                  "PDF generator is not installed.\n"
                                  "Please install: pip install reportlab")
            return
        
        # Pehle check karo quotation saved hai ya nahi
        if not hasattr(self, 'current_quotation_id') or not self.current_quotation_id:
            # Agar save nahi hai toh save karne ko bolo
            save_first = messagebox.askyesno("Save Required", 
                                             "Quotation must be saved before generating PDF.\n"
                                             "Do you want to save it now?")
            if save_first:
                self.save_draft()
                # Save ke baad check karo
                if not hasattr(self, 'current_quotation_id') or not self.current_quotation_id:
                    messagebox.showwarning("Warning", "Please save the quotation first")
                    return
            else:
                return
        
        try:
            # File save dialog
            default_filename = f"Quotation_{self.quote_no}.pdf"
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if not filename:  # User cancelled
                return
            
            # Generate PDF
            generator = PDFGenerator()
            success = generator.generate_quotation_pdf(self.current_quotation_id, filename)
            
            if success:
                messagebox.showinfo("Success", f"✅ PDF generated successfully!\n\nSaved to:\n{filename}")
                
                # Open PDF option
                open_pdf = messagebox.askyesno("Open PDF", "Do you want to open the PDF?")
                if open_pdf:
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(filename)
                        elif os.name == 'posix':  # Linux/Mac
                            os.system(f'xdg-open "{filename}"')
                    except Exception as e:
                        print(f"Could not open PDF: {e}")
            else:
                messagebox.showerror("Error", "Failed to generate PDF. Check quotation data.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    
    def print_quotation(self):
        """Print quotation"""
        messagebox.showinfo("Info", "Print functionality will be implemented in next version")
    
    def add_new_customer(self):
        """Open new customer dialog"""
        from customer_window import CustomerWindow
        CustomerWindow(self.window, mode='add')