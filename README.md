# Inventory Management System with AI Predictions

An intelligent inventory management system powered by machine learning that helps businesses optimize stock levels, predict demand, and prevent stockouts or overstocking.

Website url: inventorymanagement-blush.vercel.app

## 🚀 Features

- **AI-Powered Predictions**: Uses Linear Regression to forecast stock needs for up to 30 days
- **Real-time Inventory Tracking**: Monitor stock levels, reorder points, and inventory value
- **Automated Restocking**: Easy restock management with logging
- **Sales Analytics**: Track sales history, revenue, and top-selling products
- **Intelligent Alerts**: Automatic detection of low stock, critical stock, and overstocked items
- **Interactive Dashboard**: Visual web interface for monitoring all inventory metrics
- **RESTful API**: Comprehensive API for integration with other systems

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional)

## 🛠️ Installation

### Quick Setup (Windows)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/inventory-management-ai.git
cd inventory-management-ai
```

2. Run the setup script:
```bash
setup.bat
```

### Manual Setup (All Platforms)

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create necessary directories:
```bash
mkdir templates models
```

## 📁 Project Structure

```
inventory-management-ai/
├── app.py                 # Main Flask application
├── test_data.py           # Test script with sample data
├── check_server.py        # Server health checker
├── requirements.txt       # Python dependencies
├── setup.bat             # Windows setup script
├── templates/
│   └── index.html        # Web dashboard
├── models/               # Saved ML models
└── instance/
    └── inventory.db      # SQLite database
```

## 🏃 Running the Application

### Start the Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

### Load Sample Data

In a new terminal:
```bash
python test_data.py
```

This will:
- Add 4 sample products (electronics and clothing)
- Generate 7 days of sales data
- Train ML models for each product
- Display 7-day predictions

### Check Server Status

```bash
python check_server.py
```

## 🎯 Using the API

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | Get all products |
| GET | `/api/products/{id}` | Get specific product |
| POST | `/api/products` | Create new product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |

### Sales & Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sales` | Record a sale |
| POST | `/api/restock` | Restock inventory |

### ML & Predictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products/{id}/train` | Train ML model |
| GET | `/api/products/{id}/predict?days=7` | Get predictions |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard metrics |
| GET | `/api/analytics/sales-history/{id}` | Product sales history |

## 📊 Dashboard Features

- **Overview Cards**: Total products, low stock items, inventory value
- **Stock Status**: Visual indicators for critical, low, healthy, and overstocked items
- **Top Selling Products**: View best-performing products
- **Recent Activity**: Track sales and inventory changes
- **ML Model Status**: See which products have trained models
- **Predictions**: View AI-generated stock forecasts

## 🧠 How the AI Works

### Training Process
1. Collects historical sales data
2. Creates features: days since start, day of week, month
3. Trains a Linear Regression model
4. Calculates R² accuracy score
5. Saves model for future predictions

### Prediction Process
1. Loads the trained model for a product
2. Predicts daily sales for the next N days
3. Calculates total stock needed
4. Provides confidence level based on model accuracy
5. Generates reorder recommendations

### Model Accuracy
- **High (>70%)**: Reliable predictions
- **Medium (50-70%)**: Moderate confidence
- **Low (<50%)**: Use with caution
- **Unknown**: Insufficient data

## 🔧 Configuration

### Environment Variables
Create a `.env` file for customization:
```env
# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///inventory.db

# Flask settings
FLASK_DEBUG=True
PORT=5000
```

### Database
The system uses SQLite by default. To use PostgreSQL or MySQL:
```python
# In app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

## 🧪 Testing

### Sample Test Data
The `test_data.py` script provides realistic test scenarios:
- Multiple product categories
- Varied sales patterns (weekend spikes, bulk orders)
- Automated restocking
- ML model training and validation

### Running Tests
```bash
# Start the server first
python app.py

# In another terminal
python test_data.py
```

## 📈 Performance Considerations

- **Data Requirements**: Minimum 3 sales records for model training
- **Model Retraining**: Models become stale after new sales; retrain periodically
- **Prediction Accuracy**: Improves with more data points
- **Scalability**: SQLite handles up to 100k records; use PostgreSQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to new functions
- Update README for new features
- Write unit tests for critical functionality

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask for the web framework
- Scikit-learn for ML capabilities
- SQLAlchemy for ORM
- All contributors and users

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the [API Documentation](API.md) for detailed endpoints
- Review the [Troubleshooting Guide](TROUBLESHOOTING.md)

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Linear Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)

---

