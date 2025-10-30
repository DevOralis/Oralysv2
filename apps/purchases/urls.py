from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('suppliers/purchases_configuration/', views.purchases_configuration, name='purchases_configuration'),
    path('suppliers/<int:pk>/order-history/', views.supplier_order_history, name='supplier_order_history'),
    path('suppliers/<int:pk>/order-history/pdf/', views.supplier_order_history_pdf, name='supplier_order_history_pdf'),
    path('suppliers/filtered/', views.supplier_list_filtered, name='supplier_list_filtered'),




    # Country
    path('countries/', views.country_list, name='country_list'),
    path('countries/create/', views.country_create, name='country_create'),
    path('countries/delete/<int:pk>/', views.country_delete, name='country_delete'),

    # City
    path('cities/', views.city_list, name='city_list'),
    path('cities/create/', views.city_create, name='city_create'),
    path('cities/delete/<int:pk>/', views.city_delete, name='city_delete'),

    # Language
    path('languages/', views.language_list, name='language_list'),
    path('languages/create/', views.language_create, name='language_create'),
    path('languages/delete/<int:pk>/', views.language_delete, name='language_delete'),
    path('countries/delete/<int:pk>/', views.country_delete, name='country_delete'),
    path('cities/delete/<int:pk>/', views.city_delete, name='city_delete'),
    path('languages/delete/<int:pk>/', views.language_delete, name='language_delete'),
    
    # Tax
    path('taxes/', views.tax_list, name='tax_list'),
    path('taxes/create/', views.tax_create, name='tax_create'),
    path('taxes/delete/<int:pk>/', views.tax_delete, name='tax_delete'),


    path('currencies/', views.list_currencies, name='currency_list'),
    path('currencies/create/', views.create_currency, name='currency_create'),
    path('currencies/delete/<int:pk>/', views.delete_currency, name='currency_delete'),
    
    path('orders/', views.purchase_order_list, name='order_list'),
    path('orders/create/', views.create_purchase_order, name='order_create'),
    path('orders/delete/<int:pk>/', views.delete_purchase_order, name='order_delete'),
    path('orders/detail-json/<int:order_id>/', views.order_detail_json, name='order_detail_json'),
    path('orders/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('orders/filter/', views.order_list_filtered, name='order_list_filtered'),
    path('orders/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('orders/line/delete/<int:line_id>/', views.delete_order_line, name='delete_order_line'),
    path('order/<int:order_id>/pdf/', views.generate_order_c, name='generate_order_pdf'),  
    path('orders/request-price/<int:order_id>/pdf/', views.generate_price_request_pdf, name='generate_price_request_pdf'),  
    path('configuration/payment-mode/add/', views.add_payment_mode, name='add_payment_mode'),
    path('payment-modes/delete/<int:id>/', views.delete_payment_mode, name='delete_payment_mode'),
    path('orders/filter/', views.order_list_filtered, name='order_list_filtered'),  # Assurez-vous que cette vue existe
    path('orders/duplicate/<int:order_id>/', views.duplicate_order, name='duplicate_order'),
    
    path('configuration/type-convention/add/', views.purchases_configuration, name='add_convention_type'),
    path('convention-types/delete/<int:id>/', views.delete_convention_type, name='delete_convention_type'),
    path('conventions/', views.convention_list, name='convention_list'),
    path('conventions/create/', views.create_convention, name='convention_create'),
    path('conventions/delete/<int:pk>/', views.delete_convention, name='convention_delete'),
    path('conventions/detail-json/<int:convention_id>/', views.convention_detail_json, name='convention_detail_json'),
    path('conventions/confirm/<int:convention_id>/', views.confirm_convention, name='confirm_convention'),
    path('conventions/filter/', views.convention_list_filtered, name='convention_list_filtered'),
    path('conventions/edit/<int:convention_id>/', views.edit_convention, name='edit_convention'),
    path('conventions/line/delete/<int:line_id>/', views.delete_convention_line, name='delete_convention_line'),
    path('conventions/<int:convention_id>/pdf/', views.generate_convention_pdf, name='generate_convention_pdf'),
    path('conventions/duplicate/<int:convention_id>/', views.duplicate_convention, name='duplicate_convention'),
    # Dans votre urls.py, ajoutez cette ligne :
    path('conventions/detail-json/<int:convention_id>/', views.convention_detail_json, name='convention_detail_json'),
    path('products/', views.purchases_product_list, name='purchases_product_list'),
    path('products/create/', views.purchases_product_create, name='purchases_product_create'),
    path('products/<int:pk>/update/', views.purchases_product_update, name='purchases_product_update'),
    path('products/<int:pk>/delete/', views.purchases_product_delete, name='purchases_product_delete'),
    path('products/<int:pk>/order-history/', views.product_order_history, name='product_order_history'),
    path('products/<int:pk>/order-history/pdf/', views.product_order_history_pdf, name='product_order_history_pdf'),
    path('', views.purchases_dashboard, name='purchases_dashboard'),
    path('orders_by_state/', views.orders_by_state, name='orders_by_state'),
    path('orders_evolution/', views.orders_evolution, name='orders_evolution'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
