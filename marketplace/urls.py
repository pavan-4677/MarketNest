from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main views
    path('', views.home_view, name='home'),
    path('browse/', views.browse_products_view, name='products'),
    path('category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('product/<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    
    # Listings management
    path('listing/new/', views.create_listing_view, name='create_listing'),
    path('listing/<int:pk>/edit/', views.edit_listing_view, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing_view, name='delete_listing'),
    path('listing/<int:pk>/toggle-status/', views.toggle_listing_status_view, name='toggle_listing_status'),
    path('my-listings/', views.my_listings_view, name='my_listings'),
    path('favorites/', views.favorites_view, name='favorites'),
    
    # User account & dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('seller/<str:username>/', views.seller_profile_view, name='seller_profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Static pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
