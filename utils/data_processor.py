import pandas as pd

def clean_sales_data(df):
    # Count total records at the start (approx. 80)
    total_parsed = len(df)
    
    # 1. REMOVE INVALID RECORDS
    # Remove rows if CustomerID or Region is missing (e.g., T072 or T071)
    df = df.dropna(subset=['CustomerID', 'Region'])
    
    # Remove rows if TransactionID does not start with 'T' (e.g., X2, X611)
    df = df[df['TransactionID'].str.startswith('T', na=False)]
    
    # 2. CLEAN & KEEP VALID RECORDS
    # Remove commas from ProductNames (e.g., "Laptop,Premium" -> "Laptop Premium")
    df['ProductName'] = df['ProductName'].str.replace(',', ' ')
    
    # Remove commas from UnitPrice and convert to number (e.g., "1,916" -> 1916)
    df['UnitPrice'] = df['UnitPrice'].astype(str).str.replace(',', '').astype(float)
    
    # 3. MATH FILTER
    # Remove records where Quantity or Price is 0 or less (e.g., T075, T076)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # 4. REQUIRED VALIDATION OUTPUT
    valid_count = len(df)
    removed_count = total_parsed - valid_count
    
    print(f"Total records parsed: {total_parsed}")
    print(f"Invalid records removed: {removed_count}")
    print(f"Valid records after cleaning: {valid_count}")
    
    return df