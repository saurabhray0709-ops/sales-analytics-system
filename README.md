# Masai Sales Analytics System

A Python-based data processing system designed to clean and analyze messy e-commerce sales records.

## 🛠 Features
- **Data Cleaning**: Automatically filters invalid transactions and fixes formatting errors.
- **Modular Structure**: Logic is separated into `utils` for better maintainability.
- **Automated Reporting**: Generates a clean CSV output for business analysis.

## 📋 Data Cleaning Criteria Applied
As per the assignment requirements, the following rules are implemented in `utils/data_processor.py`:
- **Removed**: Records with missing `CustomerID` or `Region`.
- **Removed**: Transactions not starting with the letter 'T' (e.g., X-series IDs).
- **Removed**: Records where `Quantity` or `UnitPrice` is 0 or negative.
- **Fixed**: Removed commas from `ProductName` (e.g., "Mouse, Wireless" -> "Mouse Wireless").
- **Fixed**: Removed commas from `UnitPrice` to allow mathematical calculations (e.g., "1,916" -> 1916.0).

## 🚀 How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python main.py
   