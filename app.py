# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    current_stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    max_stock = db.Column(db.Integer, default=100)
    min_stock = db.Column(db.Integer, default=5)
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_ml_model = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'current_stock': self.current_stock,
            'reorder_level': self.reorder_level,
            'max_stock': self.max_stock,
            'min_stock': self.min_stock,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'has_ml_model': self.has_ml_model,
            'stock_status': self.get_stock_status()
        }
    
    def get_stock_status(self):
        if self.current_stock <= self.min_stock:
            return 'critical'
        elif self.current_stock <= self.reorder_level:
            return 'low'
        elif self.current_stock >= self.max_stock * 0.8:
            return 'overstocked'
        else:
            return 'healthy'

class SalesHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.String(50), nullable=True)
    sale_amount = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity_sold': self.quantity_sold,
            'sale_date': self.sale_date.isoformat(),
            'customer_id': self.customer_id,
            'sale_amount': self.sale_amount
        }

class MLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    model_type = db.Column(db.String(50), default='linear_regression')
    accuracy = db.Column(db.Float, default=0.0)
    trained_date = db.Column(db.DateTime, default=datetime.utcnow)
    model_path = db.Column(db.String(200))
    data_points = db.Column(db.Integer, default=0)

class InventoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    change_type = db.Column(db.String(20))  # 'sale', 'restock', 'adjustment'
    quantity_change = db.Column(db.Integer)
    previous_stock = db.Column(db.Integer)
    new_stock = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(200))

# Initialize database
with app.app_context():
    db.create_all()

# ML Training Function
def train_predictive_model(product_id):
    """Train a simple ML model to predict stock needs"""
    try:
        # Get sales data sorted by date
        sales_data = SalesHistory.query.filter_by(product_id=product_id).order_by(SalesHistory.sale_date.asc()).all()
        
        if len(sales_data) < 3:
            return None, "Not enough data to train model (need at least 3 sales records)"
        
        # Get the earliest date as reference
        earliest_date = sales_data[0].sale_date
        
        # Prepare data with proper date features
        df = pd.DataFrame([{
            'days_since_start': (s.sale_date - earliest_date).days,
            'sales': s.quantity_sold,
            'day_of_week': s.sale_date.weekday(),
            'month': s.sale_date.month
        } for s in sales_data])
        
        # Create features
        X = np.array(df['days_since_start']).reshape(-1, 1)
        y = np.array(df['sales'])
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate accuracy (R² score)
        accuracy = model.score(X, y)
        
        # Save model
        model_path = f'models/product_{product_id}.pkl'
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, model_path)
        
        # Remove old ML models for this product
        MLModel.query.filter_by(product_id=product_id).delete()
        
        # Save model info to database
        ml_model = MLModel(
            product_id=product_id,
            model_type='linear_regression',
            accuracy=accuracy,
            model_path=model_path,
            data_points=len(sales_data)
        )
        db.session.add(ml_model)
        
        # Update product has_ml_model flag
        product = Product.query.get(product_id)
        if product:
            product.has_ml_model = True
        
        db.session.commit()
        
        return model, f"Model trained successfully with {len(sales_data)} records (R²: {accuracy:.2f})"
        
    except Exception as e:
        db.session.rollback()
        return None, f"Error training model: {str(e)}"

def predict_stock_needs(product_id, days_ahead=7):
    """Predict stock needed for next days"""
    try:
        # Get the latest ML model for this product
        ml_model = MLModel.query.filter_by(product_id=product_id).order_by(MLModel.id.desc()).first()
        
        if not ml_model:
            return None, "No trained model found. Train the model first."
        
        # Check if model file exists
        if not os.path.exists(ml_model.model_path):
            return None, "Model file not found. Please retrain the model."
        
        # Load model
        model = joblib.load(ml_model.model_path)
        
        # Get product info
        product = Product.query.get(product_id)
        if not product:
            return None, "Product not found"
        
        # Get sales data to determine the date range
        sales_data = SalesHistory.query.filter_by(product_id=product_id).order_by(SalesHistory.sale_date.asc()).all()
        if not sales_data:
            return None, "No sales data available for prediction"
        
        earliest_date = sales_data[0].sale_date
        last_date = sales_data[-1].sale_date
        
        # Predict for future days (days after the last sale date)
        future_days = [(last_date - earliest_date).days + i for i in range(1, days_ahead + 1)]
        future_days = np.array(future_days).reshape(-1, 1)
        
        predictions = model.predict(future_days)
        
        # Ensure positive predictions and round up
        predictions = np.maximum(predictions, 0)
        total_needed = int(np.ceil(sum(predictions)))
        
        # Add some buffer for uncertainty (10%)
        total_needed = int(total_needed * 1.1)
        
        # Calculate daily average
        daily_avg = np.mean(predictions)
        
        return {
            'total_needed': total_needed,
            'daily_average': round(daily_avg, 2),
            'daily_predictions': [int(np.ceil(p)) for p in predictions]
        }, f"Predicted {total_needed} units needed in {days_ahead} days"
        
    except Exception as e:
        return None, f"Error making prediction: {str(e)}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(
        name=data['name'],
        sku=data['sku'],
        current_stock=data.get('current_stock', 0),
        reorder_level=data.get('reorder_level', 10),
        max_stock=data.get('max_stock', 100),
        min_stock=data.get('min_stock', 5),
        price=data.get('price', 0.0),
        category=data.get('category', 'General'),
        has_ml_model=False
    )
    db.session.add(product)
    db.session.commit()
    
    # Log initial inventory
    log = InventoryLog(
        product_id=product.id,
        change_type='adjustment',
        quantity_change=product.current_stock,
        previous_stock=0,
        new_stock=product.current_stock,
        notes='Initial inventory setup'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    # Log previous stock for tracking
    previous_stock = product.current_stock
    
    product.name = data.get('name', product.name)
    product.current_stock = data.get('current_stock', product.current_stock)
    product.reorder_level = data.get('reorder_level', product.reorder_level)
    product.max_stock = data.get('max_stock', product.max_stock)
    product.min_stock = data.get('min_stock', product.min_stock)
    product.price = data.get('price', product.price)
    product.category = data.get('category', product.category)
    
    if previous_stock != product.current_stock:
        log = InventoryLog(
            product_id=product.id,
            change_type='adjustment',
            quantity_change=product.current_stock - previous_stock,
            previous_stock=previous_stock,
            new_stock=product.current_stock,
            notes='Stock adjustment'
        )
        db.session.add(log)
    
    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Delete associated ML model records
    MLModel.query.filter_by(product_id=product_id).delete()
    
    # Delete model file if exists
    model_path = f'models/product_{product_id}.pkl'
    if os.path.exists(model_path):
        os.remove(model_path)
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/sales', methods=['POST'])
def record_sale():
    data = request.json
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.current_stock < data['quantity_sold']:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    sale = SalesHistory(
        product_id=data['product_id'],
        quantity_sold=data['quantity_sold'],
        customer_id=data.get('customer_id', None),
        sale_amount=data.get('sale_amount', data['quantity_sold'] * product.price)
    )
    db.session.add(sale)
    
    # Update current stock
    previous_stock = product.current_stock
    product.current_stock -= data['quantity_sold']
    product.has_ml_model = False  # Mark model as stale
    
    # Log the change
    log = InventoryLog(
        product_id=product.id,
        change_type='sale',
        quantity_change=-data['quantity_sold'],
        previous_stock=previous_stock,
        new_stock=product.current_stock,
        notes=f'Sale of {data["quantity_sold"]} units'
    )
    db.session.add(log)
    
    db.session.commit()
    return jsonify(sale.to_dict()), 201

@app.route('/api/restock', methods=['POST'])
def restock_product():
    data = request.json
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    quantity = data.get('quantity', 0)
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be positive'}), 400
    
    previous_stock = product.current_stock
    product.current_stock += quantity
    
    # Log the restock
    log = InventoryLog(
        product_id=product.id,
        change_type='restock',
        quantity_change=quantity,
        previous_stock=previous_stock,
        new_stock=product.current_stock,
        notes=data.get('notes', 'Restock')
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'product_id': product.id,
        'product_name': product.name,
        'new_stock': product.current_stock,
        'added_quantity': quantity
    })

@app.route('/api/products/<int:product_id>/train', methods=['POST'])
def train_model(product_id):
    model, message = train_predictive_model(product_id)
    if model is None:
        return jsonify({'error': message}), 400
    
    # Get accuracy from the latest ML model
    ml_model = MLModel.query.filter_by(product_id=product_id).order_by(MLModel.id.desc()).first()
    accuracy = ml_model.accuracy if ml_model else 0
    data_points = ml_model.data_points if ml_model else 0
    
    return jsonify({
        'message': message,
        'accuracy': accuracy,
        'data_points': data_points
    })

@app.route('/api/products/<int:product_id>/predict', methods=['GET'])
def predict_stock(product_id):
    days = request.args.get('days', 7, type=int)
    if days < 1 or days > 30:
        return jsonify({'error': 'Days must be between 1 and 30'}), 400
    
    result, message = predict_stock_needs(product_id, days)
    if result is None:
        return jsonify({'error': message}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get the ML model to check accuracy
    ml_model = MLModel.query.filter_by(product_id=product_id).order_by(MLModel.id.desc()).first()
    
    stock_level = product.current_stock
    needs_reorder = result['total_needed'] > product.reorder_level
    
    # Calculate confidence based on model accuracy
    if ml_model:
        accuracy = ml_model.accuracy
        if accuracy > 0.7:
            confidence = 'High'
        elif accuracy > 0.5:
            confidence = 'Medium'
        else:
            confidence = 'Low'
    else:
        confidence = 'Unknown'
    
    return jsonify({
        'product_id': product_id,
        'product_name': product.name,
        'predicted_need': result['total_needed'],
        'daily_average': result['daily_average'],
        'daily_predictions': result['daily_predictions'],
        'current_stock': stock_level,
        'days': days,
        'needs_reorder': needs_reorder,
        'recommendation': '⚠️ Reorder recommended' if needs_reorder else '✅ Stock sufficient',
        'stock_after_period': max(0, stock_level - result['total_needed']),
        'confidence': confidence,
        'model_accuracy': round(ml_model.accuracy * 100, 2) if ml_model else 0
    })

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard():
    products = Product.query.all()
    total_products = len(products)
    
    # Stock status counts
    low_stock = [p for p in products if p.current_stock <= p.reorder_level]
    critical_stock = [p for p in products if p.current_stock <= p.min_stock]
    overstocked = [p for p in products if p.current_stock >= p.max_stock * 0.8]
    
    total_value = sum(p.price * p.current_stock for p in products)
    
    # Recent sales
    recent_sales = SalesHistory.query.order_by(SalesHistory.sale_date.desc()).limit(10).all()
    
    # Count products with ML models
    ml_models_count = MLModel.query.count()
    
    # Total sales today
    today = datetime.utcnow().date()
    today_sales = SalesHistory.query.filter(
        db.func.date(SalesHistory.sale_date) == today
    ).all()
    today_sales_count = len(today_sales)
    today_revenue = sum(s.sale_amount for s in today_sales)
    
    # Top selling products
    top_sellers = db.session.query(
        Product.name,
        db.func.sum(SalesHistory.quantity_sold).label('total_sold')
    ).join(SalesHistory).group_by(Product.id).order_by(db.func.sum(SalesHistory.quantity_sold).desc()).limit(5).all()
    
    return jsonify({
        'total_products': total_products,
        'low_stock_items': len(low_stock),
        'critical_stock_items': len(critical_stock),
        'overstocked_items': len(overstocked),
        'total_inventory_value': round(total_value, 2),
        'recent_sales': [s.to_dict() for s in recent_sales],
        'low_stock_products': [p.to_dict() for p in low_stock[:5]],
        'ml_models_count': ml_models_count,
        'today_sales_count': today_sales_count,
        'today_revenue': round(today_revenue, 2),
        'top_selling_products': [{'name': t[0], 'total_sold': int(t[1])} for t in top_sellers]
    })

@app.route('/api/analytics/sales-history/<int:product_id>', methods=['GET'])
def get_sales_history(product_id):
    days = request.args.get('days', 30, type=int)
    sales = SalesHistory.query.filter_by(product_id=product_id).filter(
        SalesHistory.sale_date >= datetime.utcnow() - timedelta(days=days)
    ).order_by(SalesHistory.sale_date.asc()).all()
    
    return jsonify([s.to_dict() for s in sales])

@app.route('/api/analytics/inventory-logs/<int:product_id>', methods=['GET'])
def get_inventory_logs(product_id):
    logs = InventoryLog.query.filter_by(product_id=product_id).order_by(
        InventoryLog.timestamp.desc()
    ).limit(50).all()
    
    return jsonify([{
        'id': l.id,
        'change_type': l.change_type,
        'quantity_change': l.quantity_change,
        'previous_stock': l.previous_stock,
        'new_stock': l.new_stock,
        'timestamp': l.timestamp.isoformat(),
        'notes': l.notes
    } for l in logs])

if __name__ == '__main__':
    app.run(debug=True, port=5000)