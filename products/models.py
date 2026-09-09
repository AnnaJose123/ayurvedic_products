from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('Hair Care', 'Hair Care'),
    ('Skin Care', 'Skin Care'),
    ('Body Care', 'Body Care'),
    ('Herbal Care', 'Herbal Care'),
]

class Product(models.Model):
    name = models.CharField(max_length=200, help_text="Product name e.g. Herbal Hair Oil")
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text="URL friendly identifier")
    description = models.TextField(help_text="Detailed product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR (₹)")
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Product showcase image")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Hair Care')
    is_available = models.BooleanField(default=True, help_text="Designate if product is currently available for ordering")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} (₹{self.price:.2f})"


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Enquiry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries',
        verbose_name="Registered Customer Account"
    )
    name = models.CharField(max_length=150, verbose_name="Customer Name")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries',
        verbose_name="Interested Product"
    )
    message = models.TextField(verbose_name="Enquiry Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted On")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Enquiry"
        verbose_name_plural = "Customer Enquiries"

    def __str__(self):
        product_name = self.product.name if self.product else "General Enquiry"
        return f"Enquiry by {self.name} for {product_name} - {self.created_at.strftime('%b %d, %Y')}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} - {self.product.name} (x{self.quantity})"

