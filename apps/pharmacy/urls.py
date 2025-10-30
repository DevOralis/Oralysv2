from django.urls import path
from . import views

urlpatterns = [
    # Config
    path('configuration/', views.pharmacy_configuration, name='pharmacy_configuration'),
    
    # CRUD PharmaceuticalForm
    path('pharmaforms/', views.pharmaform_list, name='pharmaform_list'),  # optionnel, liste standalone
    path('pharmaforms/add/', views.pharmaform_create, name='pharmaform_create'),  # si besoin de page dédiée
    path('pharmaforms/edit/<int:pk>/', views.pharmaform_update, name='pharmaform_update'),
    path('pharmaform/delete/<int:pk>/', views.pharmaform_delete, name='pharmaform_delete'),
   

    # Supplier
    path('suppliers/', views.supplier_list, name='pharmacy_supplier_list'),
    path('suppliers/add/', views.supplier_create, name='pharmacy_supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='pharmacy_supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='pharmacy_supplier_delete'),

    # DCI
    path('dcis/', views.dci_list, name='dci_list'),
    path('dcis/add/', views.dci_create, name='dci_create'),
    path('dcis/<int:pk>/edit/', views.dci_update, name='dci_update'),
    path('dci/delete/<int:pk>/', views.dci_delete, name='dci_delete'),

    # Pharmacy
    path('pharmacies/', views.pharmacy_list, name='pharmacy_list'),
    path('pharmacies/add/', views.pharmacy_create, name='pharmacy_create'),
    path('pharmacies/<int:pk>/edit/', views.pharmacy_update, name='pharmacy_update'),
    path('location-type/delete/<int:pk>/', views.location_type_delete, name='location_type_delete'),
    path('stock-location/delete/<int:pk>/', views.stock_location_delete, name='stock_location_delete'),
    path('pharmacy/delete/<int:pk>/', views.delete_pharmacy, name='delete_pharmacy'),
    path('operation-type/delete/<int:pk>/', views.operation_type_delete, name='operation_type_delete'),
    path('category/delete/<int:pk>/', views.product_category_delete, name='product_category_delete'),
    path('unit/delete/<int:pk>/', views.product_unit_delete, name='product_unit_delete'),
    
    # Products
    path('products/', views.pharmacy_product_list, name='pharmacy_product_list'),
    path('products/add/', views.pharmacy_product_create, name='pharmacy_product_add'),
    path('products/<int:pk>/edit/', views.pharmacy_product_update, name='pharmacy_product_edit'),
    path('products/delete/<int:pk>/', views.pharmacy_product_delete, name='pharmacy_product_delete'),
    path('products/ajax/', views.pharmacy_product_list_ajax, name='pharmacy_product_list_ajax'),
    path('products/export/', views.pharmacy_product_export, name='pharmacy_product_export'),
    
    
    path('orders/', views.pharmacy_order_list, name='pharmacy_order_list'),
    path('orders/create/', views.create_pharmacy_order, name='pharmacy_order_create'),
    path('orders/delete/<int:pk>/', views.delete_pharmacy_order, name='pharmacy_order_delete'),
    path('orders/detail-json/<int:order_id>/', views.pharmacy_order_detail_json, name='pharmacy_order_detail_json'),    path('orders/confirm/<int:order_id>/', views.confirm_pharmacy_order, name='confirm_pharmacy_order'),
    path('orders/filter/', views.pharmacy_order_list_filtered, name='pharmacy_order_list_filtered'),
    path('orders/edit/<int:order_id>/', views.edit_pharmacy_order, name='pharmacy_order_edit'),
    path('orders/line/delete/<int:line_id>/', views.delete_pharmacy_order_line, name='delete_pharmacy_order_line'),
    path('orders/duplicate/<int:order_id>/', views.duplicate_pharmacy_order, name='duplicate_pharmacy_order'),
    path('orders/request-price/<int:order_id>/pdf/', views.generate_pharmacy_price_request_pdf, name='generate_pharmacy_price_request_pdf'),
    path('order/<int:order_id>/pdf/', views.generate_pharmacy_order_pdf, name='generate_pharmacy_order_pdf'),
    
    path('adjustment/', views.pharmacy_inventory_adjustment, name='pharmacy_inventory_adjustment'),
    path('adjustment/pdf/', views.pharmacy_inventory_adjustment_pdf, name='pharmacy_inventory_adjustment_pdf'),

    # Pharmacy stock move 
    path('stock-moves/', views.pharmacy_stock_move_list, name='pharmacy_stock_move_list'),
    path('stock-moves/create/', views.pharmacy_stock_move_create, name='pharmacy_stock_move_create'),
    path('stock-moves/<int:pk>/edit/', views.pharmacy_stock_move_update, name='pharmacy_stock_move_update'),
    path('stock-moves/<int:pk>/delete/', views.pharmacy_stock_move_delete, name='pharmacy_stock_move_delete'),
    path('stock-moves/<int:pk>/json/', views.pharmacy_stock_move_detail_json, name='pharmacy_stock_move_detail_json'),
    path('stock-moves/pdf/', views.pharmacy_stock_move_pdf, name='pharmacy_stock_move_pdf'),
    path('stock-moves/<int:pk>/delivery-pdf/', views.pharmacy_stock_move_delivery_pdf, name='pharmacy_stock_move_delivery_pdf'),

    # Inventory - similar to inventory module
    path('products/list/', views.pharmacy_inventory_list, name='pharmacy_inventory_list'),
    path('products/list/json/', views.pharmacy_inventory_list_json, name='pharmacy_inventory_list_json'),  
    path('products/list/pdf/', views.pharmacy_inventory_pdf, name='pharmacy_inventory_pdf'),

    # Ajax
    path('ajax/supplier-orders/', views.get_pharmacy_supplier_orders, name='get_pharmacy_supplier_orders'),
    path('ajax/order-lines/', views.get_pharmacy_order_lines, name='get_pharmacy_order_lines'),
     # Historique des commandes pour un produit pharmaceutique (JSON)
    path('products/<int:pk>/order-history/', views.pharmacy_product_order_history, name='pharmacy_product_order_history'),
    
    # Historique des commandes pour un produit pharmaceutique (PDF)
    path('products/<int:pk>/order-history/pdf/', views.pharmacy_product_order_history_pdf, name='pharmacy_product_order_history_pdf'),
    
    # Historique des commandes pour un fournisseur pharmaceutique (JSON)
    path('suppliers/<int:pk>/order-history/', views.pharmacy_supplier_order_history, name='pharmacy_supplier_order_history'),
    
    # Historique des commandes pour un fournisseur pharmaceutique (PDF)
    path('suppliers/<int:pk>/order-history/pdf/', views.pharmacy_supplier_order_history_pdf, name='pharmacy_supplier_order_history_pdf'),

    path('', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('dashboard/orders-evolution/', views.pharmacy_orders_evolution, name='pharmacy_orders_evolution'),
    path('dashboard/orders-by-state/', views.pharmacy_orders_by_state, name='pharmacy_orders_by_state'),
    path('dashboard/orders/filtered/', views.pharmacy_order_list_filtered, name='pharmacy_order_list_filtered'),

]





   