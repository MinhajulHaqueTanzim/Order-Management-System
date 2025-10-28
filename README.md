# Order Management System

A full-featured e-commerce platform for businesses in Bangladesh with real-time inventory management, secure payment integration, and role-based access control.

## Features

### Customer Portal
- Product catalog with real-time stock availability
- Shopping cart and order management
- SSLCommerz payment integration (bKash, Nagad, Cards)
- Order tracking and history
- Cash on delivery option

### Admin Dashboard
- Real-time statistics and analytics
- Complete product management with image uploads
- Order processing and status updates
- Customer and admin account management
- Inventory tracking with historical logs

## Technology Stack

**Backend:** Django 5.2.7, Python 3.8+, Django REST Framework  
**Frontend:** HTML5, CSS3, JavaScript (ES6+)  
**Database:** MongoDB 4.0+, SQLite (sessions)  
**Payment:** SSLCommerz Gateway

## Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.0+
- pip package manager

### Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start MongoDB**
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

4. **Create media directories**
```bash
mkdir -p media/products
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Start server**
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## Configuration

### Admin Registration Key
Update `order_management/settings.py`:
```python
ADMIN_REGISTRATION_KEY = 'YOUR_SECURE_KEY_HERE_2024'
```

### MongoDB Settings (Optional)
```python
MONGODB_SETTINGS = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'order_management_db'
}
```

### SSLCommerz Production Setup
```python
SSLCOMMERZ_SETTINGS = {
    'store_id': 'your_store_id',
    'store_pass': 'your_store_pass',
    'is_sandbox': False,
    'api_url': 'https://securepay.sslcommerz.com/gwprocess/v4/api.php',
    'success_url': 'https://yourdomain.com/api/payment/success/',
    'fail_url': 'https://yourdomain.com/api/payment/fail/',
    'cancel_url': 'https://yourdomain.com/api/payment/cancel/',
    'ipn_url': 'https://yourdomain.com/api/payment/ipn/'
}
```

## Quick Start

1. **Create admin account:** Navigate to `/admin-signup/` and use the registration key
2. **Add products:** Login and access Products Management
3. **Customer registration:** Available at `/customer-signup/`

## API Endpoints

### Authentication
- `POST /api/customer/signup/` - Customer registration
- `POST /api/customer/login/` - Customer authentication
- `POST /api/admin/login/` - Admin authentication

### Products
- `GET /api/products/` - List all products
- `POST /api/products/create/` - Create product (Admin)
- `POST /api/products/upload-image/` - Upload product image (Admin)

### Orders
- `POST /api/orders/create/` - Create new order
- `GET /api/orders/` - Get user orders
- `PUT /api/orders/{order_id}/status/` - Update status (Admin)

### Payments
- `POST /api/payment/initiate/` - Initiate SSLCommerz payment

## Database Schema

**Collections:** customers, products, orders, payments, inventory_logs

See full documentation for detailed schema information.

## Project Structure

```
order_management_system/
├── order_management/          # Django project configuration
├── orders/                    # Main application
├── templates/                 # HTML templates
├── media/products/            # Product images
├── manage.py
├── requirements.txt
└── README.md
```

## Security Features

- Session-based authentication
- Role-based access control (RBAC)
- Input validation and sanitization
- Secure password hashing
- Admin registration key protection

## License

Proprietary - All rights reserved
