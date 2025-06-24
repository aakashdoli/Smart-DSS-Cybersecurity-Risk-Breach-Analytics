import pandas as pd

def load_vendor_data(filepath="data/vendors.csv"):
    return pd.read_csv(filepath)
