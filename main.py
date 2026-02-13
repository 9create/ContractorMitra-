import tkinter as tk
from tkinter import messagebox
import os
import sys

class ModernStyle:
    BG_COLOR = "#f5f5f7"
    CARD_BG = "white"
    TEXT_PRIMARY = "#1d1d1f"
    TEXT_SECONDARY = "#86868b"
    ACCENT_BLUE = "#3498db"
    ACCENT_GREEN = "#2ecc71"
    ACCENT_ORANGE = "#f39c12"
    ACCENT_RED = "#e74c3c"
    ACCENT_PURPLE = "#9b59b6"
    ACCENT_TEAL = "#1abc9c"
    
    FONT_HEADER = ("SF Pro Display", 24, "bold")
    FONT_TITLE = ("SF Pro Display", 18, "bold")
    FONT_NORMAL = ("SF Pro Text", 11)
    FONT_SMALL = ("SF Pro Text", 10)

class ModernButton:
    def __init__(self, parent, text, command, color=ModernStyle.ACCENT_BLUE, width=200, height=50):
        self.frame = tk.Frame(parent, bg=ModernStyle.BG_COLOR)
        self.canvas = tk.Canvas(self.frame, width=width, height=height, 
                               highlightthickness=0, bg=ModernStyle.BG_COLOR)
        self.canvas.pack()
        self.command = command
        self.color = color
        self.text = text
        
        self.draw_button(color)
        
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
    
    def draw_button(self, fill_color):
        self.canvas.delete("all")
        # Rounded rectangle
        self.canvas.create_rounded_rect(5, 5, 195, 45, 10, fill=fill_color, outline="")
        self.canvas.create_text(100, 25, text=self.text, fill="white", 
                               font=ModernStyle.FONT_NORMAL)
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, 
                 x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, 
                 x1, y1+r, x1, y1]
        self.canvas.create_polygon(points, smooth=True, **kwargs)
    
    def darken(self, color):
        color = color.lstrip('#')
        r,g,b = int(color[0:2],16), int(color[2:4],16), int(color[4:6],16)
        return f"#{max(0,r-20):02x}{max(0,g-20):02x}{max(0,b-20):02x}"
    
    def on_enter(self, event):
        self.draw_button(self.darken(self.color))
    
    def on_leave(self, event):
        self.draw_button(self.color)
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ContractorMitra")
        self.root.geometry("1200x700")
        self.root.configure(bg=ModernStyle.BG_COLOR)
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def setup_ui(self):
        main = tk.Frame(self.root, bg=ModernStyle.BG_COLOR)
        main.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Header
        header = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        header.pack(fill=tk.X, pady=(0,40))
        
        tk.Label(header, text="ContractorMitra", 
                font=ModernStyle.FONT_HEADER,
                fg=ModernStyle.TEXT_PRIMARY, bg=ModernStyle.BG_COLOR).pack()
        
        tk.Label(header, 
                text="Professional Quotation & Billing Software for Electrical & Civil Contractors",
                font=ModernStyle.FONT_NORMAL,
                fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR).pack(pady=(10,0))
        
        # Cards Grid
        cards_frame = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        cards_frame.pack(expand=True, fill=tk.BOTH)
        
        # Configure grid
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="group")
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
        
        # Card data
        cards = [
            {"title": "📋 New Quotation", "desc": "Create professional quotations in seconds",
             "color": ModernStyle.ACCENT_BLUE, "cmd": self.new_quotation},
            {"title": "👥 Customers", "desc": "Manage your customer database",
             "color": ModernStyle.ACCENT_GREEN, "cmd": self.manage_customers},
            {"title": "📦 Materials", "desc": "Track your material inventory",
             "color": ModernStyle.ACCENT_ORANGE, "cmd": self.manage_materials},
            {"title": "📊 Reports", "desc": "View sales & payment reports",
             "color": ModernStyle.ACCENT_PURPLE, "cmd": self.view_reports},
            {"title": "💰 Pending Payments", "desc": "Track outstanding payments",
             "color": ModernStyle.ACCENT_RED, "cmd": self.pending_payments},
            {"title": "🤖 AI Quote", "desc": "AI-powered quotation generator",
             "color": ModernStyle.ACCENT_TEAL, "cmd": self.ai_quote}
        ]
        
        for idx, card in enumerate(cards):
            row = idx // 3
            col = idx % 3
            self.create_card(cards_frame, card, row, col)
        
        # Footer
        footer = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        footer.pack(fill=tk.X, pady=(30,0))
        
        tk.Label(footer, 
                text="Made with ❤️ by ContractorMitra • v3.0 • Production Ready",
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR).pack()
    
    def create_card(self, parent, card, row, col):
        card_frame = tk.Frame(parent, bg="white", relief=tk.FLAT)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        inner = tk.Frame(card_frame, bg="white")
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(inner, text=card["title"], 
                font=ModernStyle.FONT_TITLE,
                fg=ModernStyle.TEXT_PRIMARY, bg="white").pack(anchor=tk.W, pady=(0,10))
        
        tk.Label(inner, text=card["desc"],
                font=ModernStyle.FONT_SMALL,
                fg=ModernStyle.TEXT_SECONDARY, bg="white",
                wraplength=200, justify=tk.LEFT).pack(anchor=tk.W, pady=(0,20))
        
        ModernButton(inner, "Open →", card["cmd"], card["color"], 150, 40).pack()
        
        def on_enter(e):
            inner.configure(bg='#f8f9fa')
            for w in inner.winfo_children():
                if isinstance(w, tk.Label):
                    w.configure(bg='#f8f9fa')
        
        def on_leave(e):
            inner.configure(bg='white')
            for w in inner.winfo_children():
                if isinstance(w, tk.Label):
                    w.configure(bg='white')
        
        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)
    
    def new_quotation(self):
        """Open New Quotation Window"""
        try:
            from ai_quote_generator import AIQuoteGenerator
            AIQuoteGenerator(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AI Quote Generator: {str(e)}")
    
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
    
    def ai_quote(self):
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