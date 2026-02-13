import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class ModernButton(tk.Canvas):
    """Custom modern button with rounded corners and hover effect"""
    def __init__(self, parent, text, command=None, width=200, height=50, 
                 bg_color="#ffffff", fg_color="#2c3e50", accent_color="#3498db", 
                 font=("SF Pro Display", 12, "bold")):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg='#f5f5f7')
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.accent_color = accent_color
        self.text = text
        self.font = font
        self.width = width
        self.height = height
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button(bg_color)
    
    def draw_button(self, color):
        self.delete("all")
        # Rounded rectangle
        self.create_rounded_rect(5, 5, self.width-5, self.height-5, 15, fill=color, outline="", tags="button")
        # Text
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=self.fg_color, font=self.font, tags="text")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.draw_button(self.accent_color)
        self.itemconfig("text", fill="white")
    
    def on_leave(self, event):
        self.draw_button(self.bg_color)
        self.itemconfig("text", fill=self.fg_color)
    
    def on_click(self, event):
        if self.command:
            self.command()

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ContractorMitra")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f5f5f7')
        
        # Center window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#f5f5f7')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f5f5f7')
        header_frame.pack(fill=tk.X, pady=(0, 40))
        
        # Logo/Title
        title_label = tk.Label(header_frame, text="ContractorMitra", 
                              font=("SF Pro Display", 32, "bold"),
                              fg="#1d1d1f", bg='#f5f5f7')
        title_label.pack()
        
        subtitle = tk.Label(header_frame, text="Professional Quotation & Billing Software\nfor Electrical & Civil Contractors",
                          font=("SF Pro Text", 14), fg="#86868b", bg='#f5f5f7', justify=tk.CENTER)
        subtitle.pack(pady=(10, 0))
        
        # Cards Grid Frame
        cards_frame = tk.Frame(main_frame, bg='#f5f5f7')
        cards_frame.pack(expand=True, fill=tk.BOTH)
        
        # Configure grid
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="group")
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
        
        # Card data
        cards = [
            {"title": "📋 New Quotation", "desc": "Create professional quotations in seconds", "color": "#3498db", "command": self.new_quotation},
            {"title": "👥 Customers", "desc": "Manage your customer database", "color": "#2ecc71", "command": self.manage_customers},
            {"title": "📦 Materials", "desc": "Track your material inventory", "color": "#f39c12", "command": self.manage_materials},
            {"title": "📊 Reports", "desc": "View sales & payment reports", "color": "#9b59b6", "command": self.view_reports},
            {"title": "💰 Pending Payments", "desc": "Track outstanding payments", "color": "#e74c3c", "command": self.pending_payments},
            {"title": "🤖 AI Quote", "desc": "AI-powered quotation generator", "color": "#1abc9c", "command": self.ai_quote_generator},
        ]
        
        # Create cards in grid
        for idx, card in enumerate(cards):
            row = idx // 3
            col = idx % 3
            self.create_card(cards_frame, card, row, col)
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#f5f5f7')
        footer_frame.pack(fill=tk.X, pady=(30, 0))
        
        footer_text = tk.Label(footer_frame, 
                              text="Made with ❤️ by ContractorMitra • v2.0 • Clean Edition",
                              font=("SF Pro Text", 10), fg="#86868b", bg='#f5f5f7')
        footer_text.pack()
    
    def create_card(self, parent, card, row, col):
        """Create a modern card"""
        card_frame = tk.Frame(parent, bg='white', relief=tk.FLAT, bd=0)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Add shadow effect with padding
        inner_frame = tk.Frame(card_frame, bg='white')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title
        title = tk.Label(inner_frame, text=card["title"], 
                        font=("SF Pro Display", 16, "bold"),
                        fg="#1d1d1f", bg='white')
        title.pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        # Description
        desc = tk.Label(inner_frame, text=card["desc"],
                       font=("SF Pro Text", 11), fg="#86868b", bg='white',
                       wraplength=200, justify=tk.LEFT)
        desc.pack(anchor=tk.W, padx=20, pady=(0, 20))
        
        # Button
        btn = ModernButton(inner_frame, text="Open →", command=card["command"],
                          width=150, height=40, bg_color='white',
                          fg_color=card["color"], accent_color=card["color"])
        btn.pack(pady=(0, 20))
        
        # Hover effect for card
        def on_card_enter(e):
            inner_frame.configure(bg='#f8f9fa')
            for widget in inner_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg='#f8f9fa')
        
        def on_card_leave(e):
            inner_frame.configure(bg='white')
            for widget in inner_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg='white')
        
        inner_frame.bind("<Enter>", on_card_enter)
        inner_frame.bind("<Leave>", on_card_leave)
        for widget in inner_frame.winfo_children():
            widget.bind("<Enter>", on_card_enter)
            widget.bind("<Leave>", on_card_leave)
    
    def new_quotation(self):
        messagebox.showinfo("Coming Soon", "New Quotation feature coming in Phase 2")
    
    def manage_customers(self):
        try:
            from customer_window import CustomerWindow
            CustomerWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Customer Window: {str(e)}")
    
    def manage_materials(self):
        try:
            from material_window import MaterialWindow
            MaterialWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Material Window: {str(e)}")
    
    def view_reports(self):
        try:
            from reports_window import ReportsWindow
            ReportsWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Reports: {str(e)}")
    
    def pending_payments(self):
        try:
            from pending_window import PendingWindow
            PendingWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Pending Payments: {str(e)}")
    
    def ai_quote_generator(self):
        try:
            from ai_quote_generator import AIQuoteGenerator
            AIQuoteGenerator(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AI Quote Generator: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()