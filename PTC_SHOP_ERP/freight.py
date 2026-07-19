from PySide6.QtWidgets import *
from PySide6.QtCore import QDate
import pandas as pd
from styles import FREIGHT_COLS, DRIVER_MASTER_COLS

class FreightTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_driver = ""
        layout = QVBoxLayout(self)

        # --- 1. TOP BAR: DRIVER SELECT + ADD NEW DRIVER ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Select Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.currentTextChanged.connect(self.load_driver)
        top_layout.addWidget(self.driver_combo)

        add_driver_btn = QPushButton("➕ Add New Driver / Outside Vehicle")
        add_driver_btn.clicked.connect(self.add_new_driver_dialog)
        top_layout.addWidget(add_driver_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # --- 2. DRIVER PROFILE GROUP ---
        self.driver_group = QGroupBox("Driver Profile")
        form_layout = QFormLayout()
        self.driver_inputs = {}
        for col in DRIVER_MASTER_COLS[1:]:
            if col == "VEHICLE TYPE":
                self.driver_inputs[col] = QComboBox()
                self.driver_inputs[col].addItems(["OWN DRIVER", "OUTSIDE VEHICLE"])
            else:
                self.driver_inputs[col] = QLineEdit()
            form_layout.addRow(col + ":", self.driver_inputs[col])

        save_driver_btn = QPushButton("💾 Save/Update Driver Profile")
        save_driver_btn.clicked.connect(self.save_driver_details)
        form_layout.addWidget(save_driver_btn)
        self.driver_group.setLayout(form_layout)
        layout.addWidget(self.driver_group)

        # --- 3. SUMMARY LABELS ---
        summary_layout = QHBoxLayout()
        self.coolie_lbl = QLabel("COOLIE: 0.00")
        self.freight_lbl = QLabel("FREIGHT: 0.00")
        self.total_lbl = QLabel("TOTAL: 0.00")
        for lbl in [self.coolie_lbl, self.freight_lbl, self.total_lbl]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background: #0056b3; color: white; border-radius: 8px;")
            summary_layout.addWidget(lbl)
        layout.addLayout(summary_layout)

        # --- 4. FREIGHT TABLE + ADD ENTRY BUTTON ---
        btn_layout = QHBoxLayout()
        add_entry_btn = QPushButton("➕ Add Freight Entry for Selected Driver")
        add_entry_btn.clicked.connect(self.add_entry)
        btn_layout.addWidget(add_entry_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(len(FREIGHT_COLS))
        self.table.setHorizontalHeaderLabels(FREIGHT_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.itemChanged.connect(self.recalculate)
        layout.addWidget(self.table)

        self.load_driver_list()

    def load_driver_list(self):
        self.driver_combo.blockSignals(True) # crash avoid panna
        self.driver_combo.clear()
        drivers = self.db.driver_master['DRIVER NAME'].dropna().tolist() # dropna add pannen
        self.driver_combo.addItems(drivers)
        self.driver_combo.blockSignals(False)
        if drivers:
            self.driver_combo.setCurrentText(drivers[0])
            self.load_driver(drivers[0]) # first driver ah auto load pannu

    def load_driver(self, driver_name):
        if not driver_name: return # empty na return
        self.current_driver = driver_name
        df = self.db.driver_master
        driver_row = df[df['DRIVER NAME'] == driver_name]
        if not driver_row.empty:
            for i, col in enumerate(DRIVER_MASTER_COLS[1:]):
                if col == "VEHICLE TYPE":
                    self.driver_inputs[col].setCurrentText(str(driver_row.iloc[0][col]))
                else:
                    self.driver_inputs[col].setText(str(driver_row.iloc[0][col]))
        self.load_table()
        self.recalculate()

    def add_new_driver_dialog(self):
        name, ok = QInputDialog.getText(self, "Add Driver", "Enter Driver Name:")
        if ok and name and name.strip()!= "":
            new_data = {"DRIVER NAME": name.strip()}
            for col in DRIVER_MASTER_COLS[1:]:
                new_data[col] = ""
            self.db.driver_master = pd.concat([self.db.driver_master, pd.DataFrame([new_data])], ignore_index=True)
            self.db.save_driver_master()
            self.load_driver_list() # <-- ITHU DHAN MUKKIYAM
            self.driver_combo.setCurrentText(name.strip()) # add panna udane select aaganum

    def save_driver_details(self):
        if not self.current_driver:
            QMessageBox.warning(self, "Error", "Please select a driver first")
            return
        df = self.db.driver_master
        new_data = {"DRIVER NAME": self.current_driver}
        for k, v in self.driver_inputs.items():
            new_data[k] = v.currentText() if isinstance(v, QComboBox) else v.text()

        if self.current_driver in df['DRIVER NAME'].values:
            df.loc[df['DRIVER NAME'] == self.current_driver] = list(new_data.values())
        else:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        self.db.driver_master = df
        self.db.save_driver_master()
        self.load_driver_list() # save panna aprom list update aagum
        QMessageBox.information(self, "Success", f"{self.current_driver} Profile Saved")

    def add_entry(self):
        if not self.current_driver:
            QMessageBox.warning(self, "Error", "Please select a driver first")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Freight Entry - {self.current_driver}")
        form = QFormLayout(dialog)
        inputs = {}
        inputs['DATE'] = QDateEdit()
        inputs['DATE'].setDate(QDate.currentDate())
        inputs['DATE'].setCalendarPopup(True)
        for col in FREIGHT_COLS[2:]:
            if 'PER BAG' in col: inputs[col] = QLineEdit("2.50" if "COOLIE" in col else "15.00")
            elif 'QTY' in col: inputs[col] = QLineEdit("0")
            else: inputs[col] = QLineEdit()
        for k, v in inputs.items(): form.addRow(k, v)
        btn = QPushButton("💾 Save Entry")
        btn.clicked.connect(lambda: self.save(inputs, dialog))
        form.addWidget(btn)
        dialog.exec()

    def save(self, inputs, dialog):
        qty = float(inputs['QTY/BAGS'].text() or 0)
        per_coolie = float(inputs['PER BAG COOLIE'].text() or 0)
        per_freight = float(inputs['PER BAG FREIGHT'].text() or 0)
        new_row = {k: v.text() if isinstance(v, QLineEdit) else v.date().toString("dd-MM-yy") for k,v in inputs.items()}
        new_row['DATE'] = inputs['DATE'].date().toString("dd-MM-yy")
        new_row['DRIVER NAME'] = self.current_driver
        new_row['QTY/BAGS'] = qty
        new_row['PER BAG COOLIE'] = per_coolie
        new_row['COOLIE'] = qty * per_coolie
        new_row['PER BAG FREIGHT'] = per_freight
        new_row['FREIGHT'] = qty * per_freight
        self.db.freight_data = pd.concat([self.db.freight_data, pd.DataFrame([new_row])], ignore_index=True)
        self.db.save_freight()
        self.load_table()
        self.recalculate()
        dialog.close()

    def recalculate(self):
        df = self.db.freight_data
        df_driver = df[df['DRIVER NAME'] == self.current_driver]
        if not df_driver.empty:
            df_driver['COOLIE'] = pd.to_numeric(df_driver['QTY/BAGS'], errors='coerce') * pd.to_numeric(df_driver['PER BAG COOLIE'], errors='coerce')
            df_driver['FREIGHT'] = pd.to_numeric(df_driver['QTY/BAGS'], errors='coerce') * pd.to_numeric(df_driver['PER BAG FREIGHT'], errors='coerce')

        total_coolie = df_driver['COOLIE'].sum()
        total_freight = df_driver['FREIGHT'].sum()
        self.coolie_lbl.setText(f"COOLIE: {total_coolie:.2f}")
        self.freight_lbl.setText(f"FREIGHT: {total_freight:.2f}")
        self.total_lbl.setText(f"TOTAL: {total_coolie + total_freight:.2f}")

    def load_table(self):
        df = self.db.freight_data
        df_driver = df[df['DRIVER NAME'] == self.current_driver]
        self.table.setRowCount(df_driver.shape[0])
        for i in range(df_driver.shape[0]):
            for j, col in enumerate(FREIGHT_COLS):
                self.table.setItem(i, j, QTableWidgetItem(str(df_driver.iloc[i][col])))