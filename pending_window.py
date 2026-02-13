import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class PendingWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Pending Payments - ContractorMitra")
        self.window.geometry("1000x600")
        
        # Initialize UI
        self.setup_ui()
        self.load_payments()
    
    def setup_ui(self):
        """Setup Pending Payments UI"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="PENDING PAYMENTS", 
                font=("Arial", 16, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        
        # Summary Frame
        summary_frame = tk.Frame(main_frame, bg="#f0f0f0", relief=tk.GROOVE, bd=2)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_pending_var = tk.StringVar(value="₹ 0.00")
        self.total_overdue_var = tk.StringVar(value="₹ 0.00")
        
        tk.Label(summary_frame, text="Total Pending:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(summary_frame, textvariable=self.total_pending_var, font=("Arial", 12, "bold"), fg="#e74c3c", bg="#f0f0f0").pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Label(summary_frame, text="Total Overdue:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(summary_frame, textvariable=self.total_overdue_var, font=("Arial", 12, "bold"), fg="#c0392b", bg="#f0f0f0").pack(side=tk.LEFT, padx=5, pady=10)
        
        # Search and buttons frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var.trace('w', self.on_search)
        
        tk.Button(search_frame, text="+ Add Payment", command=self.add_payment,
                 bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(search_frame, text="Refresh", command=self.load_payments,
                 bg="#3498db", fg="white").pack(side=tk.LEFT)
        
        # Treeview
        columns = ("ID", "Customer", "Quotation #", "Due Date", "Amount", "Paid", "Pending", "Status", "Reference")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        # Define headings and columns
        column_widths = [50, 200, 100, 100, 120, 120, 120, 100, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Mark as Paid", command=self.mark_as_paid,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="View Details", command=self.view_details,
                 bg="#3498db", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Delete", command=self.delete_payment,
                 bg="#e74c3c", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", command=self.window.destroy,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=5)
    
    def load_payments(self):
        """Load pending payments from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            # Get all pending payments
            cursor.execute('''
                SELECT p.id, c.name, p.quotation_id, p.due_date, 
                       p.amount, p.paid_amount, p.pending_amount, p.status, p.reference_no
                FROM payments p
                LEFT JOIN customers c ON p.customer_id = c.id
                WHERE p.status IN ('pending', 'partial')
                ORDER BY p.due_date ASC
            ''')
            
            payments = cursor.fetchall()
            conn.close()
            
            total_pending = 0
            total_overdue = 0
            today = datetime.now().date()
            
            for payment in payments:
                due_date = payment[3]
                pending_amount = payment[6]
                total_pending += pending_amount
                
                # Check if overdue
                if due_date:
                    try:
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                        if due_date_obj < today and payment[7] in ['pending', 'partial']:
                            total_overdue += pending_amount
                    except:
                        pass
                
                # Insert into tree
                self.tree.insert("", "end", values=(
                    payment[0],
                    payment[1] or "N/A",
                    payment[2] or "N/A",
                    due_date,
                    f"₹ {payment[4]:,.2f}",
                    f"₹ {payment[5]:,.2f}",
                    f"₹ {pending_amount:,.2f}",
                    payment[7].title(),
                    payment[8] or "-"
                ))
            
            # Update summary
            self.total_pending_var.set(f"₹ {total_pending:,.2f}")
            self.total_overdue_var.set(f"₹ {total_overdue:,.2f}")
            
        except Exception as e:
            print(f"Error loading payments: {e}")
    
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return 'break'
    
    def show_paste_menu(self, event):
        widget = event.widget
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_text(widget))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return 'break'
    
    def paste_text(self, widget):
        try:
            text = self.window.clipboard_get()
            widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass

    def on_search(self, *args):
        """Search payments"""
        search_term = self.search_var.get().lower()
        self.load_payments()  # Simple reload for now
    
    def add_payment(self):
        """Add new payment"""
        add_window = tk.Toplevel(self.window)
        add_window.title("Add Payment - ContractorMitra")
        add_window.geometry("500x550")
        
        tk.Label(add_window, text="ADD NEW PAYMENT", 
                font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=(10, 20))
        
        form_frame = tk.Frame(add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Customer selection
        tk.Label(form_frame, text="Customer *").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        # Get customers from database
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM customers ORDER BY name")
        customers = cursor.fetchall()
        conn.close()
        
        customer_names = [f"{c[0]} - {c[1]}" for c in customers]
        customer_combo = ttk.Combobox(form_frame, values=customer_names, width=35)
        customer_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Quotation selection (optional)
        tk.Label(form_frame, text="Quotation #").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        quotation_entry = tk.Entry(form_frame, width=35)
        quotation_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Amount
        tk.Label(form_frame, text="Amount (₹) *").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        amount_entry = tk.Entry(form_frame, width=35)
        amount_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        amount_entry.bind('<Tab>', self.focus_next_widget)
        amount_entry.bind('<Button-3>', self.show_paste_menu)
        
        # Paid Amount
        tk.Label(form_frame, text="Paid Amount (₹)").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        paid_entry = tk.Entry(form_frame, width=35)
        paid_entry.insert(0, "0")
        paid_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        paid_entry.bind('<Tab>', self.focus_next_widget)
        paid_entry.bind('<Button-3>', self.show_paste_menu)
        
        # Due Date
        tk.Label(form_frame, text="Due Date *").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        due_date_entry = tk.Entry(form_frame, width=35)
        from datetime import datetime
        due_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        due_date_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)
        due_date_entry.bind('<Tab>', self.focus_next_widget)
        due_date_entry.bind('<Button-3>', self.show_paste_menu)
        
        # Reference No
        tk.Label(form_frame, text="Reference No").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        ref_entry = tk.Entry(form_frame, width=35)
        ref_entry.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)
        ref_entry.bind('<Tab>', self.focus_next_widget)
        ref_entry.bind('<Button-3>', self.show_paste_menu)
        
        # Remarks
        tk.Label(form_frame, text="Remarks").grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
        remarks_entry = tk.Entry(form_frame, width=35)
        remarks_entry.grid(row=6, column=1, padx=10, pady=10, sticky=tk.W)
        remarks_entry.bind('<Tab>', self.focus_next_widget)
        remarks_entry.bind('<Button-3>', self.show_paste_menu)
        
        def save_payment():
            # Validation
            if not customer_combo.get():
                messagebox.showerror("Error", "Please select a customer")
                return
            
            try:
                amount = float(amount_entry.get() or 0)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
                return
            
            try:
                paid_amount = float(paid_entry.get() or 0)
            except ValueError:
                paid_amount = 0
            
            if not due_date_entry.get():
                messagebox.showerror("Error", "Please enter due date")
                return
            
            # Extract customer ID
            customer_id = int(customer_combo.get().split(' - ')[0])
            
            # Calculate pending amount
            pending_amount = amount - paid_amount
            status = 'paid' if pending_amount <= 0 else 'partial' if paid_amount > 0 else 'pending'
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO payments (customer_id, quotation_id, amount, paid_amount, pending_amount, 
                                        due_date, status, reference_no, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    customer_id,
                    quotation_entry.get() or None,
                    amount,
                    paid_amount,
                    pending_amount,
                    due_date_entry.get(),
                    status,
                    ref_entry.get() or None,
                    remarks_entry.get() or None
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Payment added successfully!")
                add_window.destroy()
                self.load_payments()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save payment: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(add_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Payment", command=save_payment,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=add_window.destroy,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    
    def mark_as_paid(self):
        """Mark selected payment as paid"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to mark as paid")
            return
        messagebox.showinfo("Coming Soon", "Mark as Paid feature coming soon!")
    
    def view_details(self):
        """View payment details"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to view")
            return
        messagebox.showinfo("Coming Soon", "View Details feature coming soon!")
    
    def delete_payment(self):
        """Delete selected payment"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a payment to delete")
            return
        messagebox.showinfo("Coming Soon", "Delete feature coming soon!")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = PendingWindow(root)
    root.mainloop()