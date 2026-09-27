from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Product Category model."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        default='bi-grid',
        help_text='Bootstrap icon class name, e.g., bi-laptop, bi-car-front'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('marketplace:category_products', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Profile(models.Model):
    """Extended user profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=120, blank=True, default='City Center')
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_avatar_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        # Fallback to UI-Avatars service for consistent, beautiful initial avatars
        initials = (self.user.first_name[:1] + self.user.last_name[:1]) if (self.user.first_name and self.user.last_name) else self.user.username[:2]
        return f"https://ui-avatars.com/api/?name={initials}&background=0F766E&color=ffffff&size=128&bold=true"

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Product(models.Model):
    """Marketplace product listing model."""
    CONDITION_CHOICES = [
        ('NEW', 'Brand New'),
        ('LIKE_NEW', 'Like New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('USED', 'Used / Heavily Used'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='GOOD')
    location = models.CharField(max_length=120, help_text='City, Neighborhood or Area')
    contact_phone = models.CharField(
        max_length=25, 
        blank=True, 
        help_text='Direct phone or WhatsApp number for buyers to contact you'
    )
    image = models.ImageField(upload_to='products/', help_text='Primary display photo')
    is_active = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active']),
            models.Index(fields=['location']),
        ]

    def get_absolute_url(self):
        return reverse('marketplace:product_detail', kwargs={'pk': self.pk})

    def short_description(self):
        return (self.description[:100] + '...') if len(self.description) > 100 else self.description

    def condition_badge_class(self):
        badge_map = {
            'NEW': 'bg-success text-white',
            'LIKE_NEW': 'bg-teal text-white',
            'GOOD': 'bg-primary-subtle text-primary border border-primary-subtle',
            'FAIR': 'bg-warning-subtle text-warning-emphasis border border-warning-subtle',
            'USED': 'bg-secondary-subtle text-secondary-emphasis',
        }
        return badge_map.get(self.condition, 'bg-light text-dark')

    def display_phone(self):
        """Return the listing contact phone or fallback to seller profile phone."""
        if self.contact_phone:
            return self.contact_phone
        if hasattr(self.seller, 'profile') and self.seller.profile.phone:
            return self.seller.profile.phone
        return None

    def clean_phone_digits(self):
        """Return digits only for tel: and wa.me links."""
        phone = self.display_phone()
        if not phone:
            return ""
        digits = "".join(c for c in phone if c.isdigit())
        # If 10-digit Indian number without country code, prepend 91 for WhatsApp
        if len(digits) == 10:
            return "91" + digits
        return digits

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """Additional gallery images for product listing."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image for {self.product.title}"


class Favorite(models.Model):
    """User saved/favorited listings."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.product.title}"


class ContactMessage(models.Model):
    """Inquiry messages between buyers and sellers regarding a product."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inquiries')
    sender_phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} on {self.product.title}"
