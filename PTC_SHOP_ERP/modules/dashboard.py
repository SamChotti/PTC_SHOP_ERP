from PySide6.QtWidgets import *
from PySide6.QtCore import *


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("DASHBOARD OVERVIEW")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(title)

        cards = QHBoxLayout()
        cards.addWidget(self.create_card("Total Sales", "₹ 0.00", "#10B981"))
        cards.addWidget(self.create_card("Total Cooli", "₹ 812.50", "#F59E0B"))
        cards.addWidget(self.create_card("Total Freight", "₹ 4125.00", "#3B82F6"))
        layout.addLayout(cards)
        layout.addStretch()

    def create_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet("background-color: #1E293B; border-radius: 10px; padding: 15px;")
        layout = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #94A3B8; font-size: 12px;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(t)
        layout.addWidget(v)
        return card