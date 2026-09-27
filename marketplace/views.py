from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import Category, Product, ProductImage, Favorite, ContactMessage, Profile
from .forms import (
    UserRegisterForm, UserLoginForm, ProductForm, 
    ProfileUpdateForm, ContactMessageForm, SupportContactForm
)


def home_view(request):
    """Homepage: Hero section, Categories, Featured Listings, Features, How It Works."""
    categories = Category.objects.annotate(
        active_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('name')

    featured_products = Product.objects.filter(is_active=True).select_related(
        'category', 'seller', 'seller__profile'
    ).order_by('-created_at')[:8]

    # Marketplace quick stats for Hero / Community banner
    stats = {
        'total_listings': Product.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
    }

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'stats': stats,
    }
    return render(request, 'marketplace/home.html', context)


def browse_products_view(request):
    """
    Search and Filter products:
    - Keywords (title, description, location)
    - Category slug
    - Condition
    - Price range (min_price, max_price)
    - Location
    - Sorting (newest, price_asc, price_desc, popular)
    - Pagination (12 per page)
    """
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'seller', 'seller__profile'
    )

    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    condition = request.GET.get('condition', '').strip()
    location = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    # Keyword search
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Condition filter
    if condition:
        products = products.filter(condition=condition)

    # Location filter
    if location:
        products = products.filter(location__icontains=location)

    # Price range filter
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views', '-created_at')
    else:
        # Default: newest
        products = products.order_by('-created_at')

    # Total result count
    total_count = products.count()

    # Pagination: 12 items per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Retain active query parameters for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    categories = Category.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': total_count,
        'query': query,
        'category_slug': category_slug,
        'selected_category': selected_category,
        'condition': condition,
        'location': location,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'categories': categories,
        'condition_choices': Product.CONDITION_CHOICES,
        'query_string': query_string,
    }
    return render(request, 'marketplace/products.html', context)


def category_products_view(request, slug):
    """Direct route for category items."""
    category = get_object_or_404(Category, slug=slug)
    # Redirect to browse with category query
    url = f"{reverse('marketplace:products')}?category={slug}"
    return redirect(url)


def product_detail_view(request, pk):
    """Product Detail: image gallery, seller info, inquiry message form, similar items."""
    product = get_object_or_404(
        Product.objects.select_related('category', 'seller', 'seller__profile'),
        pk=pk
    )

    # Increment view count (simple count on get)
    session_key = f'viewed_product_{product.pk}'
    if not request.session.get(session_key):
        product.views += 1
        product.save(update_fields=['views'])
        request.session[session_key] = True

    # Check if favorited by logged-in user
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()

    # Seller metrics
    seller_listings_count = Product.objects.filter(seller=product.seller, is_active=True).count()

    # Similar listings in same category (excluding current)
    similar_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk).select_related('seller', 'seller__profile')[:4]

    # Handle inquiry contact form
    contact_form = ContactMessageForm()
    if request.method == 'POST' and request.user.is_authenticated:
        if request.user == product.seller:
            messages.warning(request, "You cannot send inquiries to your own listing.")
            return redirect('marketplace:product_detail', pk=product.pk)

        contact_form = ContactMessageForm(request.POST)
        if contact_form.is_valid():
            inquiry = contact_form.save(commit=False)
            inquiry.sender = request.user
            inquiry.receiver = product.seller
            inquiry.product = product
            inquiry.save()
            messages.success(request, f"Your inquiry has been sent to {product.seller.username}!")
            return redirect('marketplace:product_detail', pk=product.pk)

    context = {
        'product': product,
        'is_favorited': is_favorited,
        'seller_listings_count': seller_listings_count,
        'similar_products': similar_products,
        'contact_form': contact_form,
        'additional_images': product.additional_images.all(),
    }
    return render(request, 'marketplace/product_detail.html', context)


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    """Toggle a product in user favorites (works for AJAX and standard POST)."""
    product = get_object_or_404(Product, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        is_favorited = False
        msg = f"Removed '{product.title}' from your favorites."
    else:
        is_favorited = True
        msg = f"Added '{product.title}' to your favorites."

    # Return JSON for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        favorites_count = Favorite.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': msg,
            'total_favorites': favorites_count,
        })

    messages.info(request, msg)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('marketplace:product_detail', kwargs={'pk': pk})
    return redirect(next_url)


@login_required
def create_listing_view(request):
    """Create a new marketplace listing."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            # Handle optional additional gallery images
            extra_images = request.FILES.getlist('additional_images')
            for img in extra_images[:5]:  # Limit to 5 extra photos
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f"Listing '{product.title}' created successfully!")
            return redirect('marketplace:product_detail', pk=product.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        initial_data = {}
        if hasattr(request.user, 'profile') and request.user.profile.phone:
            initial_data['contact_phone'] = request.user.profile.phone
        if hasattr(request.user, 'profile') and request.user.profile.location:
            initial_data['location'] = request.user.profile.location
        form = ProductForm(initial=initial_data)

    return render(request, 'marketplace/create_listing.html', {'form': form})


@login_required
def edit_listing_view(request, pk):
    """Edit existing listing (ownership verified)."""
    product = get_object_or_404(Product, pk=pk)

    # Ownership check
    if product.seller != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this listing.")
        return redirect('marketplace:my_listings')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle optional extra images uploaded during edit
            extra_images = request.FILES.getlist('additional_images')
            for img in extra_images[:5]:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f"Listing '{product.title}' updated successfully.")
            return redirect('marketplace:product_detail', pk=product.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'additional_images': product.additional_images.all(),
    }
    return render(request, 'marketplace/edit_listing.html', context)


@login_required
@require_POST
def delete_listing_view(request, pk):
    """Delete a listing (ownership verified)."""
    product = get_object_or_404(Product, pk=pk)

    if product.seller != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this listing.")
        return redirect('marketplace:my_listings')

    title = product.title
    product.delete()
    messages.success(request, f"Listing '{title}' deleted successfully.")
    return redirect('marketplace:my_listings')


@login_required
@require_POST
def toggle_listing_status_view(request, pk):
    """Toggle listing between Active and Sold/Inactive."""
    product = get_object_or_404(Product, pk=pk)
    if product.seller != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Not authorized")

    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])

    status_str = "Active" if product.is_active else "Inactive (Marked as Sold)"
    messages.success(request, f"Listing status changed to {status_str}.")
    return redirect('marketplace:my_listings')


@login_required
def my_listings_view(request):
    """View all listings belonging to logged-in user with filter tabs."""
    status_filter = request.GET.get('status', 'all')
    user_products = Product.objects.filter(seller=request.user)

    if status_filter == 'active':
        user_products = user_products.filter(is_active=True)
    elif status_filter == 'inactive':
        user_products = user_products.filter(is_active=False)

    user_products = user_products.order_by('-created_at')

    # Counts
    total_count = Product.objects.filter(seller=request.user).count()
    active_count = Product.objects.filter(seller=request.user, is_active=True).count()
    inactive_count = total_count - active_count

    context = {
        'products': user_products,
        'status_filter': status_filter,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }
    return render(request, 'marketplace/my_listings.html', context)


@login_required
def favorites_view(request):
    """View all products saved by the user."""
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'product', 'product__category', 'product__seller'
    ).order_by('-created_at')

    context = {
        'favorites': favorites,
        'favorites_count': favorites.count(),
    }
    return render(request, 'marketplace/favorites.html', context)


@login_required
def dashboard_view(request):
    """User Dashboard showing statistics, recent listings, favorites, inquiries."""
    user = request.user

    my_listings = Product.objects.filter(seller=user)
    total_listings = my_listings.count()
    active_listings = my_listings.filter(is_active=True).count()
    total_views = my_listings.aggregate(Sum('views'))['views__sum'] or 0
    favorites_count = Favorite.objects.filter(user=user).count()

    recent_listings = my_listings.order_by('-created_at')[:5]
    recent_favorites = Favorite.objects.filter(user=user).select_related(
        'product', 'product__category'
    ).order_by('-created_at')[:4]

    received_messages = ContactMessage.objects.filter(receiver=user).select_related(
        'sender', 'product'
    ).order_by('-created_at')[:5]

    context = {
        'total_listings': total_listings,
        'active_listings': active_listings,
        'total_views': total_views,
        'favorites_count': favorites_count,
        'recent_listings': recent_listings,
        'recent_favorites': recent_favorites,
        'received_messages': received_messages,
    }
    return render(request, 'marketplace/dashboard.html', context)


@login_required
def profile_view(request):
    """User profile management and info update."""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            # Update user model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('marketplace:profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    user_listings = Product.objects.filter(seller=request.user).order_by('-created_at')[:6]

    context = {
        'form': form,
        'profile': profile,
        'user_listings': user_listings,
    }
    return render(request, 'marketplace/profile.html', context)


def seller_profile_view(request, username):
    """Public seller page showing bio, verified badge, join date, listings."""
    seller = get_object_or_404(User.objects.select_related('profile'), username=username)
    seller_listings = Product.objects.filter(seller=seller, is_active=True).order_by('-created_at')

    context = {
        'seller': seller,
        'listings': seller_listings,
        'listings_count': seller_listings.count(),
    }
    return render(request, 'marketplace/seller_profile.html', context)


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MarketNest, {user.first_name or user.username}! Your account has been created.")
            return redirect('marketplace:dashboard')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = UserRegisterForm()

    return render(request, 'marketplace/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or reverse('marketplace:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'marketplace/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect('marketplace:home')


def about_view(request):
    """About MarketNest page."""
    return render(request, 'marketplace/about.html')


def contact_view(request):
    """Contact page with general inquiry form."""
    if request.method == 'POST':
        form = SupportContactForm(request.POST)
        if form.is_valid():
            messages.success(
                request, 
                "Thank you for contacting MarketNest! Our community support team will respond within 24 hours."
            )
            return redirect('marketplace:contact')
    else:
        form = SupportContactForm()

    return render(request, 'marketplace/contact.html', {'form': form})


def custom_404_view(request, exception=None):
    """Custom 404 page."""
    return render(request, 'marketplace/404.html', status=404)


def custom_500_view(request):
    """Custom 500 error page."""
    return render(request, 'marketplace/500.html', status=500)
