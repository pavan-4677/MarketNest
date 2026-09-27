from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Category, Product, ProductImage, Favorite, ContactMessage, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_location')

    def get_location(self, instance):
        return instance.profile.location if hasattr(instance, 'profile') else '-'
    get_location.short_description = 'Location'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'get_product_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = 'Total Listings'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'seller', 'category', 'price', 
        'condition', 'location', 'contact_phone', 'is_active', 'views', 'created_at'
    )
    list_filter = ('is_active', 'category', 'condition', 'created_at')
    search_fields = ('title', 'description', 'location', 'contact_phone', 'seller__username', 'seller__email')
    list_editable = ('is_active', 'price')
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [ProductImageInline]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    actions = ['mark_as_active', 'mark_as_inactive']

    @admin.action(description='Mark selected listings as Active')
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} listings marked as active.")

    @admin.action(description='Mark selected listings as Inactive (Sold/Archived)')
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} listings marked as inactive.")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'created_at')
    search_fields = ('product__title',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__title')
    list_filter = ('created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'product', 'sender_phone', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'product__title', 'message')
    readonly_fields = ('created_at',)


# Custom Admin site header & title
admin.site.site_header = "MarketNest Administration"
admin.site.site_title = "MarketNest Admin Portal"
admin.site.index_title = "Welcome to MarketNest Marketplace Operations"
