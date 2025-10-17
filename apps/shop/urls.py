from django.urls import path

from apps.shop import views



urlpatterns = [
    path('search/', views.SearchResultView.as_view(), name='search_result'),

    path('product/<slug:slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('product/', views.ProductListView.as_view(), name='product_list'),

    path('product_detail/<slug:slug>', views.ProductDetailView.as_view(), name='product_detail'),


    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('', views.IndexView.as_view(), name='index'),
]
