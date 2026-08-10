# test_data.py
import requests
import time
from datetime import datetime, timedelta
import random
import json

BASE_URL = "http://localhost:5000/api"

def safe_json_response(response):
    """Safely parse JSON response with error handling"""
    try:
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"  ⚠️ Server returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")  # Show first 200 chars
            return None
    except requests.exceptions.JSONDecodeError:
        print(f"  ⚠️ Invalid JSON response from server")
        print(f"  Response: {response.text[:200]}")
        return None

def get_existing_products():
    """Get list of existing products"""
    try:
        response = requests.get(f"{BASE_URL}/products", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def add_product(name, sku, category, stock, reorder, min_stock, max_stock, price):
    try:
        # Check if product already exists
        existing = get_existing_products()
        for p in existing:
            if p.get('sku') == sku:
                print(f"  ⏭️ Product '{name}' already exists (SKU: {sku}) - Skipping")
                return p
        
        response = requests.post(f"{BASE_URL}/products", json={
            "name": name,
            "sku": sku,
            "category": category,
            "current_stock": stock,
            "reorder_level": reorder,
            "min_stock": min_stock,
            "max_stock": max_stock,
            "price": price
        }, timeout=10)
        return safe_json_response(response)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error adding product: {e}")
        return None

def record_sale(product_id, quantity, customer_id=None):
    try:
        response = requests.post(f"{BASE_URL}/sales", json={
            "product_id": product_id,
            "quantity_sold": quantity,
            "customer_id": customer_id
        }, timeout=10)
        return safe_json_response(response)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error recording sale: {e}")
        return None

def restock_product(product_id, quantity, notes=None):
    try:
        response = requests.post(f"{BASE_URL}/restock", json={
            "product_id": product_id,
            "quantity": quantity,
            "notes": notes
        }, timeout=10)
        return safe_json_response(response)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error restocking: {e}")
        return None

def train_model(product_id):
    try:
        response = requests.post(f"{BASE_URL}/products/{product_id}/train", timeout=30)
        return safe_json_response(response)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error training model: {e}")
        return None

def predict_stock(product_id, days=7):
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}/predict?days={days}", timeout=10)
        return safe_json_response(response)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error predicting stock: {e}")
        return None

def get_products():
    try:
        response = requests.get(f"{BASE_URL}/products", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error getting products: {e}")
        return []

def get_dashboard():
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error getting dashboard: {e}")
        return {}

def get_sales_history(product_id, days=30):
    try:
        response = requests.get(f"{BASE_URL}/analytics/sales-history/{product_id}?days={days}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error getting sales history: {e}")
        return []

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def clear_all_products():
    """Delete all products from the system"""
    try:
        products = get_products()
        if not products:
            return True
        
        print(f"  🗑️ Deleting {len(products)} existing products...")
        for product in products:
            try:
                response = requests.delete(f"{BASE_URL}/products/{product['id']}", timeout=10)
                if response.status_code != 200:
                    print(f"    ⚠️ Failed to delete product {product['id']}")
            except:
                pass
        return True
    except Exception as e:
        print(f"  ❌ Error clearing products: {e}")
        return False

print("=" * 60)
print("🚀 AI Inventory Management System - Test Script")
print("=" * 60)

# Check if server is running
print("\n🔍 Checking if server is running...")
if not check_server():
    print("❌ Server is not running!")
    print("Please start the server first with: python app.py")
    print("Then run this script again.")
    exit(1)
print("✅ Server is running!")

# Ask user what to do
print("\n📋 What would you like to do?")
print("  1. Start fresh (delete all existing products and add new ones)")
print("  2. Skip existing products and add only new ones")
print("  3. Exit")
choice = input("Enter choice (1, 2, or 3): ").strip()

if choice == "3":
    print("Exiting...")
    exit(0)
elif choice == "1":
    print("\n🗑️ Clearing existing data...")
    if clear_all_products():
        print("  ✅ All products cleared!")
    else:
        print("  ⚠️ Some products could not be deleted")
elif choice == "2":
    print("\n📋 Checking for existing products...")
else:
    print("Invalid choice. Defaulting to option 2.")
    print("\n📋 Checking for existing products...")

# Step 1: Add only 4 products with unique SKUs
print("\n📦 Adding 4 products...")
products = [
    {"name": "iPhone 15 Pro Max", "sku": "PHONE-001", "category": "Electronics", "stock": 50, "reorder": 15, "min_stock": 5, "max_stock": 100, "price": 1199.99},
    {"name": "Samsung Galaxy S24 Ultra", "sku": "PHONE-002", "category": "Electronics", "stock": 40, "reorder": 12, "min_stock": 4, "max_stock": 80, "price": 1099.99},
    {"name": "Sony WH-1000XM5 Headphones", "sku": "AUDIO-001", "category": "Electronics", "stock": 60, "reorder": 18, "min_stock": 6, "max_stock": 120, "price": 349.99},
    {"name": "Nike Air Max 270", "sku": "SHOE-001", "category": "Clothing", "stock": 80, "reorder": 25, "min_stock": 10, "max_stock": 150, "price": 149.99},
]

product_ids = []
for product in products:
    result = add_product(**product)
    if result and 'id' in result:
        product_ids.append(result['id'])
        print(f"  ✅ Added: {result['name']} (ID: {result['id']})")
    elif result and 'name' in result:
        # Product already exists
        product_ids.append(result['id'])
        print(f"  ⏭️ Already exists: {result['name']} (ID: {result['id']})")
    else:
        print(f"  ❌ Failed to add: {product['name']}")

if not product_ids:
    print("❌ No products were added. Exiting.")
    exit(1)

# Get fresh list of product IDs
all_products = get_products()
product_ids = [p['id'] for p in all_products if p['id'] in product_ids]
print(f"\n📦 Total products available: {len(product_ids)}")

# Step 2: Record sales for 7 days only
print("\n💰 Recording sales over 7 days (1 week)...")
customers = ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005', 'CUST006', 'CUST007']

# Check if we already have sales data
existing_sales = 0
for product_id in product_ids:
    sales = get_sales_history(product_id, 1)
    if sales:
        existing_sales += len(sales)

if existing_sales > 0:
    print(f"  ℹ️ Found {existing_sales} existing sales records. Adding more...")

# Record sales for 7 days only
for day in range(7):
    print(f"  Day {day + 1}/7...")
    for product_id in product_ids:
        # Different sales patterns for different products
        product = next((p for p in all_products if p['id'] == product_id), None)
        if product:
            product_name = product.get('name', '')
            if 'iPhone' in product_name:
                # iPhone sales: steady with occasional spikes
                qty = random.randint(2, 5)
                if day == 0:  # First day spike
                    qty = random.randint(5, 8)
            elif 'Samsung' in product_name:
                # Samsung sales: moderate
                qty = random.randint(1, 4)
                if day == 3:  # Mid-week spike
                    qty = random.randint(4, 7)
            elif 'Sony' in product_name:
                # Headphones: consistent sales
                qty = random.randint(3, 6)
            else:  # Shoes
                qty = random.randint(4, 8)
                if day >= 5:  # Weekend spike
                    qty = random.randint(6, 10)
        else:
            qty = random.randint(2, 6)
        
        # Weekend boost for all products (Saturday and Sunday)
        if day >= 5:  # Day 5 and 6 are weekend
            qty = int(qty * 1.4)
        
        # Occasional large orders
        if random.random() > 0.9:
            qty = qty * 2
        
        customer = random.choice(customers) if random.random() > 0.3 else None
        result = record_sale(product_id, qty, customer)
        if not result:
            print(f"    ⚠️ Failed to record sale for product {product_id}")
        time.sleep(0.02)
    
    # Restock every 3 days
    if day % 3 == 0:
        for product_id in product_ids:
            restock_qty = random.randint(15, 30)
            result = restock_product(product_id, restock_qty, f"Day {day+1} restock")
            if not result:
                print(f"    ⚠️ Failed to restock product {product_id}")

print("  ✅ Sales recording complete!")

# Step 3: Train models for all products
print("\n🧠 Training ML models...")
for product_id in product_ids:
    result = train_model(product_id)
    if not result:
        print(f"  ❌ Product {product_id}: Failed to train model")
    elif 'error' in result:
        print(f"  ❌ Product {product_id}: {result['error']}")
    else:
        print(f"  ✅ Product {product_id}: {result.get('message', 'Model trained')}")
    time.sleep(0.1)  # Small delay between training

# Step 4: Make 7-day predictions for all 4 products
print("\n🔮 Making 7-day predictions for all products...")
for product_id in product_ids:
    result = predict_stock(product_id, 7)
    if not result:
        print(f"  ❌ Product {product_id}: Failed to get prediction")
    elif 'error' in result:
        print(f"  ❌ Product {product_id}: {result['error']}")
    else:
        product_name = result.get('product_name', f'Product {product_id}')
        print(f"\n  📊 {product_name}:")
        print(f"     Current Stock: {result.get('current_stock', 'N/A')}")
        print(f"     Predicted Need (7 days): {result.get('predicted_need', 'N/A')} units")
        print(f"     Daily Average: {result.get('daily_average', 'N/A')}")
        print(f"     Stock After 7 Days: {result.get('stock_after_period', 'N/A')}")
        print(f"     Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"     Confidence: {result.get('confidence', 'N/A')}")
        print(f"     Model Accuracy: {result.get('model_accuracy', 'N/A')}%")
        if result.get('daily_predictions'):
            daily_preds = result['daily_predictions']
            print(f"     Daily Predictions (Day 1-7):")
            for i, pred in enumerate(daily_preds, 1):
                print(f"       Day {i}: {pred} units")

# Step 5: Get dashboard stats
print("\n📊 Dashboard Overview:")
dashboard = get_dashboard()
if dashboard:
    print(f"  Total Products: {dashboard.get('total_products', 0)}")
    print(f"  Low Stock Items: {dashboard.get('low_stock_items', 0)}")
    print(f"  Critical Stock: {dashboard.get('critical_stock_items', 0)}")
    print(f"  Overstocked Items: {dashboard.get('overstocked_items', 0)}")
    print(f"  Total Inventory Value: ${dashboard.get('total_inventory_value', 0):.2f}")
    print(f"  ML Models Trained: {dashboard.get('ml_models_count', 0)}")
    print(f"  Today's Sales: {dashboard.get('today_sales_count', 0)}")
    print(f"  Today's Revenue: ${dashboard.get('today_revenue', 0):.2f}")
    
    print("\n🏆 Top Selling Products:")
    for product in dashboard.get('top_selling_products', []):
        print(f"  {product.get('name', 'Unknown')}: {product.get('total_sold', 0)} units")
else:
    print("  ❌ Failed to load dashboard data")

print("\n" + "=" * 60)
print("✅ Testing complete! Open http://localhost:5000 to view the dashboard.")
print("=" * 60)