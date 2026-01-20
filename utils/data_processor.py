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

def calculate_total_revenue(transactions):
    """Calculates total revenue from all transactions"""
    return sum(t['Quantity'] * t['UnitPrice'] for t in transactions)

def region_wise_sales(transactions):
    """Analyzes sales by region including percentages"""
    total_rev = calculate_total_revenue(transactions)
    region_stats = {}
    
    for t in transactions:
        reg = t['Region']
        rev = t['Quantity'] * t['UnitPrice']
        if reg not in region_stats:
            region_stats[reg] = {'total_sales': 0.0, 'transaction_count': 0}
        region_stats[reg]['total_sales'] += rev
        region_stats[reg]['transaction_count'] += 1
        
    for reg in region_stats:
        region_stats[reg]['percentage'] = round((region_stats[reg]['total_sales'] / total_rev) * 100, 2)
        
    # Sort by total_sales descending
    return dict(sorted(region_stats.items(), key=lambda x: x[1]['total_sales'], reverse=True))

def daily_sales_trend(transactions):
    """Groups revenue and unique customers by date"""
    daily_stats = {}
    for t in transactions:
        date = t['Date']
        if date not in daily_stats:
            daily_stats[date] = {'revenue': 0.0, 'transaction_count': 0, 'customers': set()}
        daily_stats[date]['revenue'] += t['Quantity'] * t['UnitPrice']
        daily_stats[date]['transaction_count'] += 1
        daily_stats[date]['customers'].add(t['CustomerID'])
        
    result = {}
    for date in sorted(daily_stats.keys()): # Sort chronologically
        result[date] = {
            'revenue': daily_stats[date]['revenue'],
            'transaction_count': daily_stats[date]['transaction_count'],
            'unique_customers': len(daily_stats[date]['customers'])
        }
    return result

def find_peak_sales_day(transactions):
    """Identifies the date with highest revenue"""
    trend = daily_sales_trend(transactions)
    peak_date = max(trend, key=lambda d: trend[d]['revenue'])
    return peak_date, trend[peak_date]['revenue'], trend[peak_date]['transaction_count']

def top_selling_products(transactions, n=5):
    """Returns top n products by quantity sold"""
    product_stats = {}
    for t in transactions:
        p = t['ProductName']
        if p not in product_stats:
            product_stats[p] = {'qty': 0, 'rev': 0.0}
        product_stats[p]['qty'] += t['Quantity']
        product_stats[p]['rev'] += t['Quantity'] * t['UnitPrice']
        
    sorted_products = sorted(product_stats.items(), key=lambda x: x[1]['qty'], reverse=True)
    return [(name, data['qty'], data['rev']) for name, data in sorted_products[:n]]

def low_performing_products(transactions, threshold=10):
    """Finds products with total quantity < threshold"""
    product_stats = {} # Reuse logic from top_selling
    for t in transactions:
        p = t['ProductName']
        product_stats[p] = product_stats.get(p, 0) + t['Quantity']
        
    low_p = [(p, qty, sum(t['Quantity']*t['UnitPrice'] for t in transactions if t['ProductName']==p)) 
             for p, qty in product_stats.items() if qty < threshold]
    return sorted(low_p, key=lambda x: x[1]) # Sort by Quantity ascending

def customer_analysis(transactions):
    """Analyzes customer patterns sorted by total spent"""
    cust_stats = {}
    for t in transactions:
        c = t['CustomerID']
        if c not in cust_stats:
            cust_stats[c] = {'total_spent': 0.0, 'count': 0, 'products': set()}
        cust_stats[c]['total_spent'] += t['Quantity'] * t['UnitPrice']
        cust_stats[c]['count'] += 1
        cust_stats[c]['products'].add(t['ProductName'])
        
    for c in cust_stats:
        cust_stats[c]['avg_order_value'] = round(cust_stats[c]['total_spent'] / cust_stats[c]['count'], 2)
        cust_stats[c]['products_bought'] = list(cust_stats[c]['products'])
        
    return dict(sorted(cust_stats.items(), key=lambda x: x[1]['total_spent'], reverse=True))

def enrich_transaction_data(transactions):
    """
    Enriches transactions with currency conversion and manager info.
   
    """
    from utils.api_handler import fetch_exchange_rates, fetch_region_managers
    
    rates = fetch_exchange_rates()
    inr_rate = rates.get('INR', 83.0)
    managers = fetch_region_managers()
    
    for txn in transactions:
        # Add converted price
        txn['UnitPrice_INR'] = round(txn['UnitPrice'] * inr_rate, 2)
        txn['Total_Amount_INR'] = round(txn['Quantity'] * txn['UnitPrice_INR'], 2)
        
        # Add Manager info based on Region
        txn['Region_Manager'] = managers.get(txn['Region'], "Unknown")
        
    return transactions

from datetime import datetime

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """Generates a comprehensive formatted text report"""
    
    # 1. PREPARE DATA USING OUR PREVIOUS FUNCTIONS
    total_rev = calculate_total_revenue(transactions)
    avg_order = total_rev / len(transactions) if transactions else 0
    dates = sorted([t['Date'] for t in transactions])
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"
    
    regions = region_wise_sales(transactions)
    top_prods = top_selling_products(transactions, n=5)
    top_custs = list(customer_analysis(transactions).items())[:5]
    trends = daily_sales_trend(transactions)
    peak_date, peak_rev, peak_count = find_peak_sales_day(transactions)
    low_prods = low_performing_products(transactions)

    with open(output_file, 'w', encoding='utf-8') as f:
        # 1. HEADER
        f.write("="*44 + "\n")
        f.write("         SALES ANALYTICS REPORT\n")
        f.write(f"      Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"      Records Processed: {len(transactions)}\n")
        f.write("="*44 + "\n\n")

        # 2. OVERALL SUMMARY
        f.write("OVERALL SUMMARY\n" + "-"*44 + "\n")
        f.write(f"Total Revenue:       ₹{total_rev:,.2f}\n")
        f.write(f"Total Transactions:  {len(transactions)}\n")
        f.write(f"Average Order Value: ₹{avg_order:,.2f}\n")
        f.write(f"Date Range:          {date_range}\n\n")

        # 3. REGION-WISE PERFORMANCE
        f.write("REGION-WISE PERFORMANCE\n" + "-"*44 + "\n")
        f.write(f"{'Region':<10} {'Sales':<12} {'% Total':<10} {'Txns':<5}\n")
        for reg, data in regions.items():
            f.write(f"{reg:<10} ₹{data['total_sales']:<11,.0f} {data['percentage']:<10}% {data['transaction_count']:<5}\n")
        f.write("\n")

        # 4. TOP 5 PRODUCTS
        f.write("TOP 5 PRODUCTS\n" + "-"*44 + "\n")
        f.write(f"{'Rank':<5} {'Product Name':<20} {'Qty':<5} {'Revenue':<12}\n")
        for i, (name, qty, rev) in enumerate(top_prods, 1):
            f.write(f"{i:<5} {name[:19]:<20} {qty:<5} ₹{rev:,.2f}\n")
        f.write("\n")

        # 5. TOP 5 CUSTOMERS
        f.write("TOP 5 CUSTOMERS\n" + "-"*44 + "\n")
        f.write(f"{'Rank':<5} {'Cust ID':<10} {'Spent':<15} {'Orders':<5}\n")
        for i, (cid, data) in enumerate(top_custs, 1):
            f.write(f"{i:<5} {cid:<10} ₹{data['total_spent']:<14,.2f} {data['count']:<5}\n")
        f.write("\n")

        # 6. DAILY SALES TREND
        f.write("DAILY SALES TREND\n" + "-"*44 + "\n")
        f.write(f"{'Date':<12} {'Revenue':<15} {'Txns':<8} {'Unq Cust':<8}\n")
        for date, data in list(trends.items())[:10]: # Showing first 10 days
            f.write(f"{date:<12} ₹{data['revenue']:<14,.2f} {data['transaction_count']:<8} {data['unique_customers']:<8}\n")
        f.write("\n")

        # 7. PRODUCT PERFORMANCE ANALYSIS
        f.write("PRODUCT PERFORMANCE ANALYSIS\n" + "-"*44 + "\n")
        f.write(f"Peak Sales Day: {peak_date} (₹{peak_rev:,.2f})\n")
        f.write(f"Low Performing Count: {len(low_prods)} products\n\n")

        # 8. API ENRICHMENT SUMMARY
        enriched_count = len([t for t in enriched_transactions if 'Region_Manager' in t])
        success_rate = (enriched_count / len(transactions)) * 100 if transactions else 0
        f.write("API ENRICHMENT SUMMARY\n" + "-"*44 + "\n")
        f.write(f"Total Products Enriched: {enriched_count}\n")
        f.write(f"Success Rate:            {success_rate:.2f}%\n")
        f.write("-" * 44 + "\n")

    print(f"--- Report generated successfully at {output_file} ---")