import os

def read_sales_data(filename):
    """
    Reads sales data while handling encoding issues and missing files.
   
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    if not os.path.exists(filename):
        print(f"Error: The file {filename} was not found.")
        return []

    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                # Skip header and remove empty lines
                lines = [line.strip() for line in f.readlines()[1:] if line.strip()]
                return lines
        except (UnicodeDecodeError, Exception):
            continue
            
    return []

def parse_transactions(raw_lines):
    """
    Splits pipe-delimited strings into a list of dictionaries.
   
    """
    transactions = []
    for line in raw_lines:
        # Split by pipe delimiter '|'
        parts = line.split('|')
        
        # Skip rows with incorrect number of fields (expected 8)
        if len(parts) != 8:
            continue
            
        try:
            # Clean commas from numeric strings
            qty_str = parts[4].replace(',', '')
            price_str = parts[5].replace(',', '')
            
            txn = {
                'TransactionID': parts[0],
                'Date': parts[1],
                'ProductID': parts[2],
                'ProductName': parts[3].replace(',', ' '), # Handle commas in name
                'Quantity': int(qty_str),   # Convert to int
                'UnitPrice': float(price_str), # Convert to float
                'CustomerID': parts[6],
                'Region': parts[7]
            }
            transactions.append(txn)
        except ValueError:
            continue
            
    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates business rules and applies user-defined filters.
   
    """
    valid_list = []
    invalid_count = 0
    filtered_by_region = 0
    filtered_by_amount = 0
    
    for txn in transactions:
        # 1. Validation Rules
        is_valid = (
            txn['TransactionID'].startswith('T') and
            txn['ProductID'].startswith('P') and
            txn['CustomerID'].startswith('C') and
            txn['Quantity'] > 0 and
            txn['UnitPrice'] > 0
        )
        
        if not is_valid:
            invalid_count += 1
            continue
            
        # 2. Optional Filters
        if region and txn['Region'] != region:
            filtered_by_region += 1
            continue
            
        total_amt = txn['Quantity'] * txn['UnitPrice']
        if (min_amount and total_amt < min_amount) or (max_amount and total_amt > max_amount):
            filtered_by_amount += 1
            continue
            
        valid_list.append(txn)

    summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid_list)
    }
    
    return valid_list, invalid_count, summary