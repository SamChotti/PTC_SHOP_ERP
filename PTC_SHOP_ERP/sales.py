from PySide6.QtWidgets import *
from PySide6.QtCore import QDate
from styles import SALES_COLS

class SalesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(len(SALES_COLS))
        self.table.setHorizontalHeaderLabels(SALES_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.load_table()

    def add_entry(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Sales Entry")
        form = QFormLayout(dialog)
        inputs = {col: QLineEdit() for col in SALES_COLS if col not in ['TOTAL', 'BALANCE']}
        inputs['DATE'].setText(QDate.currentDate().toString("dd-MM-yy"))
        for k, v in inputs.items(): form.addRow(k, v)
        btn = QPushButton("💾 Save Sale")
        btn.clicked.connect(lambda: self.save(inputs, dialog))
        form.addWidget(btn)
        dialog.exec()

    def save(self, inputs, dialog):
        qty = float(inputs['QTY'].text() or 0)
        rate = float(inputs['RATE'].text() or 0)
        paid = float(inputs['PAID'].text() or 0)
        total = qty * rate
        new_row = {k: v.text() for k,v in inputs.items()}
        new_row['TOTAL'] = total
        new_row['BALANCE'] = total - paid
        self.db.sales_data = pd.concat([self.db.sales_data, pd.DataFrame([new_row])], ignore_index=True)
        self.db.save_sales()
        self.load_table()
        dialog.close()

    def load_table(self):
        df = self.db.sales_data
        self.table.setRowCount(df.shape[0])
        for i in range(df.shape[0]):
            for j, col in enumerate(SALES_COLS):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i][col])))