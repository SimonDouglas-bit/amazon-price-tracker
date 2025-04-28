from price_tracker import AmazonPriceTracker

def main():
    print("Amazon Price Tracker - One-time Check")
    print("=====================================")
    
    tracker = AmazonPriceTracker()
    tracker.track_all_products()
    
    print("\nCompleted price check")
    print("To set up regular price checking, run: python schedule_tracking.py")

if __name__ == "__main__":
    main()
