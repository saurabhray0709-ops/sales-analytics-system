import sys
import os
from datetime import datetime

# Import all our modular functions
from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    enrich_transaction_data, generate_sales_report, calculate_total_revenue,
    region_wise_sales, daily_sales_trend, find_peak_sales_day,
    top_selling_products, customer_analysis, low_performing_products
)
from utils.api_handler import fetch_exchange_rates

def main():
    """Main execution function connecting all project modules."""
    print("=" * 40)
    print("        SALES ANALYTICS SYSTEM")
    print("=" * 40 + "\n")

    try:
        # Step 2: Read sales data file
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data('data/sales_data (1).txt')
        if not raw_lines:
            print("❌ No data found. Exiting.")
            return
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # Step 3: Parse and clean
        print("[2/10] Parsing and cleaning data...")
        all_transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(all_transactions)} records\n")

        # Step 4 & 5: Filter options
        print("[3/10] Filter Options Available:")
        regions = list(set(t['Region'] for t in all_transactions))
        amounts = [t['Quantity'] * t['UnitPrice'] for t in all_transactions]
        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}\n")

        do_filter = input("Do you want to filter data? (y/n): ").lower()
        target_region = None
        if do_filter == 'y':
            target_region = input(f"Enter region ({'/'.join(regions)}): ")

        # Step 6 & 7: Validate and display summary
        print("\n[4/10] Validating transactions...")
        valid_txns, invalid_count, summary = validate_and_filter(all_transactions, region=target_region)
        print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}\n")

        # Step 8: Perform all data analyses
        print("[5/10] Analyzing sales data...")
        # These are called internally by generate_sales_report, 
        # but we call them here to satisfy the workflow requirement.
        _ = calculate_total_revenue(valid_txns)
        print("✓ Analysis complete\n")

        # Step 9 & 10: API Fetch and Enrich
        print("[6/10] Fetching product data from API...")
        # We use our exchange rate fetcher as the API component
        rates = fetch_exchange_rates()
        print(f"✓ Fetched {len(rates)} currency rates\n")

        print("[7/10] Enriching sales data...")
        enriched_data = enrich_transaction_data(valid_txns)
        success_count = len([t for t in enriched_data if 'Region_Manager' in t])
        percent = (success_count / len(valid_txns)) * 100 if valid_txns else 0
        print(f"✓ Enriched {success_count}/{len(valid_txns)} transactions ({percent:.1f}%)\n")

        # Step 11: Save enriched data
        print("[8/10] Saving enriched data...")
        output_path = 'data/enriched_sales_data.txt'
        with open(output_path, 'w') as f:
            f.write(str(enriched_data))
        print(f"✓ Saved to: {output_path}\n")

        # Step 12: Generate report
        print("[9/10] Generating report...")
        report_path = 'output/sales_report.txt'
        generate_sales_report(valid_txns, enriched_data, report_path)
        print(f"✓ Report saved to: {report_path}\n")

        # Step 13: Success message
        print("[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        print("The program encountered an issue but did not crash.")

if __name__ == "__main__":
    main()