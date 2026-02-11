# fix_all.py
import sqlite3

conn = sqlite3.connect('contractormitra.db')
cursor = conn.cursor()

# 1. Customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
)
''')

# 2. Quotations table
cursor.execute('DROP TABLE IF EXISTS quotations')
cursor.execute('''
CREATE TABLE quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_no TEXT UNIQUE NOT NULL,
    customer_id INTEGER,
    date DATE NOT NULL,
    subtotal REAL DEFAULT 0,
    gst_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft'
)
''')

# 3. Add sample data
cursor.execute("INSERT OR IGNORE INTO customers (id, name, phone) VALUES (1, 'Rajesh Electricals', '9876543210')")
cursor.execute('''
INSERT INTO quotations (quote_no, customer_id, date, subtotal, gst_amount, grand_total, status)
VALUES ('QT-PDF-FINAL', 1, '2024-02-10', 12600.0, 1458.0, 14058.0, 'Draft')
''')

conn.commit()
conn.close()
print("✅ All tables created!")