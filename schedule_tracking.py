import argparse
import time
import schedule
import sys
import os
from datetime import datetime
from price_tracker import AmazonPriceTracker

def track_prices():
    print(f"\n===== Price Tracking Job: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    tracker = AmazonPriceTracker()
    tracker.track_all_products()
    print("=== Tracking complete ===\n")

def main():
    parser = argparse.ArgumentParser(description='Schedule regular price tracking')
    parser.add_argument('--interval', type=float, default=6, 
                       help='Time interval between checks in hours')
    args = parser.parse_args()
    
    if args.interval < 1:
        print("Warning: Checking too frequently may result in your IP being blocked")
        response = input("Do you want to continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Schedule the tracking job
    schedule.every(args.interval).hours.do(track_prices)
    
    print(f"Price tracker scheduled to run every {args.interval} hours")
    print("Press Ctrl+C to stop")
    
    # Run once immediately
    track_prices()
    
    try:
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute
    except KeyboardInterrupt:
        print("\nPrice tracker stopped")

if __name__ == "__main__":
    main()
