import requests
import smtplib
from bs4 import BeautifulSoup
import sqlite3
import json
import re
import time
from datetime import datetime
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AmazonPriceTracker:
    def __init__(self, db_path='product_database.db'):
        self.db_path = db_path
        self.setup_database()
        self.load_email_config()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
    def setup_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create products table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            url TEXT UNIQUE,
            target_price REAL
        )
        ''')
        
        # Create price history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            price REAL,
            timestamp TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_email_config(self, config_path='email_config.json'):
        """Load email configuration for notifications"""
        try:
            with open(config_path, 'r') as f:
                self.email_config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {config_path} not found. Email notifications will not work.")
            self.email_config = None
    
    def add_product(self, url, target_price):
        """Add a product to track"""
        # First fetch the product name from Amazon
        product_name = self.fetch_product_name(url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO products (name, url, target_price) VALUES (?, ?, ?)",
                (product_name, url, target_price)
            )
            conn.commit()
            print(f"Added product: {product_name}")
        except sqlite3.IntegrityError:
            # Update existing product
            cursor.execute(
                "UPDATE products SET name=?, target_price=? WHERE url=?",
                (product_name, target_price, url)
            )
            conn.commit()
            print(f"Updated product: {product_name}")
        
        conn.close()
        return product_name
    
    def fetch_product_name(self, url):
        """Fetch product name from Amazon product page"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to get product title
            product_title = soup.find("span", {"id": "productTitle"})
            if product_title:
                return product_title.text.strip()
            return "Unknown Product"
        except Exception as e:
            print(f"Error fetching product name: {e}")
            return "Unknown Product"
    
    def fetch_current_price(self, url):
        """Fetch current price from Amazon product page"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for price elements - Amazon uses different structures
            price_whole = soup.find("span", {"class": "a-price-whole"})
            price_fraction = soup.find("span", {"class": "a-price-fraction"})
            
            if price_whole and price_fraction:
                price = float(f"{price_whole.text.replace(',', '')}{price_fraction.text}")
                return price
            
            # Alternative way to find price
            price_elem = soup.find("span", {"class": "a-offscreen"})
            if price_elem:
                price_text = price_elem.text.strip()
                price = float(re.sub(r'[^\d.]', '', price_text))
                return price
                
            return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def track_all_products(self):
        """Track prices for all products in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, url, target_price FROM products")
        products = cursor.fetchall()
        
        print(f"Tracking {len(products)} products...\n")
        
        for product_id, name, url, target_price in products:
            current_price = self.fetch_current_price(url)
            
            if current_price:
                # Save price history
                cursor.execute(
                    "INSERT INTO price_history (product_id, price, timestamp) VALUES (?, ?, ?)",
                    (product_id, current_price, datetime.now().isoformat())
                )
                
                # Print status
                print(f"PRODUCT: {name}")
                print(f"CURRENT PRICE: ${current_price:.2f}")
                print(f"TARGET PRICE: ${target_price:.2f}")
                
                # Check if price dropped below target
                if current_price <= target_price:
                    savings = target_price - current_price
                    print(f"STATUS: ✅ PRICE DROP ALERT! Save ${savings:.2f}")
                    self.send_price_alert(name, url, current_price, target_price)
                else:
                    difference = current_price - target_price
                    print(f"STATUS: Waiting for price drop (-${difference:.2f})")
                
                print("PRICE HISTORY: View Chart")
                print()
            else:
                print(f"Failed to fetch price for {name}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        conn.commit()
        conn.close()
    
    def send_price_alert(self, product_name, url, current_price, target_price):
        """Send email notification for price drop"""
        if not self.email_config:
            print("Email configuration not available. Skipping notification.")
            return
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = f"Price Drop Alert: {product_name}"
            
            # Email body
            body = f"""
            <html>
            <body>
                <h2>Price Drop Alert!</h2>
                <p>Good news! A product on your Amazon tracking list has dropped below your target price.</p>
                
                <h3>{product_name}</h3>
                <p>Current Price: <strong>${current_price:.2f}</strong></p>
                <p>Your Target Price: ${target_price:.2f}</p>
                <p>Savings: ${target_price - current_price:.2f}</p>
                
                <p><a href="{url}">View on Amazon</a></p>
                
                <p>This is an automated message from your Amazon Price Tracker.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"NOTIFICATION: Email sent to {self.email_config['to_email']}")
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    def generate_price_history_chart(self, product_id, output_file=None):
        """Generate price history chart for a product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get product name
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product_name = cursor.fetchone()[0]
        
        # Get price history
        cursor.execute(
            "SELECT price, timestamp FROM price_history WHERE product_id = ? ORDER BY timestamp",
            (product_id,)
        )
        history = cursor.fetchall()
        
        if not history:
            print("No price history available")
            return
            
        prices = [h[0] for h in history]
        dates = [datetime.fromisoformat(h[1]) for h in history]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, prices, marker='o')
        plt.title(f"Price History: {product_name}")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.grid(True)
        
        if output_file:
            plt.savefig(output_file)
            print(f"Chart saved to {output_file}")
        else:
            plt.show()
            
        conn.close()

def main():
    tracker = AmazonPriceTracker()
    tracker.track_all_products()

if __name__ == "__main__":
    main()
