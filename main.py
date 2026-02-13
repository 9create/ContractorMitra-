import tkinter as tk
from tkinter import ttk, messagebox
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

class ModernButton(tk.Button):
    def __init__(self, parent, text, command, bg_color=ModernStyle.ACCENT_BLUE, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=ModernStyle.FONT_NORMAL,
            bg=bg_color,
            fg="white",
            activebackground=self.darken(bg_color),
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            **kwargs
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def darken(self, color):
        color = color.lstrip('#')
        r,g,b = int(color[0:2],16), int(color[2:4],16), int(color[4:6],16)
        return f"#{max(0,r-20):02x}{max(0,g-20):02x}{max(0,b-20):02x}"

    def on_enter(self, e):
        self.config(bg=self.darken(self['bg']))

    def on_leave(self, e):
        self.config(bg=self['bg'])

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
                text="Professional Quotation & Billing Software",
                font=ModernStyle.FONT_NORMAL,
                fg=ModernStyle.TEXT_SECONDARY, bg=ModernStyle.BG_COLOR).pack()

        # Cards Grid
        cards_frame = tk.Frame(main, bg=ModernStyle.BG_COLOR)
        cards_frame.pack(expand=True, fill=tk.BOTH)

        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="group")
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)

        cards = [
            {"title": "📋 New Quotation", "desc": "Create professional quotations",
             "color": ModernStyle.ACCENT_BLUE, "cmd": self.new_quotation},
            {"title": "👥 Customers", "desc": "Manage customer database",
             "color": ModernStyle.ACCENT_GREEN, "cmd": self.manage_customers},
            {"title": "📦 Materials", "desc": "Track material inventory",
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

        ModernButton(inner, "Open →", card["cmd"], card["color"]).pack()

    def new_quotation(self):
        try:
            from ai_quote_generator import AIQuoteGenerator
            AIQuoteGenerator(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def manage_customers(self):
        try:
            from customer_window import CustomerWindow
            CustomerWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def manage_materials(self):
        try:
            from material_window import MaterialWindow
            MaterialWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_reports(self):
        try:
            from reports_window import ReportsWindow
            ReportsWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pending_payments(self):
        try:
            from pending_window import PendingWindow
            PendingWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ai_quote(self):
        try:
            from ai_quote_generator import AIQuoteGenerator
            AIQuoteGenerator(self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()