import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class CustomerWindow:
    def __init__(self, parent, mode='view'):
        self.parent = parent
        self.mode = mode
        self.window = tk.Toplevel(parent)
        self.window.title("Customer Management - ContractorMitra")
        self.window.geometry("900x600")
        # Initialize
         self.setup_ui()
        if mode == 'view':
            self.load_customers()

    def focus_next_widget(self, event):
        """Tab press karne par next widget pe focus karo"""
        event.widget.tk_focusNext().focus()
        return 'break'  # Default Tab behavior rokne ke liye        
        
    def show_paste_menu(self, event):
        """Right-click par Paste menu dikhao"""
        widget = event.widget
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_text(widget))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return 'break'
    
    def paste_text(self, widget):
        """Clipboard se text paste karo"""
        try:
            text = self.window.clipboard_get()
            widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass  # Clipboard empty hai

    def setup_ui(self):
        """Setup customer window UI"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if self.mode == 'add':
            self.setup_add_form(main_frame)
        else:
            self.setup_view_list(main_frame)
    
    def setup_add_form(self, parent):
        """Setup add customer form"""
        tk.Label(parent, text="ADD NEW CUSTOMER", 
                font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(0, 20))
        
        form_frame = tk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        fields = [
            ("Customer Name *", "name", True),
            ("Phone Number *", "phone", True),
            ("Email Address", "email", False),
            ("GSTIN Number", "gstin", False),
            ("Address", "address", False)
        ]
        
        self.entries = {}
        for i, (label, key, required) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            
            if key == 'address':
                entry = tk.Text(form_frame, height=4, width=40)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
                entry.bind('<Tab>', self.focus_next_widget)
                entry.bind('<Button-3>', self.show_paste_menu)
                entry.bind('<Button-2>', self.show_paste_menu)  # Mac support

            else:
                entry = tk.Entry(form_frame, width=40)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
                entry.bind('<Tab>', self.focus_next_widget)
                entry.bind('<Button-3>', self.show_paste_menu)
                entry.bind('<Button-2>', self.show_paste_menu)  # Mac support
            self.entries[key] = entry
        
        # Buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Customer", command=self.save_customer,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Clear", command=self.clear_form,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Close", command=self.window.destroy,
                 bg="#e74c3c", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    
    def setup_view_list(self, parent):
        """Setup customer list view"""
        # Search frame
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var.trace('w', self.on_search)
        
        tk.Button(search_frame, text="+ Add New", command=self.add_new,
                 bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(search_frame, text="Refresh", command=self.load_customers,
                 bg="#3498db", fg="white").pack(side=tk.LEFT)
        
        # Treeview
        columns = ("ID", "Name", "Phone", "Email", "GSTIN", "Added Date")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Name", width=200)
        self.tree.column("Email", width=150)
        self.tree.column("Added Date", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Edit Selected", command=self.edit_customer,
                 bg="#f39c12", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Delete Selected", command=self.delete_customer,
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="View Quotations", command=self.view_quotations,
                 bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", command=self.window.destroy,
                 bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)
    
    def save_customer(self):
        """Save new customer"""
        name = self.entries['name'].get().strip()
        phone = self.entries['phone'].get().strip()
        
        if not name or not phone:
            messagebox.showwarning("Warning", "Name and Phone are required fields")
            return
        
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO customers (name, phone, email, gstin, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                phone,
                self.entries['email'].get().strip(),
                self.entries['gstin'].get().strip(),
                self.entries['address'].get("1.0", tk.END).strip() if 'address' in self.entries else ''
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Customer '{name}' added successfully!")
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for key, entry in self.entries.items():
            if key == 'address':
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
    
    def load_customers(self):
        """Load customers into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email, gstin, created_date FROM customers ORDER BY name")
        customers = cursor.fetchall()
        conn.close()
        
        for customer in customers:
            self.tree.insert("", "end", values=customer)
    
    def on_search(self, *args):
        """Search customers"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.load_customers()
            return
        
        # Filter in memory (for small datasets)
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email, gstin, created_date FROM customers")
        all_customers = cursor.fetchall()
        conn.close()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and insert
        for customer in all_customers:
            if (search_term in customer[1].lower() or  # name
                search_term in customer[2].lower() or  # phone
                search_term in str(customer[3]).lower()):  # email
                self.tree.insert("", "end", values=customer)
    
    def add_new(self):
        """Open add new customer form"""
        self.window.destroy()
        CustomerWindow(self.parent, mode='add')
    
    def edit_customer(self):
        """Edit selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        # Get customer ID
        item = self.tree.item(selected[0])
        customer_id = item['values'][0]
        
        # Open edit window
        self.open_edit_window(customer_id)
    
    def open_edit_window(self, customer_id):
        """Open window to edit customer"""
        # Fetch customer data
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone, email, gstin, address FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        
        if not customer:
            messagebox.showerror("Error", "Customer not found")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Customer")
        edit_window.geometry("500x400")
        
        tk.Label(edit_window, text="EDIT CUSTOMER", 
                font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=(10, 20))
        
        form_frame = tk.Frame(edit_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        fields = [
            ("Customer Name *", "name", customer[0]),
            ("Phone Number *", "phone", customer[1]),
            ("Email Address", "email", customer[2] or ""),
            ("GSTIN Number", "gstin", customer[3] or ""),
            ("Address", "address", customer[4] or "")
        ]
        
        entries = {}
        for i, (label, key, value) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            
            if key == 'address':
                entry = tk.Text(form_frame, height=4, width=30)
                entry.insert("1.0", value)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
                entry.bind('<Tab>', self.focus_next_widget)
                entry.bind('<Button-3>', self.show_paste_menu)
            else:
                entry = tk.Entry(form_frame, width=30)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
                entry.bind('<Tab>', self.focus_next_widget)
                entry.bind('<Button-3>', self.show_paste_menu)
            
            entries[key] = entry
        
        def save_changes():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip()
            
            if not name or not phone:
                messagebox.showwarning("Warning", "Name and Phone are required fields")
                return
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE customers 
                    SET name = ?, phone = ?, email = ?, gstin = ?, address = ?
                    WHERE id = ?
                ''', (
                    name,
                    phone,
                    entries['email'].get().strip(),
                    entries['gstin'].get().strip(),
                    entries['address'].get("1.0", tk.END).strip(),
                    customer_id
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Customer updated successfully!")
                edit_window.destroy()
                self.load_customers()  # Refresh list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Changes", command=save_changes,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=edit_window.destroy,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        item = self.tree.item(selected[0])
        customer_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete customer:\n{customer_name}?\n\nThis action cannot be undone."):
            customer_id = item['values'][0]
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                
                # Check if customer has quotations
                cursor.execute("SELECT COUNT(*) FROM quotations WHERE customer_id = ?", (customer_id,))
                quote_count = cursor.fetchone()[0]
                
                if quote_count > 0:
                    if not messagebox.askyesno("Warning", 
                                              f"This customer has {quote_count} quotation(s).\nDelete anyway?"):
                        conn.close()
                        return
                
                cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Customer deleted successfully!")
                self.load_customers()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def view_quotations(self):
        """View customer's quotations"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        item = self.tree.item(selected[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Open quotations window for this customer
        messagebox.showinfo("Info", 
                           f"Will show quotations for: {customer_name}\n\nThis feature will be implemented in next version")