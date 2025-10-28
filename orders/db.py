
from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId
from datetime import datetime

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection"""
        mongo_settings = settings.MONGODB_SETTINGS
        self.client = MongoClient(
            mongo_settings['host'],
            mongo_settings['port']
        )
        self.db = self.client[mongo_settings['db_name']]
        
        # Collections
        self.customers = self.db['customers']
        self.products = self.db['products']
        self.orders = self.db['orders']
        self.deliveries = self.db['deliveries']
        self.payments = self.db['payments']
        self.inventory_logs = self.db['inventory_logs']
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        self.customers.create_index('email', unique=True)
        self.orders.create_index('customer_id')
        self.orders.create_index('status')
        self.products.create_index('name')
        self.products.create_index('category')
        self.products.create_index('price')
        self.deliveries.create_index('order_id')
        self.payments.create_index('order_id')
        self.inventory_logs.create_index([('product_id', 1), ('timestamp', -1)])

# Helper functions
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, list):
            doc[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
    return doc

def to_object_id(id_string):
    """Convert string to ObjectId"""
    try:
        return ObjectId(id_string)
    except:
        return None

def validate_image_url(url):
    """Validate if URL is a valid image URL"""
    if not url:
        return True  # Allow empty URLs
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    valid_domains = ['unsplash.com', 'pexels.com', 'pixabay.com', 'localhost', '127.0.0.1']
    
    # Check if it's a relative URL (uploaded file)
    if url.startswith('/media/'):
        return True
    
    # Check if it's from a valid domain
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path.lower()
        
        # Check domain
        if any(valid_domain in domain for valid_domain in valid_domains):
            return True
        
        # Check extension
        if any(path.endswith(ext) for ext in valid_extensions):
            return True
            
        return False
    except:
        return False

def get_default_product_image():
    """Return default placeholder image URL"""
    return '/media/products/default-product.png'

# Initialize MongoDB connection
db = MongoDB()