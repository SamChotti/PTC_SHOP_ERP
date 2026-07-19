from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
import pandas as pd


class Dashboard(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)

        title = QLabel("📊 DASHBOARD OVERVIEW")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0056b3; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Summary Cards
        summary_layout = QHBoxLayout()
        self.sales_card = self.create_card("Total Sales", "0.00", "#28a745")
        self.coolie_card = self.create_card("Total Coolie", "0.00", "#ffc107")
        self.freight_card = self.create_card("Total Freight", "0.00", "#17a2b8")
        summary_layout.addWidget(self.sales_card)
        summary_layout.addWidget(self.coolie_card)
        summary_layout.addWidget(self.freight_card)
        layout.addLayout(summary_layout)

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        self.update_dashboard()

    def create_card(self, title, value, color):
        card = QGroupBox()
        card.setStyleSheet(f"QGroupBox {{ border: 2px solid {color}; border-radius: 10px; }}")
        layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_value = QLabel(f"₹ {value}")
        lbl_value.setObjectName("value")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        card.setLayout(layout)
        card.value_label = lbl_value
        return card

    def update_dashboard(self):
        sales_total = pd.to_numeric(self.db.sales_data['TOTAL'], errors='coerce').sum()
        self.sales_card.value_label.setText(f"₹ {sales_total:.2f}")

        freight_df = self.db.freight_data
        if not freight_df.empty:
            freight_df['COOLIE'] = pd.to_numeric(freight_df['QTY/BAGS'], errors='coerce') * pd.to_numeric(
                freight_df['PER BAG COOLIE'], errors='coerce')
            freight_df['FREIGHT'] = pd.to_numeric(freight_df['QTY/BAGS'], errors='coerce') * pd.to_numeric(
                freight_df['PER BAG FREIGHT'], errors='coerce')
            coolie_total = freight_df['COOLIE'].sum()
            freight_total = freight_df['FREIGHT'].sum()
        else:
            coolie_total = 0
            freight_total = 0

        self.coolie_card.value_label.setText(f"₹ {coolie_total:.2f}")
        self.freight_card.value_label.setText(f"₹ {freight_total:.2f}")

        chart = QChart()
        chart.setTitle("Sales vs Expenses")
        series = QBarSeries()
        sales_set = QBarSet("Sales")
        sales_set.append(sales_total)
        expense_set = QBarSet("Expenses")
        expense_set.append(coolie_total + freight_total)
        series.append(sales_set)
        series.append(expense_set)
        chart.addSeries(series)
        chart.createDefaultAxes()
        self.chart_view.setChart(chart)