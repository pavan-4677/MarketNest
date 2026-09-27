from django.db.models import Count, Q
from .models import Category, Product, Favorite, ContactMessage

def global_marketplace_context(request):
    """Context processor providing common categories, stats, and favorite product IDs."""
    context = {}
    try:
        context['global_categories'] = Category.objects.annotate(
            active_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')

        if request.user.is_authenticated:
            context['user_favorite_ids'] = set(
                Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
            )
            context['user_unread_messages_count'] = ContactMessage.objects.filter(
                receiver=request.user, is_read=False
            ).count()
        else:
            context['user_favorite_ids'] = set()
            context['user_unread_messages_count'] = 0

        context['total_active_listings_count'] = Product.objects.filter(is_active=True).count()
    except Exception:
        # Fallback during initial migrations or empty DB
        context['global_categories'] = []
        context['user_favorite_ids'] = set()
        context['user_unread_messages_count'] = 0
        context['total_active_listings_count'] = 0

    return context
