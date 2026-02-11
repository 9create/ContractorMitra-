# pdf_generator.py
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import sqlite3

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for PDF"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='QuotationTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalCenter',
            parent=self.styles['Normal'],
            alignment=1,  # Center alignment
            fontSize=10
        ))
    
    def generate_quotation_pdf(self, quotation_id, output_path="quotation.pdf"):
        """Generate PDF for a quotation"""
        # Get quotation data from database
        quote_data = self.get_quotation_data(quotation_id)
        if not quote_data:
            return False
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # 1. Company Header
        story.append(Paragraph("RAJESH ELECTRICALS & CIVIL WORKS", self.styles['CompanyName']))
        story.append(Paragraph("Professional Electrical & Civil Contractor", self.styles['NormalCenter']))
        story.append(Paragraph("GSTIN: 27ABCDE1234F1Z5 | Phone: 9876543210", self.styles['NormalCenter']))
        story.append(Paragraph("Address: 123, Main Road, Pune, Maharashtra - 411001", self.styles['NormalCenter']))
        story.append(Spacer(1, 20))
        
        # 2. Quotation Title
        story.append(Paragraph("TAX INVOICE / QUOTATION", self.styles['QuotationTitle']))
        story.append(Spacer(1, 10))
        
        # 3. Quotation Details Table
        quote_details = [
            ["Quotation No:", quote_data['quote_no'], "Date:", quote_data['date']],
            ["Customer:", quote_data['customer_name'], "Phone:", quote_data['customer_phone']],
            ["Address:", quote_data['customer_address'], "GSTIN:", quote_data['customer_gstin'] or "N/A"]
        ]
        
        quote_table = Table(quote_details, colWidths=[80, 200, 60, 200])
        quote_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(quote_table)
        story.append(Spacer(1, 20))
        
        # 4. Items Table
        story.append(Paragraph("Description of Works / Materials", self.styles['Heading3']))
        story.append(Spacer(1, 10))
        
        # Table headers
        table_data = [["Sr.No", "Description", "Quantity", "Unit", "Rate (Rs.)", "Amount (Rs.)"]]
        
        # Add items
        for idx, item in enumerate(quote_data['items'], 1):
            table_data.append([
                str(idx),
                item['item_name'],
                str(item['quantity']),
                item['unit'],
                f"{item['rate']:,.2f}",
                f"{item['amount']:,.2f}"
            ])
        
        # Create table
        items_table = Table(table_data, colWidths=[30, 220, 60, 50, 80, 80])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # 5. Totals Table
        totals_data = [
            ["", "", "Sub Total:", f"Rs. {quote_data['subtotal']:,.2f}"],
            ["", "", "GST @ 18%:", f"Rs. {quote_data['gst_amount']:,.2f}"],
            ["", "", "Grand Total:", f"Rs. {quote_data['grand_total']:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[100, 100, 100, 100])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),     # Blank columns - center
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),      # Labels - right aligned
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),      # Amounts - right aligned
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (2, 0), (3, -1), 11),        # Labels & amounts - bigger
            ('FONTSIZE', (0, 0), (1, -1), 8),         # Blank columns - small
            ('FONTNAME', (2, 2), (3, 2), 'Helvetica-Bold'),  # Grand Total bold
            ('LINEABOVE', (2, 2), (3, 2), 1, colors.black),   # Line above Grand Total
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 30))
        
        # 6. Terms and Conditions
        story.append(Paragraph("Terms & Conditions:", self.styles['Heading4']))
        terms = [
            "1. Validity: This quotation is valid for 30 days from the date of issue.",
            "2. Payment: 50% advance payment before starting work, balance on completion.",
            "3. GST: All prices are inclusive of GST @ 18%.",
            "4. Warranty: 1 year warranty on materials and workmanship.",
            "5. Delivery: Delivery within 7-10 days after advance payment.",
        ]
        
        for term in terms:
            story.append(Paragraph(term, self.styles['Normal']))
            story.append(Spacer(1, 3))
        
        story.append(Spacer(1, 20))
        
        # 7. Bank Details
        bank_data = [
            ["Bank Name:", "State Bank of India", "Account No:", "123456789012"],
            ["Branch:", "Pune Main Branch", "IFSC Code:", "SBIN0001234"],
            ["Account Name:", "Rajesh Electricals", "UPI ID:", "rajesh-electricals@okhdfcbank"]
        ]
        
        bank_table = Table(bank_data, colWidths=[80, 150, 80, 150])
        bank_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(bank_table)
        
        # 8. Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("For Rajesh Electricals & Civil Works", self.styles['NormalCenter']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Authorized Signatory", self.styles['NormalCenter']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("_________________________", self.styles['NormalCenter']))
        
        # Generate PDF
        doc.build(story)
        return True
    
    def get_quotation_data(self, quotation_id):
        """Fetch quotation data from database"""
        try:
            conn = sqlite3.connect('contractormitra.db')
            cursor = conn.cursor()
            
            # Get quotation details
            cursor.execute('''
                SELECT q.id, q.quote_no, q.date, q.subtotal, q.gst_amount, q.grand_total, 
                       c.name, c.phone, c.address, c.gstin
                FROM quotations q
                LEFT JOIN customers c ON q.customer_id = c.id
                WHERE q.id = ?
            ''', (quotation_id,))
            
            quote = cursor.fetchone()
            if not quote:
                return None
            
            # Get quotation items
            cursor.execute('''
                SELECT item_name, quantity, unit, rate, amount
                FROM quotation_items
                WHERE quotation_id = ?
                ORDER BY id
            ''', (quotation_id,))
            
            items = cursor.fetchall()
            
            conn.close()
            
            # Format data
            quote_data = {
                'id': quote[0],
                'quote_no': quote[1],
                'date': quote[2],
                'subtotal': float(quote[3]) if quote[3] else 0,
                'gst_amount': float(quote[4]) if quote[4] else 0,
                'grand_total': float(quote[5]) if quote[5] else 0,
                'customer_name': quote[6] or "",
                'customer_phone': quote[7] or "",
                'customer_address': quote[8] or "",
                'customer_gstin': quote[9] or "",
                'items': []
            }
            
            for item in items:
                quote_data['items'].append({
                    'item_name': item[0],
                    'quantity': float(item[1]) if item[1] else 0,
                    'unit': item[2] or "",
                    'rate': float(item[3]) if item[3] else 0,
                    'amount': float(item[4]) if item[4] else 0
                })
            
            return quote_data
            
        except Exception as e:
            print(f"Error fetching quotation data: {e}")
            return None
    
    def generate_sales_report_pdf(self, report_data, output_path="sales_report.pdf"):
        """Generate PDF for sales report"""
        # Similar to above but for reports
        pass

# Quick test function
def test_pdf_generation():
    """Test PDF generation"""
    generator = PDFGenerator()
    
    # Test with first quotation in database
    conn = sqlite3.connect('contractormitra.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM quotations LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        success = generator.generate_quotation_pdf(result[0], "test_quotation.pdf")
        if success:
            print("✅ PDF generated successfully: test_quotation.pdf")
        else:
            print("❌ Failed to generate PDF")
    else:
        print("⚠️ No quotations found in database")

if __name__ == "__main__":
    test_pdf_generation()