from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from orders import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Admin Management
    path('api/admins/', views.get_admins, name='api_get_admins'),
    path('api/admins/<str:admin_id>/delete/', views.delete_admin, name='api_delete_admin'),
    
    # Frontend pages
    path('', views.index, name='index'),
    path('customer-login/', views.customer_login_page, name='customer_login_page'),
    path('admin-login/', views.admin_login_page, name='admin_login_page'),
    path('customer-signup/', views.customer_signup_page, name='customer_signup_page'),
    path('admin-signup/', views.admin_signup_page, name='admin_signup_page'),
    path('customer-dashboard/', views.customer_dashboard_page, name='customer_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_page, name='admin_dashboard'),
    
    # Authentication API
    path('api/customer/signup/', views.customer_signup, name='api_customer_signup'),
    path('api/customer/login/', views.customer_login, name='api_customer_login'),
    path('api/admin/signup/', views.admin_signup, name='api_admin_signup'),
    path('api/admin/login/', views.admin_login, name='api_admin_login'),
    path('api/logout/', views.user_logout, name='api_logout'),
    
    # Products API - IMPORTANT: Specific URLs must come BEFORE dynamic URLs
    path('api/products/', views.get_products, name='api_get_products'),
    path('api/products/create/', views.create_product, name='api_create_product'),
    path('api/products/upload-image/', views.upload_product_image, name='api_upload_product_image'),  # MOVED HERE
    path('api/products/<str:product_id>/', views.update_product, name='api_update_product'),  # After upload-image
    path('api/products/<str:product_id>/delete/', views.delete_product, name='api_delete_product'),
    
    # Orders API
    path('api/orders/', views.get_orders, name='api_get_orders'),
    path('api/orders/create/', views.create_order, name='api_create_order'),
    path('api/orders/<str:order_id>/', views.get_order, name='api_get_order'),
    path('api/orders/<str:order_id>/status/', views.update_order_status, name='api_update_order_status'),
    path('api/orders/<str:order_id>/quantity/', views.modify_order_quantity, name='api_modify_order_quantity'),
    path('api/orders/<str:order_id>/delete/', views.delete_order, name='api_delete_order'),


    # Payment API
    path('api/payment/initiate/', views.initiate_payment, name='api_initiate_payment'),
    path('api/payment/success/', views.payment_success, name='payment_success'),
    path('api/payment/fail/', views.payment_fail, name='payment_fail'),
    path('api/payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('api/payment/ipn/', views.payment_ipn, name='payment_ipn'),
    
    # Advanced Queries
    path('api/customers/by-product/<str:product_id>/', views.get_customers_by_product, name='api_customers_by_product'),
    path('api/delivery/<str:order_id>/', views.get_delivery_tracking, name='api_delivery_tracking'),
    
    # Customers API
    path('api/customers/', views.get_customers, name='api_get_customers'),
    
    # Dashboard Stats
    path('api/dashboard/stats/', views.get_dashboard_stats, name='api_dashboard_stats'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)