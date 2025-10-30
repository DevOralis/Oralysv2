from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('products/export/', views.product_export, name='product_export'),
    path('products/ajax/', views.product_list_ajax, name='product_list_ajax'),

    #Inventory URls
    path('products/list/', views.inventory_list, name='inventory_list'),
    path('products/list/json/', views.inventory_list_json, name='inventory_list_json'),  
    path('products/list/pdf/', views.inventory_pdf, name='inventory_pdf'),  
    path('valuation/', views.valuation_list, name='valuation_list'),
    path('valuation/json/', views.valuation_list_json, name='valuation_list_json'),
    path('valuation/pdf/', views.valuation_pdf, name='valuation_pdf'),
    path('adjustment/', views.inventory_adjustment, name='inventory_adjustment'),
    path('adjustment/pdf/', views.inventory_adjustment_pdf, name='inventory_adjustment_pdf'),

    # Configuration URL
    path('configuration/', views.configuration, name='configuration'),

    # Statistics URL
    path('statistics/', views.inventory_statistics, name='inventory_statistics'),

    # UOM
    path('uom/add/', views.uom_create, name='uom_add'),
    path('uom/<int:pk>/edit/', views.uom_update, name='uom_edit'),
    path('uom/<int:pk>/delete/', views.uom_delete, name='uom_delete'),
    path('uom/search/', views.uom_search, name='uom_search'),

    # Catégorie
    path('category/add/', views.category_create, name='category_add'),
    path('category/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('category/search/', views.category_search, name='category_search'),

    # Product Type URLs
    path('product_type/add/', views.product_type_create, name='product_type_add'),
    path('product_type/<int:pk>/edit/', views.product_type_update, name='product_type_edit'),
    path('product_type/<int:pk>/delete/', views.product_type_delete, name='product_type_delete'),
    path('product_type/search/', views.product_type_search, name='product_type_search'),   

    # Operation Type URLs
    path('operation_type/add/', views.operation_type_create, name='operation_type_add'),
    path('operation_type/<int:pk>/edit/', views.operation_type_update, name='operation_type_edit'),
    path('operation_type/<int:pk>/delete/', views.operation_type_delete, name='operation_type_delete'),
    path('operation_type/search/', views.operation_type_search, name='operation_type_search'),    

    # Location Type URLs
    path('location_type/add/', views.location_type_create, name='location_type_add'),
    path('location_type/<int:pk>/edit/', views.location_type_update, name='location_type_edit'),
    path('location_type/<int:pk>/delete/', views.location_type_delete, name='location_type_delete'),
    path('location_type/list/json/', views.location_type_list_json, name='location_type_list_json'),
    path('location_type/search/', views.location_type_search, name='location_type_search'),

    # Location (Emplacement) -- 
    path('location/add/', views.location_create, name='location_add'),
    path('location/<int:pk>/edit/', views.location_update, name='location_edit'),
    path('location/<int:pk>/delete/', views.location_delete, name='location_delete'),
    path('location/search/', views.location_search, name='location_search'),

    # ProductLocation
    path('product-locations/',              views.product_location_list,   name='product_location_list'),
    path('product-locations/add/',          views.product_location_create, name='product_location_add'),
    path('product-locations/<int:pk>/edit/',views.product_location_update, name='product_location_edit'),
    path('product-locations/<int:pk>/delete/', views.product_location_delete, name='product_location_delete'),

    # Stock Move URLs
    path('stock-moves/', views.stock_move_list, name='stock_move_list'),
    path('stock-moves/create/', views.stock_move_create, name='stock_move_create'),
    path('stock-moves/<int:pk>/edit/', views.stock_move_update, name='stock_move_update'),
    path('stock-moves/<int:pk>/delete/', views.stock_move_delete, name='stock_move_delete'), 
    path('stock-moves/pdf/', views.stock_move_pdf, name='stock_move_pdf'),
    path('stock-moves/<int:pk>/json/', views.stock_move_detail_json, name='stock_move_detail_json'),
    path('stock-moves/<int:pk>/delivery-pdf/', views.stock_move_delivery_pdf, name='stock_move_delivery_pdf'),

    path('api/purchase_orders', views.get_supplier_orders, name='api_supplier_orders'),
    path('api/purchase_order_lines', views.get_order_lines, name='api_order_lines'),

    
]