import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import io

# Config
FILE_PATH = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\-Güncel.xlsx"
OUTPUT_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\dataset_splits"
RANDOM_SEED = 42

def load_and_parse_data(file_path):
    """
    Loads Excel file where the entire content is essentially a CSV inside the first column.
    """
    print(f"Loading raw file from {file_path}...")
    # Read excel - expecting single column
    df_raw = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    
    # If the dataframe has only one column, we treat it as lines of a CSV
    if len(df_raw.columns) == 1:
        print("Detected single column format. Parsing as embedded CSV...")
        # Get the header from the column name
        header = df_raw.columns[0]
        # Get the rest of the lines
        lines = df_raw.iloc[:, 0].astype(str).tolist()
        
        # Combine header and lines
        csv_content = header + "\n" + "\n".join(lines)
        
        # Read back as CSV with more robust error handling
        try:
            df = pd.read_csv(io.StringIO(csv_content), quotechar='"', on_bad_lines='warn')
        except Exception:
            print("Standard parse failed. Trying python engine...")
            df = pd.read_csv(io.StringIO(csv_content), engine='python', on_bad_lines='warn')
    else:
        print("Detected standard format.")
        df = df_raw

    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    print(f"Columns found: {df.columns.tolist()}")
    return df

def create_model_input(row):
    """
    Formats the input string:
    [SORU] Soru metni
    [A] Seçenek A
    ...
    [GÖRSEL] Bu soru görsele bağlıdır. (if applicable)
    """
    text = f"[SORU] {row['soru_metin']}\n"
    
    # Options
    for opt in ['A', 'B', 'C', 'D', 'E']:
        col_name = f"secenek_{opt}"
        if col_name in row and pd.notna(row[col_name]):
            text += f"[{opt}] {row[col_name]}\n"
    
    # Visual tag
    if 'gorsel_bagimli' in row:
        val = str(row['gorsel_bagimli']).lower()
        if 'bagimli' in val or 'var' in val: # Adjust as needed based on data inspection
             text += "[GÖRSEL] Bu soru görsele bağlıdır.\n"
    
    return text.strip()

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    df = load_and_parse_data(FILE_PATH)
    
    # Basic cleaning
    # Target columns must exist
    required_cols = ['alt_konu', 'soru_tipi', 'soru_metin']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
        
    # Drop rows with missing targets
    print(f"Original shape: {df.shape}")
    df = df.dropna(subset=['alt_konu', 'soru_tipi'])
    print(f"Shape after dropping missing targets: {df.shape}")
    
    # Create Input Column
    print("Formatting inputs...")
    df['text_input'] = df.apply(create_model_input, axis=1)
    
    # Create Stratify Column (Combination of classes)
    df['stratify_col'] = df['alt_konu'].astype(str) + "_" + df['soru_tipi'].astype(str)
    
    # Filtering rare classes if any (just in case split fails)
    # Filter classes with fewer than 5 samples to ensure we can split into Train/Val/Test (need at least 1 in each, ideally more)
    MIN_SAMPLES = 5
    class_counts = df['stratify_col'].value_counts()
    rare_classes = class_counts[class_counts < MIN_SAMPLES].index
    if len(rare_classes) > 0:
        print(f"Warning: {len(rare_classes)} combinations have fewer than {MIN_SAMPLES} samples. They will be excluded to allow stratified splitting.")
        df = df[~df['stratify_col'].isin(rare_classes)]
    
    print(f"Shape after filtering rare classes: {df.shape}")
    
    print("Splitting data (70% Train, 15% Val, 15% Test)...")
    
    # First split: Train (70%) vs Temp (30%)
    train_df, temp_df = train_test_split(
        df, 
        test_size=0.30, 
        stratify=df['stratify_col'], 
        random_state=RANDOM_SEED
    )
    
    # Check for singletons in temp_df that would break the next split
    temp_counts = temp_df['stratify_col'].value_counts()
    temp_singletons = temp_counts[temp_counts < 2].index
    
    if len(temp_singletons) > 0:
        print(f"Warning: {len(temp_singletons)} classes have < 2 samples in temp set. Moving them to Train to prevent error.")
        # Identify rows to move
        to_move = temp_df[temp_df['stratify_col'].isin(temp_singletons)]
        
        # Move to train
        train_df = pd.concat([train_df, to_move])
        
        # Remove from temp
        temp_df = temp_df[~temp_df['stratify_col'].isin(temp_singletons)]
        
    # Second split: Val (15% -> 50% of Temp) vs Test (15% -> 50% of Temp)
    # Note: temp_df is roughly 30% of original. Splitting 50/50 gives ~15% each.
    val_df, test_df = train_test_split(
        temp_df, 
        test_size=0.50, 
        stratify=temp_df['stratify_col'], 
        random_state=RANDOM_SEED
    )
    
    print(f"Train size: {len(train_df)}")
    print(f"Val size: {len(val_df)}")
    print(f"Test size: {len(test_df)}")
    
    # Save
    train_df.to_csv(os.path.join(OUTPUT_DIR, 'train.csv'), index=False)
    val_df.to_csv(os.path.join(OUTPUT_DIR, 'val.csv'), index=False)
    test_df.to_csv(os.path.join(OUTPUT_DIR, 'test.csv'), index=False)
    
    print(f"Data saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
