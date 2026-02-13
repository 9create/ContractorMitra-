"""
AI QUOTE GENERATOR - ContractorMitra
Pure AI based quotation generation system
Version: 2.0.0 (FINAL FIXED VERSION)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from datetime import datetime
import os
import time

class AIQuoteGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("AI Quote Generator - ContractorMitra")
        self.window.geometry("1000x750")
        
        # Variables
        self.items = []
        self.selected_customer_id = None
        self.customer_name = None
        self.customer_phone = None
        self.customer_address = None
        self.customer_gstin = None
        
        # Initialize UI
        self.setup_ui()
        self.load_materials()
        self.load_customers()
        
        # Center window
        self.center_window()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_closing(self):
        """Handle window close event"""
        try:
            self.window.destroy()
        except:
            pass
    
    def setup_ui(self):
        """Setup AI Quote Generator UI"""
        # Main container with scrollbar
        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main frame inside scrollable frame
        main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="🤖 AI QUOTE GENERATOR", 
                font=("Arial", 22, "bold"), fg="#2c3e50").pack()
        
        tk.Label(header_frame, text="Pure AI - Rule Based Intelligent Quotation System", 
                font=("Arial", 11), fg="#34495e").pack(pady=(5, 0))
        
        # Customer Selection Frame
        cust_frame = tk.LabelFrame(main_frame, text="👤 CUSTOMER DETAILS", 
                                 font=("Arial", 12, "bold"), 
                                 bg="#f8f9fa", fg="#2c3e50",
                                 padx=15, pady=15, relief=tk.GROOVE, bd=2)
        cust_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Customer selection row
        cust_row1 = tk.Frame(cust_frame, bg="#f8f9fa")
        cust_row1.pack(fill=tk.X, pady=5)
        
        tk.Label(cust_row1, text="Select Customer:", font=("Arial", 11, "bold"),
                bg="#f8f9fa").pack(side=tk.LEFT, padx=(0, 15))
        
        self.customer_combo = ttk.Combobox(cust_row1, width=50, font=("Arial", 11))
        self.customer_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_select)
        
        tk.Button(cust_row1, text="+ New Customer", command=self.open_customer_window,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor="hand2").pack(side=tk.LEFT)
        
        # Customer info display
        self.customer_info_var = tk.StringVar(value="👤 No customer selected")
        cust_info_label = tk.Label(cust_frame, textvariable=self.customer_info_var,
                                  font=("Arial", 10), fg="#27ae60", bg="#f8f9fa",
                                  justify=tk.LEFT)
        cust_info_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Project Description Frame
        desc_frame = tk.LabelFrame(main_frame, text="📝 PROJECT DESCRIPTION", 
                                 font=("Arial", 12, "bold"),
                                 bg="#f8f9fa", fg="#2c3e50",
                                 padx=15, pady=15, relief=tk.GROOVE, bd=2)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.project_desc = tk.Text(desc_frame, height=6, width=80, 
                                  font=("Arial", 11), wrap=tk.WORD,
                                  relief=tk.SUNKEN, bd=2)
        self.project_desc.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Example text
        example_text = """
📌 EXAMPLES:
• 5000 sqft factory wiring, 20 LED lights, 15 sockets, 2 fans, 3 phase MCB, 100m 1.5sqmm wire
• 2 BHK flat complete wiring, 10 lights, 8 sockets, modular switches, 4 fans, 1 distribution box
• 100 meter 25sqmm copper cable, 2 industrial MCB 63A, 1 distribution board, 5A sockets
"""
        example_label = tk.Label(desc_frame, text=example_text, font=("Arial", 9),
                               fg="#7f8c8d", justify=tk.LEFT, bg="#f8f9fa")
        example_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Generate Button Frame
        btn_frame = tk.Frame(main_frame, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.generate_btn = tk.Button(btn_frame, text="⚡ GENERATE QUOTATION ⚡", 
                                     command=self.generate_ai_quote,
                                     bg="#27ae60", fg="white", 
                                     font=("Arial", 14, "bold"),
                                     height=2, width=30, cursor="hand2",
                                     relief=tk.RAISED, bd=3)
        self.generate_btn.pack(pady=5)
        
        # Results Frame
        results_frame = tk.LabelFrame(main_frame, text="📋 QUOTATION ITEMS", 
                                    font=("Arial", 12, "bold"),
                                    bg="#f8f9fa", fg="#2c3e50",
                                    padx=15, pady=15, relief=tk.GROOVE, bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview with scrollbars
        tree_container = tk.Frame(results_frame, bg="#f8f9fa")
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("Item", "Description", "Qty", "Unit", "Rate (Rs.)", "Amount (Rs.)", "GST%")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=8)
        
        # Define column headings and widths
        column_configs = [
            ("Item", 120),
            ("Description", 250),
            ("Qty", 60),
            ("Unit", 70),
            ("Rate (Rs.)", 100),
            ("Amount (Rs.)", 110),
            ("GST%", 60)
        ]
        
        for col, width in column_configs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        self.tree.column("Description", anchor="w")
        self.tree.column("Item", anchor="w")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Total Calculation Frame
        total_frame = tk.Frame(results_frame, bg="#e8f4f8", relief=tk.RIDGE, bd=3)
        total_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Totals
        self.subtotal_var = tk.StringVar(value="Rs. 0.00")
        self.gst_var = tk.StringVar(value="Rs. 0.00")
        self.total_var = tk.StringVar(value="Rs. 0.00")
        
        # Subtotal
        tk.Label(total_frame, text="SUBTOTAL:", font=("Arial", 11, "bold"),
                bg="#e8f4f8").pack(side=tk.LEFT, padx=(30, 5), pady=12)
        tk.Label(total_frame, textvariable=self.subtotal_var, font=("Arial", 11, "bold"),
                fg="#27ae60", bg="#e8f4f8").pack(side=tk.LEFT, padx=5, pady=12)
        
        # GST
        tk.Label(total_frame, text="GST (18%):", font=("Arial", 11, "bold"),
                bg="#e8f4f8").pack(side=tk.LEFT, padx=(30, 5), pady=12)
        tk.Label(total_frame, textvariable=self.gst_var, font=("Arial", 11, "bold"),
                fg="#e67e22", bg="#e8f4f8").pack(side=tk.LEFT, padx=5, pady=12)
        
        # Grand Total
        tk.Label(total_frame, text="GRAND TOTAL:", font=("Arial", 12, "bold"),
                bg="#e8f4f8", fg="#c0392b").pack(side=tk.LEFT, padx=(30, 5), pady=12)
        tk.Label(total_frame, textvariable=self.total_var, font=("Arial", 13, "bold"),
                fg="#c0392b", bg="#e8f4f8").pack(side=tk.LEFT, padx=5, pady=12)
        
        # Action Buttons Frame
        action_frame = tk.Frame(main_frame, bg="#f8f9fa")
        action_frame.pack(fill=tk.X, pady=15)
        
        # Button configurations
        buttons = [
            ("💾 Save Quotation", self.save_quotation, "#3498db"),
            ("📄 Generate PDF", self.generate_pdf, "#e67e22"),
            ("🔄 Reset All", self.clear_all, "#95a5a6"),
            ("❌ Close", self.window.destroy, "#e74c3c")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(action_frame, text=text, command=command,
                          bg=color, fg="white", font=("Arial", 11, "bold"),
                          width=15, height=1, cursor="hand2",
                          relief=tk.RAISED, bd=2)
            btn.pack(side=tk.LEFT, padx=8)
        
        # Status Bar
        self.status_var = tk.StringVar(value="✅ Ready. Customer select करें और project description लिखें.")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                            font=("Arial", 10), fg="#34495e", 
                            bg="#ecf0f1", relief=tk.SUNKEN, bd=1,
                            anchor=tk.W, padx=10, pady=8)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def load_materials(self):
        """Load materials from database"""
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, category, default_unit, default_rate, default_gst FROM materials")
            self.materials = cursor.fetchall()
            conn.close()
            
            # Create lookup dictionaries
            self.material_rate = {}
            self.material_unit = {}
            self.material_gst = {}
            
            for m in self.materials:
                key = m[0].lower().strip()
                self.material_rate[key] = m[3]
                self.material_unit[key] = m[2]
                self.material_gst[key] = m[4]
            
            self.status_var.set(f"✅ Loaded {len(self.materials)} materials from database")
                
        except Exception as e:
            self.status_var.set(f"❌ Error loading materials: {str(e)}")
            self.materials = []
            self.material_rate = {}
            self.material_unit = {}
            self.material_gst = {}
    
    def load_customers(self):
        """Load customers into combobox"""
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone, address, gstin FROM customers ORDER BY name")
            customers = cursor.fetchall()
            conn.close()
            
            customer_list = []
            self.customer_details = {}
            
            for c in customers:
                display_text = f"{c[1]} - {c[2] if c[2] else 'No Phone'}"
                customer_list.append(display_text)
                self.customer_details[display_text] = {
                    'id': c[0],
                    'name': c[1],
                    'phone': c[2] or "",
                    'address': c[3] or "",
                    'gstin': c[4] or ""
                }
            
            self.customer_combo['values'] = customer_list
            
            if customers:
                self.status_var.set(f"✅ Loaded {len(customers)} customers")
            else:
                self.status_var.set("⚠️ No customers found. Please add a customer first.")
            
        except Exception as e:
            self.status_var.set(f"❌ Error loading customers: {str(e)}")
    
    def on_customer_select(self, event):
        """Handle customer selection"""
        selection = self.customer_combo.get()
        if selection and hasattr(self, 'customer_details') and selection in self.customer_details:
            details = self.customer_details[selection]
            self.selected_customer_id = details['id']
            self.customer_name = details['name']
            self.customer_phone = details['phone']
            self.customer_address = details['address']
            self.customer_gstin = details['gstin']
            
            # Update customer info display
            info_text = f"✓ Customer: {self.customer_name}"
            if self.customer_phone:
                info_text += f" | 📞 {self.customer_phone}"
            if self.customer_gstin:
                info_text += f" | GST: {self.customer_gstin}"
            
            self.customer_info_var.set(info_text)
            self.status_var.set(f"✅ Customer selected: {self.customer_name}")
    
    def open_customer_window(self):
        """Open add customer window"""
        try:
            from customer_window import CustomerWindow
            customer_win = CustomerWindow(self.window, mode='add')
            self.window.wait_window(customer_win.window)
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open customer window: {str(e)}")
    
    def generate_ai_quote(self):
        """PURE AI - Rule based quotation generation"""
        
        # Validate customer
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "❌ पहले Customer select करें!")
            return
        
        description = self.project_desc.get("1.0", tk.END).strip()
        if not description:
            messagebox.showwarning("Warning", "❌ Project description लिखें!")
            return
        
        # Show loading
        self.status_var.set("⏳ AI is processing your request...")
        self.window.update()
        
        # Clear previous items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.items = []
        desc_lower = description.lower()
        items_added = 0
        not_found = []
        
        # ============ PURE AI - RULE ENGINE ============
        
        # 1. WIRES / CABLES
        wire_keywords = ['wire', 'cable', 'वायर', 'तार', 'copper']
        if any(k in desc_lower for k in wire_keywords):
            qty = self.extract_quantity(desc_lower, wire_keywords)
            if qty > 0:
                self.add_item("1.5 sq.mm Copper Wire", "PVC insulated copper wire", qty, "meter", 48.0)
                items_added += 1
                
                # Power wire for heavy loads
                power_keywords = ['power', 'factory', '3 phase', 'तीन फेज']
                if any(k in desc_lower for k in power_keywords):
                    qty2 = int(qty * 0.6) if qty > 0 else 50
                    self.add_item("2.5 sq.mm Copper Wire", "Heavy duty power wire", qty2, "meter", 65.0)
                    items_added += 1
            else:
                not_found.append('wire/cable')
        
        # 2. LIGHTS
        light_keywords = ['light', 'led', 'लाइट', 'बल्ब', 'panel']
        if any(k in desc_lower for k in light_keywords):
            qty = self.extract_quantity(desc_lower, light_keywords)
            if qty > 0:
                self.add_item("LED Panel Light 18W", "LED panel surface mount", qty, "piece", 450.0)
                items_added += 1
            else:
                not_found.append('lights')
        
        # 3. FANS
        fan_keywords = ['fan', 'पंखा', 'ceiling']
        if any(k in desc_lower for k in fan_keywords):
            qty = self.extract_quantity(desc_lower, fan_keywords)
            if qty > 0:
                self.add_item("Ceiling Fan", "1200mm ceiling fan with regulator", qty, "piece", 1500.0)
                items_added += 1
            else:
                not_found.append('fans')
        
        # 4. SOCKETS
        socket_keywords = ['socket', 'सॉकेट', 'plug', 'point']
        if any(k in desc_lower for k in socket_keywords):
            qty = self.extract_quantity(desc_lower, socket_keywords)
            if qty > 0:
                # 15A socket for power
                self.add_item("15A Socket", "15A power socket with switch", qty, "piece", 150.0)
                # 5A socket for normal use
                self.add_item("5A Socket", "5A switch socket", qty, "piece", 120.0)
                items_added += 2
            else:
                not_found.append('sockets')
        
        # 5. SWITCHES
        switch_keywords = ['switch', 'स्विच', 'modular']
        if any(k in desc_lower for k in switch_keywords):
            qty = self.extract_quantity(desc_lower, switch_keywords)
            if qty == 0:
                qty = self.extract_quantity(desc_lower, ['socket']) + 5
            if qty > 0:
                self.add_item("Modular Switch 1-Gang", "1 gang modular switch", qty, "piece", 180.0)
                items_added += 1
            else:
                not_found.append('switches')
        
        # 6. MCB / DISTRIBUTION
        mcb_keywords = ['mcb', 'distribution', 'डिस्ट्रीब्यूशन', 'db', 'board']
        if any(k in desc_lower for k in mcb_keywords):
            self.add_item("6A MCB", "6A SP MCB", 4, "piece", 200.0)
            self.add_item("Distribution Box 8-way", "8 way distribution board", 1, "piece", 800.0)
            items_added += 2
            
            if '3 phase' in desc_lower or 'तीन फेज' in desc_lower or 'industrial' in desc_lower:
                self.add_item("Industrial MCB 63A", "3 phase 63A MCB", 1, "piece", 850.0)
                items_added += 1
        
        # 7. CONDUIT PIPES
        conduit_keywords = ['conduit', 'pipe', 'पाइप', 'pvc']
        if any(k in desc_lower for k in conduit_keywords):
            qty = self.extract_quantity(desc_lower, conduit_keywords)
            if qty > 0:
                self.add_item("20mm PVC Conduit", "PVC conduit pipe", qty, "meter", 30.0)
                items_added += 1
            else:
                # Estimate conduit from wire quantity
                wire_qty = self.extract_quantity(desc_lower, wire_keywords)
                if wire_qty > 0:
                    conduit_qty = int(wire_qty * 0.8)
                    self.add_item("20mm PVC Conduit", "PVC conduit pipe", conduit_qty, "meter", 30.0)
                    items_added += 1
        
        # 8. LABOUR
        area_keywords = ['sqft', 'square', 'sq.ft', 'वर्ग फुट', 'area']
        area = self.extract_quantity(desc_lower, area_keywords)
        
        if area > 0:
            points = max(5, int(area / 150))
            self.add_item("Electrical Labour", f"Installation labour (per point)", points, "point", 300.0)
            items_added += 1
        else:
            # Default labour based on project size
            total_items = len(self.items)
            points = max(5, int(total_items * 1.5))
            self.add_item("Electrical Labour", "Installation labour", points, "point", 300.0)
            items_added += 1
        
        # Check for missing materials
        if not_found:
            self.status_var.set(f"⚠️ Could not detect: {', '.join(not_found)}. Add manually if needed.")
        
        # Calculate totals
        self.calculate_totals()
        
        # Final status
        if items_added > 0:
            self.status_var.set(f"✅ AI generated {items_added} items successfully!")
            messagebox.showinfo("Success", 
                              f"✅ {items_added} items generated!\n\n"
                              f"📊 Subtotal: {self.subtotal_var.get()}\n"
                              f"💰 Grand Total: {self.total_var.get()}\n\n"
                              f"अब Save Quotation या Generate PDF करें।")
        else:
            self.status_var.set("❌ No items matched. Please be more descriptive.")
            messagebox.showwarning("No Match", 
                                 "❌ कोई item match नहीं हुआ।\n\n"
                                 "कृपया और detail में लिखें:\n"
                                 "• कितने lights?\n"
                                 "• कितने fans?\n"
                                 "• कितने sockets?\n"
                                 "• wire quantity?\n"
                                 "• area (sqft)?")
    
    def extract_quantity(self, text, keywords):
        """Extract quantity from text with validation"""
        quantity = 0
        for keyword in keywords:
            # Find numbers before keyword
            pattern = r'(\d+)\s*' + re.escape(keyword)
            matches = re.findall(pattern, text)
            
            for match in matches:
                try:
                    qty = int(match)
                    if 0 < qty < 10000:  # Sanity check
                        quantity += qty
                    else:
                        self.status_var.set(f"⚠️ Unusual quantity {qty} for {keyword}")
                except ValueError:
                    continue
        
        return quantity
    
    def add_item(self, name, desc, qty, unit, rate):
        """Add item to quotation with duplicate check"""
        
        # Validation: Quantity must be positive
        if qty <= 0:
            return False
        
        # Check for duplicate (same name and rate)
        for item in self.items:
            if item['name'] == name and item['rate'] == rate:
                # Update quantity
                old_qty = item['quantity']
                item['quantity'] += qty
                item['amount'] = item['quantity'] * item['rate']
                item['description'] = desc  # Update description
                
                # Update in treeview
                for child in self.tree.get_children():
                    values = self.tree.item(child)['values']
                    if values and len(values) > 0 and values[0] == name[:20]:
                        self.tree.item(child, values=(
                            name[:20], 
                            desc[:30], 
                            f"{item['quantity']:.0f}", 
                            unit, 
                            f"Rs. {rate:,.2f}", 
                            f"Rs. {item['amount']:,.2f}", 
                            "18%"
                        ))
                        break
                
                self.status_var.set(f"🔄 Updated {name}: +{qty} (Total: {item['quantity']})")
                return True
        
        # New item
        amount = qty * rate
        self.items.append({
            'name': name,
            'description': desc,
            'quantity': qty,
            'unit': unit,
            'rate': rate,
            'gst': 18,
            'amount': amount
        })
        
        # Add to treeview
        self.tree.insert("", "end", values=(
            name[:20], 
            desc[:30], 
            f"{qty:.0f}", 
            unit, 
            f"Rs. {rate:,.2f}", 
            f"Rs. {amount:,.2f}", 
            "18%"
        ))
        
        self.status_var.set(f"✅ Added: {name} x{qty}")
        return True
    
    def calculate_totals(self):
        """Calculate subtotal, GST and grand total"""
        subtotal = sum(item['amount'] for item in self.items)
        gst = subtotal * 0.18
        grand_total = subtotal + gst
        
        self.subtotal_var.set(f"Rs. {subtotal:,.2f}")
        self.gst_var.set(f"Rs. {gst:,.2f}")
        self.total_var.set(f"Rs. {grand_total:,.2f}")
    
    def save_quotation(self):
        """Save quotation to database - FINAL FIXED VERSION"""
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "❌ पहले Customer select करें!")
            return
        
        if not self.items:
            messagebox.showwarning("Warning", "❌ पहले quotation generate करें!")
            return
        
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            # Calculate totals
            subtotal = sum(item['amount'] for item in self.items)
            gst = subtotal * 0.18
            grand_total = subtotal + gst
            
            # Generate quotation number
            date_str = datetime.now().strftime('%Y%m%d')
            cursor.execute("SELECT COUNT(*) FROM quotations WHERE quote_no LIKE ?", (f"QT-{date_str}-%",))
            count = cursor.fetchone()[0] + 1
            quote_no = f"QT-{date_str}-{count:03d}"
            
            # Insert quotation
            cursor.execute('''
                INSERT INTO quotations (quote_no, date, customer_id, subtotal, gst_amount, grand_total, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (quote_no, datetime.now().strftime('%Y-%m-%d'), 
                  self.selected_customer_id, subtotal, gst, grand_total, 'Draft'))
            
            quotation_id = cursor.lastrowid
            
            # 🔥 FIXED: Insert items with EXPLICIT column names and ALL values
            for item in self.items:
                cursor.execute('''
                    INSERT INTO quotation_items 
                    (quotation_id, item_name, description, quantity, unit, rate, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quotation_id, 
                    item['name'], 
                    item['description'],  # ✅ description value देना
                    item['quantity'], 
                    item['unit'], 
                    item['rate'], 
                    item['amount']
                ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"✅ Quotation {quote_no} saved successfully!")
            self.status_var.set(f"✅ Quotation {quote_no} saved!")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to save: {str(e)}")
            return False    
    
    def generate_pdf(self):
        """Generate PDF for quotation"""
        # Validation: Items exist?
        if not self.items:
            messagebox.showwarning("Warning", "❌ पहले quotation generate करें!")
            return
        
        # Validation: Customer selected?
        if not self.selected_customer_id:
            messagebox.showwarning("Warning", "❌ पहले Customer select करें!")
            return
        
        try:
            # Import PDF generator
            from pdf_generator import PDFGenerator
            
            # Calculate totals
            subtotal = sum(item['amount'] for item in self.items)
            gst = subtotal * 0.18
            grand_total = subtotal + gst
            
            # Create quotation data dictionary with customer details
            quote_data = {
                'quote_no': f"AI-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'date': datetime.now().strftime('%d-%b-%Y'),
                'customer_name': self.customer_name or "Customer",
                'customer_phone': self.customer_phone or "",
                'customer_address': self.customer_address or "",
                'customer_gstin': self.customer_gstin or "",
                'subtotal': subtotal,
                'gst_amount': gst,
                'grand_total': grand_total,
                'items': self.items
            }
            
            # Generate PDF
            pdf = PDFGenerator()
            filename = f"quotation_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            self.status_var.set("⏳ PDF generating... please wait")
            self.window.update()
            
            success = pdf.generate_quotation_pdf_from_dict(quote_data, filename)
            
            if success:
                self.status_var.set(f"✅ PDF generated: {filename}")
                
                # Ask if user wants to open PDF
                if messagebox.askyesno("Open PDF", 
                                     "✅ PDF तैयार है!\n\n"
                                     f"📄 {filename}\n\n"
                                     "अभी खोलना चाहेंगे?"):
                    try:
                        os.startfile(filename)  # Windows
                    except:
                        self.status_var.set(f"✅ PDF saved: {filename}")
            else:
                self.status_var.set("❌ PDF generation failed")
                messagebox.showerror("Error", "❌ PDF generation failed!")
            
        except ImportError:
            messagebox.showerror("Error", "❌ PDF Generator module not found!\nPlease check pdf_generator.py")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to generate PDF: {str(e)}")
    
    def clear_all(self):
        """Reset everything to initial state"""
        
        # Clear text
        self.project_desc.delete("1.0", tk.END)
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear data
        self.items = []
        self.selected_customer_id = None
        self.customer_name = None
        self.customer_phone = None
        self.customer_address = None
        self.customer_gstin = None
        
        # Reset combobox
        self.customer_combo.set('')
        
        # Reset customer info
        self.customer_info_var.set("👤 No customer selected")
        
        # Reset totals
        self.subtotal_var.set("Rs. 0.00")
        self.gst_var.set("Rs. 0.00")
        self.total_var.set("Rs. 0.00")
        
        # Update status
        self.status_var.set("✅ Reset complete. New quotation ready.")
        
        # Reload customers
        self.load_customers()
        
        # Beep sound
        self.window.bell()


# ============ MAIN ============
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("AI Quote Generator - ContractorMitra")
        root.geometry("1000x750")
        
        # Set window icon (if available)
        try:
            root.iconbitmap('icon.ico')
        except:
            pass
        
        app = AIQuoteGenerator(root)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        try:
            messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        except:
            pass