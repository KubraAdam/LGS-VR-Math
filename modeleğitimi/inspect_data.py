import pandas as pd
import os

file_path = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\-Güncel.xlsx"

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        print("\nFirst 3 rows:")
        print(df.head(3))
        print("\nUnique values in potentially relevant columns:")

        for col in df.columns:
             if df[col].dtype == 'object' or df[col].nunique() < 20:
                 print(f"\nColumn: {col}")
                 print(df[col].unique()[:10]) 
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print(f"File not found at {file_path}")
