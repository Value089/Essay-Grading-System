"""
Data Loading Script - Finds and prepares the Essay Scoring Dataset
This script locates the training data and converts it to a usable format
"""

import os
import pandas as pd
import shutil

def find_excel_files(directory):
    """Find all Excel files in directory and subdirectories"""
    excel_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.xlsx', '.xls')):
                full_path = os.path.join(root, file)
                excel_files.append(full_path)
    return excel_files

def inspect_excel_file(file_path):
    """Inspect an Excel file and show its structure"""
    print(f"\n{'='*70}")
    print(f"File: {file_path}")
    print(f"{'='*70}")
    
    try:
        # Try reading with openpyxl
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        print(f"✓ Loaded with openpyxl")
    except:
        try:
            # Try reading with xlrd
            xl = pd.ExcelFile(file_path, engine='xlrd')
            print(f"✓ Loaded with xlrd")
        except Exception as e:
            print(f"✗ Failed to load: {e}")
            return None
    
    print(f"\nSheets: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet, nrows=3)
            print(f"\n--- Sheet: {sheet} ---")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample data:")
            print(df.head())
        except Exception as e:
            print(f"Error reading sheet {sheet}: {e}")
    
    return xl

def find_training_data():
    """Find the main training data file"""
    print("Searching for training data files...")
    
    # Search in data directory
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"✗ Data directory not found: {data_dir}")
        return None
    
    # Find all Excel files
    excel_files = find_excel_files(data_dir)
    
    if not excel_files:
        print("✗ No Excel files found in data directory")
        return None
    
    print(f"\n✓ Found {len(excel_files)} Excel file(s):")
    for i, file in enumerate(excel_files, 1):
        print(f"  {i}. {file}")
    
    # Inspect each file
    for file_path in excel_files:
        inspect_excel_file(file_path)
    
    return excel_files

def convert_to_single_file(excel_file):
    """Convert multi-sheet Excel to single TSV file"""
    print(f"\n\nConverting {excel_file} to single TSV file...")
    
    try:
        xl = pd.ExcelFile(excel_file, engine='openpyxl')
    except:
        xl = pd.ExcelFile(excel_file, engine='xlrd')
    
    all_data = []
    
    for sheet_name in xl.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Add essay_set column if not present
        if 'essay_set' not in df.columns:
            # Try to extract essay set number from sheet name
            import re
            match = re.search(r'\d+', sheet_name)
            if match:
                essay_set_num = int(match.group())
                df['essay_set'] = essay_set_num
                print(f"  Added essay_set column: {essay_set_num}")
        
        all_data.append(df)
        print(f"  Loaded {len(df)} essays")
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save as TSV
    output_file = 'data/training_set_rel3.tsv'
    combined_df.to_csv(output_file, sep='\t', index=False)
    print(f"\n✓ Saved combined data to: {output_file}")
    print(f"  Total essays: {len(combined_df)}")
    print(f"  Columns: {combined_df.columns.tolist()}")
    
    return output_file

def main():
    print("="*70)
    print("ESSAY SCORING DATASET - DATA LOADER")
    print("="*70)
    
    # Find all Excel files
    excel_files = find_training_data()
    
    if not excel_files:
        print("\n✗ No training data found!")
        print("\nExpected file structure:")
        print("  data/")
        print("    ├── Essay_Set_Descriptions/")
        print("    │   └── [Excel file with training data]")
        print("    └── Training_Materials/")
        return
    
    # Ask user which file to use
    print("\n" + "="*70)
    print("Select the file that contains the training essays:")
    for i, file in enumerate(excel_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
    
    choice = input("\nEnter file number (or press Enter for file 1): ").strip()
    
    if choice == '':
        choice = 1
    else:
        choice = int(choice)
    
    selected_file = excel_files[choice - 1]
    print(f"\n✓ Selected: {selected_file}")
    
    # Convert to TSV
    output_file = convert_to_single_file(selected_file)
    
    print("\n" + "="*70)
    print("DATA PREPARATION COMPLETE!")
    print("="*70)
    print(f"\n✓ Training data is ready at: {output_file}")
    print("\nYou can now run: python train_models.py")

if __name__ == "__main__":
    main()