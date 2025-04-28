# Amazon Price Tracker

An automated tool that tracks Amazon product prices over time and notifies you when prices drop to your target threshold.

## 💰 Problem Solved

Online shoppers want to purchase products at the best possible price but don't have time to constantly check for price fluctuations. This tool monitors product prices automatically and sends notifications when items drop to your desired price point.

## ✨ Features

- Track unlimited Amazon products across multiple regions
- Set custom price threshold alerts for each product
- Receive email notifications when prices drop
- Historical price tracking with trend visualization
- Export price history to CSV for analysis
- Configurable scanning frequency

## 🛠️ Technologies Used

- Python 3.8+
- BeautifulSoup4 for web scraping
- SQLite for data storage
- Matplotlib for price trend visualization
- smtplib for email notifications

## 📋 Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your email settings for notifications
cp email_config.example.json email_config.json
# Edit email_config.json with your email settings

# Add products to track
python add_product.py --url "https://www.amazon.com/product-url" --target-price 29.99

# Run the tracker once
python track_prices.py

# Set up as scheduled task
python schedule_tracking.py --interval 6  # Check every 6 hours
```
## 📊 Sample Output
Tracking 3 products...

PRODUCT: Sony WH-1000XM4 Wireless Headphones
CURRENT PRICE: $248.00
TARGET PRICE: $220.00
STATUS: Waiting for price drop (-$28.00)
PRICE HISTORY: View Chart

PRODUCT: Instant Pot Duo 7-in-1  
CURRENT PRICE: $79.95  
TARGET PRICE: $89.99  
STATUS: ✅ PRICE DROP ALERT! Save $10.04  
NOTIFICATION: Email sent to user@example.com  
## 📝 License
MIT
