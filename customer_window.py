"""
CUSTOMER WINDOW - ContractorMitra
Modern Apple-style customer management
Version: 3.0.0 (Clean UI Edition)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ModernStyle:
    """Modern Apple-like style constants"""
    BG_COLOR = "#f5f5f7"
    CARD_BG = "white"
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    ACCENT_BLUE = "#3498db"
    ACCENT_GREEN = "#2ecc71"
    ACCENT_ORANGE = "#f39c12"
    ACCENT_PURPLE = "#9b59b6"
    ACCENT_RED = "#e74c3c"
    ACCENT_TEAL = "#1abc9c"
    
    FONT_HEADER = ("SF Pro Display", 18, "bold")
    FONT_TITLE = ("SF Pro Display", 16, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)
    
    PADDING = 15
    BUTTON_WIDTH = 120
    BUTTON_HEIGHT = 35


class CustomerWindow:
    def __init__(self, parent, mode='view'):
        self.parent = parent
        self.mode = mode
        self.window = tk.Toplevel(parent)
        self.window.title("Customer Management - ContractorMitra")
        self.window.geometry("1000x650")
        self.window.configure(bg=ModernStyle.BG_COLOR)
        
        # Center window
        self.center_window()
        
        # Initialize
        self.setup_ui()
        if mode == 'view':
            self.load_customers()
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_modern_button(self, parent, text, command, color=ModernStyle.ACCENT_BLUE):
        """Create a modern rounded button"""
        btn_frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        
        canvas = tk.Canvas(btn_frame, width=120, height=35, 
                          highlightthickness=0, bg=ModernStyle.BG_COLOR)
        canvas.pack()
        
        def draw_rect(fill_color):
            canvas.delete("all")
            # Draw rounded rectangle
            canvas.create_rounded_rect(2, 2, 118, 33, 8, 
                                      fill=fill_color, outline="")
            canvas.create_text(60, 18, text=text, fill="white", 
                             font=ModernStyle.FONT_SMALL)
        
        # Define rounded rect method
        def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
            points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, 
                     x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, 
                     x1, y1+r, x1, y1]
            canvas.create_polygon(points, smooth=True, **kwargs)
        
        # Monkey patch canvas
        canvas.create_rounded_rect = create_rounded_rect.__get__(canvas)
        
        # Initial draw
        draw_rect(color)
        
        # Hover effects
        def on_enter(e):
            draw_rect(self.darken_color(color))
        
        def on_leave(e):
            draw_rect(color)
        
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", lambda e: command())
        
        return btn_frame
    
    def darken_color(self, color):
        """Darken hex color for hover effect"""
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def focus_next_widget(self, event):
        """Tab navigation"""
        event.widget.tk_focusNext().focus()
        return 'break'
    
    def show_paste_menu(self, event):
        """Right-click paste menu"""
        widget = event.widget
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_text(widget))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return 'break'
    
    def paste_text(self, widget):
        """Paste from clipboard"""
        try:
            text = self.window.clipboard_get()
            widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass
    
    def setup_ui(self):
        """Setup main UI"""
        # Main container with padding
        main_frame = tk.Frame(self.window, bg=ModernStyle.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=ModernStyle.BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame, text="👤 Customers", 
                        font=ModernStyle.FONT_HEADER,
                        fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR)
        title.pack(side=tk.LEFT)
        
        if self.mode == 'view':
            add_btn = self.create_modern_button(header_frame, "+ Add New", 
                                               self.add_new, ModernStyle.ACCENT_GREEN)
            add_btn.pack(side=tk.RIGHT, padx=5)
        
        if self.mode == 'add':
            self.setup_add_form(main_frame)
        else:
            self.setup_view_list(main_frame)
    
    def setup_view_list(self, parent):
        """Setup customer list view"""
        # Search frame
        search_frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search box
        search_label = tk.Label(search_frame, text="🔍 Search:", 
                               font=ModernStyle.FONT_NORMAL,
                               fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR)
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=ModernStyle.FONT_NORMAL,
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightcolor=ModernStyle.ACCENT_BLUE,
                               highlightbackground="#ddd", width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.on_search)
        
        # Refresh button
        refresh_btn = self.create_modern_button(search_frame, "🔄 Refresh", 
                                               self.load_customers, ModernStyle.ACCENT_BLUE)
        refresh_btn.pack(side=tk.LEFT)
        
        # Treeview styling
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
        
        # Treeview
        columns = ("ID", "Name", "Phone", "Email", "GSTIN", "Added Date")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", 
                                 height=15, style="Treeview")
        
        # Column widths
        column_widths = [50, 200, 120, 180, 120, 100]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons frame
        button_frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        button_frame.pack(fill=tk.X, pady=15)
        
        # Modern action buttons
        buttons = [
            ("✏️ Edit", self.edit_customer, ModernStyle.ACCENT_BLUE),
            ("🗑️ Delete", self.delete_customer, ModernStyle.ACCENT_RED),
            ("📋 View Quotations", self.view_quotations, ModernStyle.ACCENT_PURPLE),
            ("❌ Close", self.window.destroy, ModernStyle.TEXT_SECONDARY)
        ]
        
        for text, cmd, color in buttons:
            btn = self.create_modern_button(button_frame, text, cmd, color)
            btn.pack(side=tk.LEFT, padx=5)
    
    def setup_add_form(self, parent):
        """Setup add customer form"""
        # Form card
        card = tk.Frame(parent, bg="white", relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Inner padding
        inner = tk.Frame(card, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title = tk.Label(inner, text="➕ Add New Customer", 
                        font=ModernStyle.FONT_TITLE,
                        fg=ModernStyle.TEXT_PRIMARY, bg="white")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Form fields
        fields = [
            ("Customer Name *", "name"),
            ("Phone Number *", "phone"),
            ("Email Address", "email"),
            ("GSTIN Number", "gstin"),
            ("Address", "address")
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields, start=1):
            # Label
            lbl = tk.Label(inner, text=label, 
                          font=ModernStyle.FONT_NORMAL,
                          fg=ModernStyle.TEXT_PRIMARY, bg="white")
            lbl.grid(row=i, column=0, padx=10, pady=8, sticky=tk.W)
            
            # Entry
            if key == 'address':
                entry = tk.Text(inner, height=4, width=40,
                               font=ModernStyle.FONT_NORMAL,
                               relief=tk.FLAT, highlightthickness=1,
                               highlightcolor=ModernStyle.ACCENT_BLUE,
                               highlightbackground="#ddd")
                entry.grid(row=i, column=1, padx=10, pady=8, sticky=tk.W)
            else:
                entry = tk.Entry(inner, width=40,
                                font=ModernStyle.FONT_NORMAL,
                                relief=tk.FLAT, highlightthickness=1,
                                highlightcolor=ModernStyle.ACCENT_BLUE,
                                highlightbackground="#ddd")
                entry.grid(row=i, column=1, padx=10, pady=8, sticky=tk.W)
            
            entry.bind('<Tab>', self.focus_next_widget)
            entry.bind('<Button-3>', self.show_paste_menu)
            self.entries[key] = entry
        
        # Button frame
        btn_frame = tk.Frame(inner, bg="white")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # Modern buttons
        save_btn = self.create_modern_button(btn_frame, "💾 Save Customer", 
                                            self.save_customer, ModernStyle.ACCENT_GREEN)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = self.create_modern_button(btn_frame, "🔄 Clear", 
                                             self.clear_form, ModernStyle.ACCENT_ORANGE)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = self.create_modern_button(btn_frame, "❌ Close", 
                                             self.window.destroy, ModernStyle.TEXT_SECONDARY)
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def load_customers(self):
        """Load customers into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone, email, gstin, created_date FROM customers ORDER BY name")
            customers = cursor.fetchall()
            conn.close()
            
            for customer in customers:
                # Format date if exists
                date = customer[5] if customer[5] else "-"
                if date != "-":
                    try:
                        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                        date = date_obj.strftime('%d-%b-%Y')
                    except:
                        pass
                
                self.tree.insert("", "end", values=(
                    customer[0],
                    customer[1],
                    customer[2] or "-",
                    customer[3] or "-",
                    customer[4] or "-",
                    date
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def on_search(self, event=None):
        """Search customers"""
        search_term = self.search_var.get().lower()
        
        # Reload all
        self.load_customers()
        
        if not search_term:
            return
        
        # Filter in treeview
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if not any(search_term in str(v).lower() for v in values[1:4]):  # Search in name, phone, email
                self.tree.delete(item)
    
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
            
            # Go back to view mode
            self.window.destroy()
            CustomerWindow(self.parent, mode='view')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for key, entry in self.entries.items():
            if key == 'address':
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
    
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
        
        item = self.tree.item(selected[0])
        customer_id = item['values'][0]
        self.open_edit_window(customer_id)
    
    def open_edit_window(self, customer_id):
        """Open window to edit customer"""
        # Fetch customer data
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, phone, email, gstin, address FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            conn.close()
            
            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Customer")
        edit_window.geometry("500x450")
        edit_window.configure(bg=ModernStyle.BG_COLOR)
        
        # Center window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main frame
        main_frame = tk.Frame(edit_window, bg=ModernStyle.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card
        card = tk.Frame(main_frame, bg="white", relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Inner
        inner = tk.Frame(card, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(inner, text="✏️ Edit Customer", 
                        font=ModernStyle.FONT_TITLE,
                        fg=ModernStyle.TEXT_PRIMARY, bg="white")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Form fields
        fields = [
            ("Customer Name *", "name", customer[0]),
            ("Phone Number *", "phone", customer[1]),
            ("Email Address", "email", customer[2] or ""),
            ("GSTIN Number", "gstin", customer[3] or ""),
            ("Address", "address", customer[4] or "")
        ]
        
        entries = {}
        for i, (label, key, value) in enumerate(fields, start=1):
            # Label
            lbl = tk.Label(inner, text=label, 
                          font=ModernStyle.FONT_NORMAL,
                          fg=ModernStyle.TEXT_PRIMARY, bg="white")
            lbl.grid(row=i, column=0, padx=10, pady=8, sticky=tk.W)
            
            # Entry
            if key == 'address':
                entry = tk.Text(inner, height=3, width=30,
                               font=ModernStyle.FONT_NORMAL,
                               relief=tk.FLAT, highlightthickness=1,
                               highlightcolor=ModernStyle.ACCENT_BLUE,
                               highlightbackground="#ddd")
                entry.insert("1.0", value)
                entry.grid(row=i, column=1, padx=10, pady=8, sticky=tk.W)
            else:
                entry = tk.Entry(inner, width=30,
                                font=ModernStyle.FONT_NORMAL,
                                relief=tk.FLAT, highlightthickness=1,
                                highlightcolor=ModernStyle.ACCENT_BLUE,
                                highlightbackground="#ddd")
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=10, pady=8, sticky=tk.W)
            
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
                self.load_customers()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        # Button frame
        btn_frame = tk.Frame(inner, bg="white")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # Modern buttons
        save_btn = self.create_modern_button(btn_frame, "💾 Save Changes", 
                                            save_changes, ModernStyle.ACCENT_GREEN)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = self.create_modern_button(btn_frame, "❌ Cancel", 
                                              edit_window.destroy, ModernStyle.TEXT_SECONDARY)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        item = self.tree.item(selected[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete customer:\n{customer_name}?\n\nThis action cannot be undone."):
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
        
        messagebox.showinfo("Info", 
                           f"Will show quotations for: {customer_name}\n\nThis feature will be implemented in next version")


# ============ MAIN ============
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = CustomerWindow(root)
    root.mainloop()