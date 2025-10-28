import os
import uuid
import requests
import random
import string

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from bson import ObjectId
from datetime import datetime
import json
import hashlib

from .db import db, serialize_doc, to_object_id

from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def customer_login_page(request):
    return render(request, 'customer_login.html')

def admin_login_page(request):
    return render(request, 'admin_login.html')

def customer_signup_page(request):
    return render(request, 'customer_signup.html')

def admin_signup_page(request):
    return render(request, 'admin_signup.html')

def customer_dashboard_page(request):
    return render(request, 'customer_dashboard.html')

def admin_dashboard_page(request):
    return render(request, 'admin_dashboard.html')

# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def generate_transaction_id():
    """Generate unique transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# Authentication Views
@csrf_exempt
@require_http_methods(["POST"])
def customer_signup(request):
    try:
        data = json.loads(request.body)
        
        # Check if customer exists
        if db.customers.find_one({'email': data['email']}):
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        customer = {
            'name': data['name'],
            'email': data['email'],
            'password': hash_password(data['password']),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'role': 'customer',
            'created_at': datetime.now()
        }
        
        result = db.customers.insert_one(customer)
        return JsonResponse({
            'message': 'Customer created successfully',
            'customer_id': str(result.inserted_id)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

#function for image upload

@csrf_exempt
@require_http_methods(["POST"])
def upload_product_image(request):
    """Upload product image"""
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image = request.FILES['image']
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(image.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({'error': 'Invalid file type. Allowed: JPG, PNG, GIF, WEBP'}, status=400)
        
        # Validate file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'File too large. Max size: 5MB'}, status=400)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'products'))
        saved_filename = fs.save(filename, image)
        file_url = f"{settings.MEDIA_URL}products/{saved_filename}"
        
        return JsonResponse({
            'message': 'Image uploaded successfully',
            'image_url': file_url
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def customer_login(request):
    try:
        data = json.loads(request.body)
        customer = db.customers.find_one({'email': data['email']})
        
        if customer and verify_password(data['password'], customer['password']):
            request.session['user_id'] = str(customer['_id'])
            request.session['user_role'] = 'customer'
            customer_data = serialize_doc(customer)
            del customer_data['password']
            return JsonResponse({
                'message': 'Login successful',
                'user': customer_data
            })
        
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@require_http_methods(["POST"])
def admin_signup(request):
    try:
        data = json.loads(request.body)
        
        # Check if request is from authenticated admin (dashboard call)
        user_role = request.session.get('user_role')
        is_admin_creating = user_role == 'admin'
        
        # If NOT authenticated admin, check registration key
        if not is_admin_creating:
            registration_key = data.get('registration_key')
            if not registration_key or registration_key != settings.ADMIN_REGISTRATION_KEY:
                return JsonResponse({'error': 'Invalid admin registration key'}, status=403)
        
        # Check if email already exists
        if db.customers.find_one({'email': data['email']}):
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        # Create admin account
        admin = {
            'name': data['name'],
            'email': data['email'],
            'password': hash_password(data['password']),
            'role': 'admin',
            'created_at': datetime.now()
        }
        
        result = db.customers.insert_one(admin)
        return JsonResponse({
            'message': 'Admin created successfully',
            'admin_id': str(result.inserted_id)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    try:
        data = json.loads(request.body)
        admin = db.customers.find_one({'email': data['email'], 'role': 'admin'})
        
        if admin and verify_password(data['password'], admin['password']):
            request.session['user_id'] = str(admin['_id'])
            request.session['user_role'] = 'admin'
            admin_data = serialize_doc(admin)
            del admin_data['password']
            return JsonResponse({
                'message': 'Login successful',
                'user': admin_data
            })
        
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def user_logout(request):
    request.session.flush()
    return JsonResponse({'message': 'Logout successful'})

# Product Views
@require_http_methods(["GET"])
def get_products(request):
    try:
        products = list(db.products.find())
        return JsonResponse(serialize_doc(products), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def create_product(request):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        product = {
            'name': data['name'],
            'description': data.get('description', ''),
            'price': float(data['price']),
            'stock': int(data['stock']),
            'category': data.get('category', ''),
            'image_url': data.get('image_url', ''),  
            'created_at': datetime.now()
        }
        
        result = db.products.insert_one(product)
        
        # Log inventory
        db.inventory_logs.insert_one({
            'product_id': result.inserted_id,
            'change': product['stock'],
            'reason': 'Initial stock',
            'timestamp': datetime.now()
        })
        
        return JsonResponse({
            'message': 'Product created successfully',
            'product_id': str(result.inserted_id)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@csrf_exempt
@require_http_methods(["PUT"])
def update_product(request, product_id):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        oid = to_object_id(product_id)
        
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'stock' in data:
            old_product = db.products.find_one({'_id': oid})
            new_stock = int(data['stock'])
            update_data['stock'] = new_stock
            
            
            db.inventory_logs.insert_one({
                'product_id': oid,
                'change': new_stock - old_product['stock'],
                'reason': 'Manual update',
                'timestamp': datetime.now()
            })
        if 'category' in data:
            update_data['category'] = data['category']
        if 'image_url' in data:  
            update_data['image_url'] = data['image_url']
        
        db.products.update_one({'_id': oid}, {'$set': update_data})
        return JsonResponse({'message': 'Product updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product(request, product_id):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        oid = to_object_id(product_id)
        db.products.delete_one({'_id': oid})
        return JsonResponse({'message': 'Product deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Order Views
@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        items = data['items']
        
        # Validate stock and calculate total
        total_amount = 0
        order_items = []
        
        for item in items:
            product = db.products.find_one({'_id': to_object_id(item['product_id'])})
            if not product:
                return JsonResponse({'error': f'Product not found'}, status=400)
            
            if product['stock'] < item['quantity']:
                return JsonResponse({
                    'error': f'Insufficient stock for {product["name"]}'
                }, status=400)
            
            item_total = product['price'] * item['quantity']
            total_amount += item_total
            
            order_items.append({
                'product_id': to_object_id(item['product_id']),
                'product_name': product['name'],
                'quantity': item['quantity'],
                'price': product['price'],
                'subtotal': item_total
            })
        
        # Create order
        order = {
            'customer_id': to_object_id(user_id),
            'items': order_items,
            'total_amount': total_amount,
            'status': 'pending',
            'payment_status': 'unpaid',
            'shipping_address': data.get('shipping_address', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.orders.insert_one(order)
        
        # Update stock and log inventory
        for item in items:
            product_oid = to_object_id(item['product_id'])
            db.products.update_one(
                {'_id': product_oid},
                {'$inc': {'stock': -item['quantity']}}
            )
            
            db.inventory_logs.insert_one({
                'product_id': product_oid,
                'change': -item['quantity'],
                'reason': f'Order {result.inserted_id}',
                'timestamp': datetime.now()
            })
        
        # Create delivery record
        db.deliveries.insert_one({
            'order_id': result.inserted_id,
            'status': 'pending',
            'estimated_delivery': None,
            'actual_delivery': None,
            'tracking_number': None,
            'created_at': datetime.now()
        })
        
        return JsonResponse({
            'message': 'Order created successfully',
            'order_id': str(result.inserted_id)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_orders(request):
    try:
        user_id = request.session.get('user_id')
        user_role = request.session.get('user_role')
        
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        if user_role == 'admin':
            orders = list(db.orders.find().sort('created_at', -1))
        else:
            orders = list(db.orders.find({
                'customer_id': to_object_id(user_id)
            }).sort('created_at', -1))
        
        return JsonResponse(serialize_doc(orders), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_order(request, order_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        order = db.orders.find_one({'_id': to_object_id(order_id)})
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        return JsonResponse(serialize_doc(order))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_order_status(request, order_id):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        status = data['status']
        
        db.orders.update_one(
            {'_id': to_object_id(order_id)},
            {
                '$set': {
                    'status': status,
                    'updated_at': datetime.now()
                }
            }
        )
        
        # Update delivery status
        db.deliveries.update_one(
            {'order_id': to_object_id(order_id)},
            {'$set': {'status': status}}
        )
        
        return JsonResponse({'message': 'Order status updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def modify_order_quantity(request, order_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        product_id = data['product_id']
        new_quantity = int(data['quantity'])
        
        order = db.orders.find_one({'_id': to_object_id(order_id)})
        if not order or order['status'] != 'pending':
            return JsonResponse({
                'error': 'Order cannot be modified'
            }, status=400)
        
        # Find item in order
        item_index = None
        old_quantity = 0
        for i, item in enumerate(order['items']):
            if str(item['product_id']) == product_id:
                item_index = i
                old_quantity = item['quantity']
                break
        
        if item_index is None:
            return JsonResponse({'error': 'Product not in order'}, status=400)
        
        quantity_diff = new_quantity - old_quantity
        product = db.products.find_one({'_id': to_object_id(product_id)})
        
        # Check stock
        if quantity_diff > 0 and product['stock'] < quantity_diff:
            return JsonResponse({'error': 'Insufficient stock'}, status=400)
        
        # Update order
        new_subtotal = product['price'] * new_quantity
        db.orders.update_one(
            {
                '_id': to_object_id(order_id),
                'items.product_id': to_object_id(product_id)
            },
            {
                '$set': {
                    'items.$.quantity': new_quantity,
                    'items.$.subtotal': new_subtotal,
                    'updated_at': datetime.now()
                }
            }
        )
        
        # Recalculate total
        order = db.orders.find_one({'_id': to_object_id(order_id)})
        total = sum(item['subtotal'] for item in order['items'])
        db.orders.update_one(
            {'_id': to_object_id(order_id)},
            {'$set': {'total_amount': total}}
        )
        
        # Update stock
        db.products.update_one(
            {'_id': to_object_id(product_id)},
            {'$inc': {'stock': -quantity_diff}}
        )
        
        # Log inventory
        db.inventory_logs.insert_one({
            'product_id': to_object_id(product_id),
            'change': -quantity_diff,
            'reason': f'Order {order_id} modified',
            'timestamp': datetime.now()
        })
        
        return JsonResponse({'message': 'Order quantity updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_order(request, order_id):
    try:
        user_role = request.session.get('user_role')
        if user_role != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        order = db.orders.find_one({'_id': to_object_id(order_id)})
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        # Restore stock if order is canceled
        if order['status'] in ['pending', 'processing']:
            for item in order['items']:
                db.products.update_one(
                    {'_id': item['product_id']},
                    {'$inc': {'stock': item['quantity']}}
                )
                
                db.inventory_logs.insert_one({
                    'product_id': item['product_id'],
                    'change': item['quantity'],
                    'reason': f'Order {order_id} canceled',
                    'timestamp': datetime.now()
                })
        
        # Delete related records
        db.deliveries.delete_many({'order_id': to_object_id(order_id)})
        db.payments.delete_many({'order_id': to_object_id(order_id)})
        db.orders.delete_one({'_id': to_object_id(order_id)})
        
        return JsonResponse({'message': 'Order deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Payment Integration - SSLCommerz
@csrf_exempt
@require_http_methods(["POST"])
def initiate_payment(request):
    """Initiate SSLCommerz payment"""
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        # Get order details
        order = db.orders.find_one({'_id': to_object_id(order_id)})
        if not order:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        # Get customer details
        customer = db.customers.find_one({'_id': to_object_id(user_id)})
        
        # Generate transaction ID
        tran_id = generate_transaction_id()
        
        # Prepare payment data
        post_data = {
            'store_id': settings.SSLCOMMERZ_SETTINGS['store_id'],
            'store_passwd': settings.SSLCOMMERZ_SETTINGS['store_pass'],
            'total_amount': float(order['total_amount']),
            'currency': 'BDT',
            'tran_id': tran_id,
            'success_url': settings.SSLCOMMERZ_SETTINGS['success_url'],
            'fail_url': settings.SSLCOMMERZ_SETTINGS['fail_url'],
            'cancel_url': settings.SSLCOMMERZ_SETTINGS['cancel_url'],
            'ipn_url': settings.SSLCOMMERZ_SETTINGS['ipn_url'],
            'cus_name': customer['name'],
            'cus_email': customer['email'],
            'cus_add1': customer.get('address', 'Dhaka'),
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_phone': customer.get('phone', '01700000000'),
            'shipping_method': 'NO',
            'product_name': f"Order #{order_id[-6:]}",
            'product_category': 'General',
            'product_profile': 'general',
            'num_of_item': len(order['items']),
        }
        
        # Call SSLCommerz API
        response = requests.post(
            settings.SSLCOMMERZ_SETTINGS['api_url'],
            data=post_data
        )
        
        response_data = response.json()
        
        if response_data.get('status') == 'SUCCESS':
            # Store payment record
            db.payments.insert_one({
                'order_id': to_object_id(order_id),
                'transaction_id': tran_id,
                'amount': order['total_amount'],
                'currency': 'BDT',
                'status': 'pending',
                'payment_method': 'SSLCommerz',
                'gateway_response': response_data,
                'created_at': datetime.now()
            })
            
            return JsonResponse({
                'success': True,
                'gateway_url': response_data['GatewayPageURL'],
                'transaction_id': tran_id
            })
        else:
            return JsonResponse({
                'error': 'Payment initialization failed',
                'details': response_data
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST", "GET"])
def payment_success(request):
    """Handle successful payment"""
    try:
        if request.method == 'POST':
            data = request.POST
        else:
            data = request.GET
        
        tran_id = data.get('tran_id')
        val_id = data.get('val_id')
        amount = data.get('amount')
        
        # Validate payment
        validation_url = 'https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php'
        
        validation_data = {
            'val_id': val_id,
            'store_id': settings.SSLCOMMERZ_SETTINGS['store_id'],
            'store_passwd': settings.SSLCOMMERZ_SETTINGS['store_pass']
        }
        
        validation_response = requests.get(validation_url, params=validation_data)
        validation_result = validation_response.json()
        
        if validation_result.get('status') == 'VALID' or validation_result.get('status') == 'VALIDATED':
            # Update payment status
            payment = db.payments.find_one({'transaction_id': tran_id})
            if payment:
                db.payments.update_one(
                    {'transaction_id': tran_id},
                    {
                        '$set': {
                            'status': 'completed',
                            'validation_id': val_id,
                            'validated_at': datetime.now(),
                            'validation_response': validation_result
                        }
                    }
                )
                
                # Update order status
                db.orders.update_one(
                    {'_id': payment['order_id']},
                    {
                        '$set': {
                            'payment_status': 'paid',
                            'status': 'processing',
                            'updated_at': datetime.now()
                        }
                    }
                )
                
                # Update delivery status
                db.deliveries.update_one(
                    {'order_id': payment['order_id']},
                    {'$set': {'status': 'processing'}}
                )
                
                # Redirect to customer dashboard with success message
                return render(request, 'payment_success.html', {
                    'transaction_id': tran_id,
                    'amount': amount,
                    'order_id': str(payment['order_id'])
                })
        
        return render(request, 'payment_failed.html', {
            'message': 'Payment validation failed'
        })
        
    except Exception as e:
        return render(request, 'payment_failed.html', {
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST", "GET"])
def payment_fail(request):
    """Handle failed payment"""
    try:
        if request.method == 'POST':
            data = request.POST
        else:
            data = request.GET
        
        tran_id = data.get('tran_id')
        
        # Update payment status
        db.payments.update_one(
            {'transaction_id': tran_id},
            {
                '$set': {
                    'status': 'failed',
                    'failed_at': datetime.now(),
                    'failure_reason': data.get('error', 'Payment failed')
                }
            }
        )
        
        return render(request, 'payment_failed.html', {
            'message': 'Payment failed. Please try again.'
        })
        
    except Exception as e:
        return render(request, 'payment_failed.html', {
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST", "GET"])
def payment_cancel(request):
    """Handle cancelled payment"""
    try:
        if request.method == 'POST':
            data = request.POST
        else:
            data = request.GET
        
        tran_id = data.get('tran_id')
        
        # Update payment status
        db.payments.update_one(
            {'transaction_id': tran_id},
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.now()
                }
            }
        )
        
        return render(request, 'payment_cancel.html', {
            'message': 'Payment cancelled by user.'
        })
        
    except Exception as e:
        return render(request, 'payment_cancel.html', {
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def payment_ipn(request):
    """Handle IPN from SSLCommerz"""
    try:
        data = request.POST
        tran_id = data.get('tran_id')
        status = data.get('status')
        
        # Update payment based on IPN
        db.payments.update_one(
            {'transaction_id': tran_id},
            {
                '$set': {
                    'ipn_received': True,
                    'ipn_status': status,
                    'ipn_data': dict(data),
                    'ipn_received_at': datetime.now()
                }
            }
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Advanced Queries
@require_http_methods(["GET"])
def get_customers_by_product(request, product_id):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        pipeline = [
            {
                '$match': {
                    'items.product_id': to_object_id(product_id)
                }
            },
            {
                '$lookup': {
                    'from': 'customers',
                    'localField': 'customer_id',
                    'foreignField': '_id',
                    'as': 'customer'
                }
            },
            {
                '$unwind': '$customer'
            },
            {
                '$group': {
                    '_id': '$customer._id',
                    'name': {'$first': '$customer.name'},
                    'email': {'$first': '$customer.email'},
                    'order_count': {'$sum': 1}
                }
            }
        ]
        
        customers = list(db.orders.aggregate(pipeline))
        return JsonResponse(serialize_doc(customers), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_delivery_tracking(request, order_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        pipeline = [
            {
                '$match': {
                    'order_id': to_object_id(order_id)
                }
            },
            {
                '$lookup': {
                    'from': 'orders',
                    'localField': 'order_id',
                    'foreignField': '_id',
                    'as': 'order'
                }
            },
            {
                '$unwind': '$order'
            }
        ]
        
        delivery = list(db.deliveries.aggregate(pipeline))
        if delivery:
            return JsonResponse(serialize_doc(delivery[0]))
        return JsonResponse({'error': 'Delivery not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Customer Management
@require_http_methods(["GET"])
def get_customers(request):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        customers = list(db.customers.find({'role': 'customer'}))
        for customer in customers:
            del customer['password']
        return JsonResponse(serialize_doc(customers), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Admin Management
@require_http_methods(["GET"])
def get_admins(request):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        admins = list(db.customers.find({'role': 'admin'}))
        for admin in admins:
            del admin['password']
        return JsonResponse(serialize_doc(admins), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_admin(request, admin_id):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Prevent deleting yourself
        if request.session.get('user_id') == admin_id:
            return JsonResponse({'error': 'Cannot delete your own account'}, status=400)
        
        # Ensure at least one admin remains
        admin_count = db.customers.count_documents({'role': 'admin'})
        if admin_count <= 1:
            return JsonResponse({'error': 'Cannot delete the last admin'}, status=400)
        
        db.customers.delete_one({'_id': to_object_id(admin_id), 'role': 'admin'})
        return JsonResponse({'message': 'Admin deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Dashboard Stats
@require_http_methods(["GET"])
def get_dashboard_stats(request):
    try:
        if request.session.get('user_role') != 'admin':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        total_orders = db.orders.count_documents({})
        total_customers = db.customers.count_documents({'role': 'customer'})
        total_products = db.products.count_documents({})
        pending_orders = db.orders.count_documents({'status': 'pending'})
        
        # Revenue
        pipeline = [
            {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
        ]
        revenue = list(db.orders.aggregate(pipeline))
        total_revenue = revenue[0]['total'] if revenue else 0
        
        return JsonResponse({
            'total_orders': total_orders,
            'total_customers': total_customers,
            'total_products': total_products,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)