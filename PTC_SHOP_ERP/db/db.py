import pandas as pd
import os

class FreightDB:
    def __init__(self):
        # Project root la iruka data folder ah edukum
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.freight_file = os.path.join(self.data_dir, "All_Freight.xlsx")
        self.driver_file = os.path.join(self.data_dir, "All_Drivers.xlsx")

        self.freight_cols = ['ID','Date','Bill No','Driver Name','Truck No','From','To','Qty/Bags','Per Bag Coolie','Coolie','Per Bag Freight','Freight','Amount','Status']
        self.driver_cols = ['ID','Driver Name','Mobile','License No','Address']

        self.freight_df = self._load_df(self.freight_file, self.freight_cols)
        self.driver_df = self._load_df(self.driver_file, self.driver_cols)
        self.file_path = self.freight_file

    def _load_df(self, file_path, columns):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            if 'ID' not in df.columns:
                df.insert(0, 'ID', range(1, len(df)+1))
            print(f"Loaded: {os.path.basename(file_path)} - Rows: {len(df)}")
            return df
        except Exception as e:
            print(f"Load Info: Creating new file {os.path.basename(file_path)}")
            return pd.DataFrame(columns=columns)

    def load_excel(self, file_type="freight"):
        self.file_path = self.freight_file if file_type == "freight" else self.driver_file
        df = self.freight_df if file_type == "freight" else self.driver_df
        return df.to_dict('records')

    def get_df(self, file_type):
        return self.freight_df if file_type == "freight" else self.driver_df

    def save_excel(self):
        self.freight_df.to_excel(self.freight_file, index=False, engine='openpyxl')
        self.driver_df.to_excel(self.driver_file, index=False, engine='openpyxl')

    def add_data(self, data_dict, file_type="freight"):
        df = self.get_df(file_type)
        cols = self.freight_cols if file_type == "freight" else self.driver_cols
        new_id = 1 if df.empty else int(df['ID'].max() + 1)
        data_dict['ID'] = new_id
        new_row = pd.DataFrame([data_dict], columns=cols)
        if file_type == "freight":
            self.freight_df = pd.concat([df, new_row], ignore_index=True)
        else:
            self.driver_df = pd.concat([df, new_row], ignore_index=True)
        self.save_excel()

    def update_cell(self, row, col, value, file_type="freight"):
        df = self.get_df(file_type)
        col_name = df.columns[col]
        dtype = df[col_name].dtype
        try:
            if pd.api.types.is_numeric_dtype(dtype):
                cast_value = 0 if value == "" else pd.to_numeric(value)
            else:
                cast_value = str(value)
        except:
            cast_value = value
        df.iat[row, col] = cast_value
        self.save_excel()

    def get_columns(self, file_type="freight"):
        df = self.get_df(file_type)
        return df.columns.tolist()

    def get_driver_names(self):
        if self.driver_df.empty: return []
        return self.driver_df['Driver Name'].dropna().unique().tolist()

db = FreightDB()