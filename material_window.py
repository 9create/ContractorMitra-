import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class MaterialWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Material Management - ContractorMitra")
        self.window.geometry("1000x600")
        
        # Initialize
        self.setup_ui()
        self.load_materials()
    
    def setup_ui(self):
        """Setup material window UI"""
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="MATERIAL DATABASE", 
                font=("Arial", 16, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        
        # Search and buttons frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var.trace('w', self.on_search)
        
        tk.Button(search_frame, text="+ Add New", command=self.add_material,
                 bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(search_frame, text="Refresh", command=self.load_materials,
                 bg="#3498db", fg="white").pack(side=tk.LEFT)
        
        # Treeview
        columns = ("ID", "Material Name", "Category", "Unit", "Default Rate (₹)", "Default GST %")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Material Name", width=250)
        self.tree.column("Default Rate (₹)", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Edit Selected", command=self.edit_material,
                 bg="#f39c12", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Delete Selected", command=self.delete_material,
                 bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Import from Excel", command=self.import_excel,
                 bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Export to Excel", command=self.export_excel,
                 bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", command=self.window.destroy,
                 bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)
    
    def load_materials(self):
        """Load materials into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, default_unit, default_rate, default_gst FROM materials ORDER BY name")
        materials = cursor.fetchall()
        conn.close()
        
        for material in materials:
            self.tree.insert("", "end", values=material)
    
    def on_search(self, *args):
        """Search materials"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.load_materials()
            return
        
        # Filter in memory
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, default_unit, default_rate, default_gst FROM materials")
        all_materials = cursor.fetchall()
        conn.close()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and insert
        for material in all_materials:
            if (search_term in material[1].lower() or  # name
                search_term in material[2].lower()):  # category
                self.tree.insert("", "end", values=material)
    
    def add_material(self):
        """Add new material"""
        add_window = tk.Toplevel(self.window)
        add_window.title("Add New Material")
        add_window.geometry("400x400")
        
        tk.Label(add_window, text="ADD NEW MATERIAL", 
                font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=(10, 20))
        
        form_frame = tk.Frame(add_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        fields = [
            ("Material Name *", "name"),
            ("Category", "category"),
            ("Default Unit", "unit"),
            ("Default Rate (₹)", "rate"),
            ("Default GST %", "gst")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            
            if key == 'category':
                # Category dropdown
                categories = ["Wires", "Switches", "Sockets", "Conduits", "Lighting", 
                            "Fans", "Protection", "Labour", "Civil", "Other"]
                entry = ttk.Combobox(form_frame, values=categories, width=27)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            elif key == 'unit':
                # Unit dropdown
                units = ["meter", "piece", "set", "kg", "roll", "day", "hour", "point", "sq.ft"]
                entry = ttk.Combobox(form_frame, values=units, width=27)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            elif key in ['rate', 'gst']:
                entry = tk.Entry(form_frame, width=30)
                entry.insert(0, "0.0" if key == 'rate' else "18.0")
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            else:
                entry = tk.Entry(form_frame, width=30)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            
            entries[key] = entry
        
        def save_material():
            name = entries['name'].get().strip()
            if not name:
                messagebox.showwarning("Warning", "Material name is required")
                return
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO materials (name, category, default_unit, default_rate, default_gst)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    name,
                    entries['category'].get().strip(),
                    entries['unit'].get().strip(),
                    float(entries['rate'].get() or 0),
                    float(entries['gst'].get() or 18)
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Material added successfully!")
                add_window.destroy()
                self.load_materials()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add material: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(add_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Material", command=save_material,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=add_window.destroy,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    
    def edit_material(self):
        """Edit selected material"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a material to edit")
            return
        
        # Get material ID
        item = self.tree.item(selected[0])
        material_id = item['values'][0]
        
        # Open edit window
        self.open_edit_window(material_id)
    
    def open_edit_window(self, material_id):
        """Open window to edit material"""
        # Fetch material data
        conn = sqlite3.connect('contractormitra.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, category, default_unit, default_rate, default_gst FROM materials WHERE id = ?", (material_id,))
        material = cursor.fetchone()
        conn.close()
        
        if not material:
            messagebox.showerror("Error", "Material not found")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Material")
        edit_window.geometry("400x400")
        
        tk.Label(edit_window, text="EDIT MATERIAL", 
                font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=(10, 20))
        
        form_frame = tk.Frame(edit_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        fields = [
            ("Material Name *", "name", material[0]),
            ("Category", "category", material[1]),
            ("Default Unit", "unit", material[2]),
            ("Default Rate (₹)", "rate", material[3]),
            ("Default GST %", "gst", material[4])
        ]
        
        entries = {}
        for i, (label, key, value) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=10, sticky=tk.W)
            
            if key == 'category':
                categories = ["Wires", "Switches", "Sockets", "Conduits", "Lighting", 
                            "Fans", "Protection", "Labour", "Civil", "Other"]
                entry = ttk.Combobox(form_frame, values=categories, width=27)
                entry.set(value)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            elif key == 'unit':
                units = ["meter", "piece", "set", "kg", "roll", "day", "hour", "point", "sq.ft"]
                entry = ttk.Combobox(form_frame, values=units, width=27)
                entry.set(value)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            else:
                entry = tk.Entry(form_frame, width=30)
                entry.insert(0, str(value))
                entry.grid(row=i, column=1, padx=10, pady=10, sticky=tk.W)
            
            entries[key] = entry
        
        def save_changes():
            name = entries['name'].get().strip()
            if not name:
                messagebox.showwarning("Warning", "Material name is required")
                return
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE materials 
                    SET name = ?, category = ?, default_unit = ?, default_rate = ?, default_gst = ?
                    WHERE id = ?
                ''', (
                    name,
                    entries['category'].get().strip(),
                    entries['unit'].get().strip(),
                    float(entries['rate'].get() or 0),
                    float(entries['gst'].get() or 18),
                    material_id
                ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Material updated successfully!")
                edit_window.destroy()
                self.load_materials()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save Changes", command=save_changes,
                 bg="#27ae60", fg="white", width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=edit_window.destroy,
                 bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    
    def delete_material(self):
        """Delete selected material"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a material to delete")
            return
        
        item = self.tree.item(selected[0])
        material_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete material:\n{material_name}?"):
            material_id = item['values'][0]
            
            try:
                conn = sqlite3.connect('contractormitra.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Material deleted successfully!")
                self.load_materials()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def import_excel(self):
        """Import materials from Excel"""
        messagebox.showinfo("Info", "Excel import will be implemented in next version")
    
    def export_excel(self):
        """Export materials to Excel"""
        messagebox.showinfo("Info", "Excel export will be implemented in next version")