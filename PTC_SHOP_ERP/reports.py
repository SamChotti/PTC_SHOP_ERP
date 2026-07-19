from PySide6.QtWidgets import *
from PySide6.QtCore import QDate
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)

        # Filter Bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setCalendarPopup(True)
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        filter_layout.addWidget(self.to_date)

        filter_layout.addWidget(QLabel("Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.addItem("ALL DRIVERS")
        filter_layout.addWidget(self.driver_combo)

        btn_generate = QPushButton("🔍 Generate Report")
        btn_generate.clicked.connect(self.generate_report)
        filter_layout.addWidget(btn_generate)
        layout.addLayout(filter_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_excel = QPushButton("📊 Export to Excel")
        btn_excel.clicked.connect(self.export_excel)
        btn_summary = QPushButton("🖨️ Print Summary")
        btn_summary.clicked.connect(lambda: self.print_summary_pdf())
        btn_bill = QPushButton("🧾 Print Driver Bill Receipt")
        btn_bill.clicked.connect(lambda: self.print_driver_bill_pdf())
        btn_layout.addWidget(btn_excel)
        btn_layout.addWidget(btn_summary)
        btn_layout.addWidget(btn_bill)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.load_drivers()

    def load_drivers(self):
        drivers = self.db.driver_master['DRIVER NAME'].dropna().tolist()
        self.driver_combo.addItems(drivers)

    def get_filtered_data(self):
        df = self.db.freight_data.copy()
        if df.empty: return pd.DataFrame()

        # Date fix
        df['DATE'] = pd.to_datetime(df['DATE'], format='%d-%m-%y', errors='coerce')
        df['DATE'] = df['DATE'].fillna(pd.to_datetime(self.db.freight_data['DATE'], format='%d-%m-%Y', errors='coerce'))

        from_d = self.from_date.date().toPyDate()
        to_d = self.to_date.date().toPyDate()
        df = df[(df['DATE'] >= pd.to_datetime(from_d)) & (df['DATE'] <= pd.to_datetime(to_d))]

        selected_driver = self.driver_combo.currentText()
        if selected_driver!= "ALL DRIVERS":
            df = df[df['DRIVER NAME'] == selected_driver]

        df['QTY/BAGS'] = pd.to_numeric(df['QTY/BAGS'], errors='coerce').fillna(0)
        df['PER BAG COOLIE'] = pd.to_numeric(df['PER BAG COOLIE'], errors='coerce').fillna(0)
        df['PER BAG FREIGHT'] = pd.to_numeric(df['PER BAG FREIGHT'], errors='coerce').fillna(0)
        df['COOLIE'] = df['QTY/BAGS'] * df['PER BAG COOLIE']
        df['FREIGHT'] = df['QTY/BAGS'] * df['PER BAG FREIGHT']
        return df

    def generate_report(self):
        df = self.get_filtered_data()
        if df.empty:
            QMessageBox.warning(self, "No Data", "Selected date range la data illa")
            return

        summary = df.groupby('DRIVER NAME').agg(
            BILLS=('BILL NO', 'count'),
            TOTAL_QTY=('QTY/BAGS', 'sum'),
            TOTAL_COOLIE=('COOLIE', 'sum'),
            TOTAL_FREIGHT=('FREIGHT', 'sum')
        ).reset_index()
        summary['TOTAL'] = summary['TOTAL_COOLIE'] + summary['TOTAL_FREIGHT']

        self.table.setRowCount(summary.shape[0])
        self.table.setColumnCount(summary.shape[1])
        self.table.setHorizontalHeaderLabels(summary.columns)
        for i in range(summary.shape[0]):
            for j, col in enumerate(summary.columns):
                val = summary.iloc[i,j]
                text = f"{val:.2f}" if isinstance(val, (int, float)) else str(val)
                self.table.setItem(i, j, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def export_excel(self):
        df = self.get_filtered_data()
        if df.empty: return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel", "Freight_Report.xlsx", "Excel Files (*.xlsx)")
        if file_name:
            df.to_excel(file_name, index=False)
            QMessageBox.information(self, "Success", f"Saved to {file_name}")

    def print_summary_pdf(self):
        # Office use ku simple table
        pass # idhu same ah irukum. Venumna sollu full ah tharen

    def print_driver_bill_pdf(self):
        driver = self.driver_combo.currentText()
        if driver == "ALL DRIVERS":
            QMessageBox.warning(self, "Select Driver", "Please select one driver for Bill Receipt")
            return

        df = self.get_filtered_data()
        if df.empty:
            QMessageBox.warning(self, "No Data", "Selected driver ku andha date la data illa")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Driver Bill", f"{driver}_Receipt.pdf", "PDF Files (*.pdf)")
        if not file_name: return

        c = canvas.Canvas(file_name, pagesize=A4)
        width, height = A4

        # ===== HEADER BOX =====
        c.setStrokeColor(colors.HexColor('#0056b3'))
        c.setLineWidth(2)
        c.rect(15*mm, 250*mm, 180*mm, 35*mm, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.HexColor('#0056b3'))
        c.drawCentredString(105*mm, 275*mm, "PTC SHOP")
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        c.drawCentredString(105*mm, 268*mm, "Freight & Coolie Settlement Receipt")
        c.drawCentredString(105*mm, 262*mm, "Chennai, Tamil Nadu")

        # ===== DRIVER INFO BOX =====
        driver_info = self.db.driver_master[self.db.driver_master['DRIVER NAME'] == driver]
        if not driver_info.empty: driver_info = driver_info.iloc[0]
        else: driver_info = {}

        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, 245*mm, f"Driver Name : {driver}")
        c.drawString(20*mm, 240*mm, f"Truck No : {driver_info.get('TRUCK NO','')}")
        c.drawString(20*mm, 235*mm, f"Phone : {driver_info.get('PHONE','')}")
        c.drawString(100*mm, 245*mm, f"Vehicle Type : {driver_info.get('VEHICLE TYPE','')}")
        c.drawString(100*mm, 240*mm, f"Period : {self.from_date.date().toString('dd-MM-yy')} to {self.to_date.date().toString('dd-MM-yy')}")
        c.line(20*mm, 232*mm, 190*mm, 232*mm)

        # ===== TABLE =====
        data = [['S.No', 'Date', 'Bill No', 'Customer', 'Qty', 'Coolie', 'Freight', 'Total']]
        total_coolie = 0
        total_freight = 0
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            row_total = row['COOLIE'] + row['FREIGHT']
            data.append([
                idx, row['DATE'].strftime('%d-%m-%y'), row['BILL NO'], row['CUSTOMER NAME'][:15],
                f"{row['QTY/BAGS']:.0f}", f"₹{row['COOLIE']:.2f}", f"₹{row['FREIGHT']:.2f}", f"₹{row_total:.2f}"
            ])
            total_coolie += row['COOLIE']
            total_freight += row['FREIGHT']

        grand_total = total_coolie + total_freight

        t = Table(data, colWidths=[10*mm, 20*mm, 20*mm, 40*mm, 15*mm, 20*mm, 20*mm, 20*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0056b3')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        t.wrapOn(c, 20*mm, 200*mm)
        t.drawOn(c, 20*mm, 120*mm)

        # ===== TOTAL BOX =====
        c.setFillColor(colors.HexColor('#fff3cd'))
        c.rect(120*mm, 100*mm, 70*mm, 18*mm, stroke=1, fill=1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(125*mm, 112*mm, f"Total Coolie : ₹{total_coolie:.2f}")
        c.drawString(125*mm, 105*mm, f"Total Freight : ₹{total_freight:.2f}")

        c.setFillColor(colors.HexColor('#0056b3'))
        c.rect(120*mm, 90*mm, 70*mm, 10*mm, stroke=1, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(130*mm, 93*mm, f"GRAND TOTAL: ₹{grand_total:.2f}")

        # ===== FOOTER =====
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, 40*mm, "Driver Signature: _________________")
        c.drawString(120*mm, 40*mm, "For PTC SHOP: _________________")
        c.drawCentredString(105*mm, 20*mm, "Thank You! Drive Safe")

        c.save()
        QMessageBox.information(self, "Success", f"{driver} Bill Receipt Created")