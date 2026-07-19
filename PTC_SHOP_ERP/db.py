import pandas as pd
import os
from styles import FREIGHT_COLS, SALES_COLS, DRIVER_MASTER_COLS

class Database:
    def __init__(self):
        self.freight_data = pd.DataFrame(columns=FREIGHT_COLS) # 6 file illa, 1 file mattum
        self.sales_data = pd.DataFrame(columns=SALES_COLS)
        self.driver_master = pd.DataFrame(columns=DRIVER_MASTER_COLS)
        self.load_all()

    def load_all(self):
        if os.path.exists("Sales.xlsx"):
            self.sales_data = pd.read_excel("Sales.xlsx").fillna("")
        if os.path.exists("Driver_Master.xlsx"):
            self.driver_master = pd.read_excel("Driver_Master.xlsx").fillna("")
        if os.path.exists("All_Freight.xlsx"): # Ellam ingathan
            self.freight_data = pd.read_excel("All_Freight.xlsx").fillna("")

    def save_sales(self):
        self.sales_data.to_excel("Sales.xlsx", index=False)

    def save_freight(self):
        self.freight_data.to_excel("All_Freight.xlsx", index=False) # Ellam orae file

    def save_driver_master(self):
        self.driver_master.to_excel("Driver_Master.xlsx", index=False)