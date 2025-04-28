import argparse
import sqlite3
import sys
from price_tracker import AmazonPriceTracker

def main():
    parser = argparse.ArgumentParser(description='Add a product to track')
    parser.add_argument('--url', type=str, required=True, help='Amazon product URL')
    parser.add_argument('--target-price', type=float, required=True, help='Target price for alerts')
    args = parser.parse_args()
    
    # Validate URL
    if "amazon.com" not in args.url and "amazon." not in args.url:
        print("Error: Please provide a valid Amazon product URL")
        sys.exit(1)
    
    # Validate price
    if args.target_price <= 0:
        print("Error: Target price must be greater than 0")
        sys.exit(1)
    
    try:
        # Initialize tracker
        tracker = AmazonPriceTracker()
        
        # Add product to database
        product_name = tracker.add_product(args.url, args.target_price)
        
        print(f"Successfully added product: {product_name}")
        print(f"Target price set to: ${args.target_price:.2f}")
        print("Run 'python track_prices.py' to check current prices")
        
    except Exception as e:
        print(f"Error adding product: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
