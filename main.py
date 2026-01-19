import pandas as pd
import os
from utils.data_processor import clean_sales_data

def main():
    # 1. Path to your raw data file
    input_file = "data/sales_data (1).txt"
    
    try:
        print("--- Starting Sales Analytics System ---")
        
        # 2. Load the messy data
        # We use sep='|' because your file uses pipes instead of commas
        raw_df = pd.read_csv(input_file, sep='|', encoding='utf-8-sig')
        
        # 3. Call the cleaning function from your utils folder
        cleaned_df = clean_sales_data(raw_df)
        
        # 4. Create output folder if it doesn't exist
        if not os.path.exists('output'):
            os.makedirs('output')
            
        # 5. Save the final report
        output_path = "output/cleaned_sales_report.csv"
        cleaned_df.to_csv(output_path, index=False)
        
        print(f"--- Process Complete! Report saved to {output_path} ---")

    except FileNotFoundError:
        print(f"Error: Could not find the file at {input_file}. Make sure it is inside the 'data' folder.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()