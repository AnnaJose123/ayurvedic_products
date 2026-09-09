from decimal import Decimal
from .models import Product, CartItem

CART_SESSION_ID = 'session_cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = getattr(request, 'user', None)
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}

        # Auto-restore saved cart items from DB for logged-in user if session cart is currently empty
        if self.user and self.user.is_authenticated and not cart:
            db_items = CartItem.objects.filter(user=self.user).select_related('product')
            for db_item in db_items:
                cart[str(db_item.product.id)] = {
                    'quantity': db_item.quantity,
                    'price': str(db_item.product.price)
                }
            self.session.modified = True

        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = max(1, int(quantity))
        else:
            self.cart[product_id]['quantity'] += max(1, int(quantity))
        
        self.save()

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            if self.user and self.user.is_authenticated:
                CartItem.objects.filter(user=self.user, product=product).delete()

    def save(self):
        """Mark session as modified and sync DB for authenticated users."""
        self.session.modified = True
        if self.user and self.user.is_authenticated:
            self._sync_to_db()

    def _sync_to_db(self):
        """Persist current session cart to CartItem DB records for logged in user."""
        if not (self.user and self.user.is_authenticated):
            return
        for p_id, item_data in self.cart.items():
            try:
                product = Product.objects.get(id=int(p_id))
                CartItem.objects.update_or_create(
                    user=self.user,
                    product=product,
                    defaults={'quantity': item_data['quantity']}
                )
            except Product.DoesNotExist:
                pass

    def merge_on_login(self, user):
        """
        Merges guest session cart with database saved cart items for logging-in user,
        then populates the active session cart.
        """
        self.user = user
        if not (user and user.is_authenticated):
            return

        # 1. Pull existing DB cart items for user
        db_items = CartItem.objects.filter(user=user).select_related('product')
        
        # 2. Merge DB items into session cart
        for db_item in db_items:
            p_id = str(db_item.product.id)
            if p_id in self.cart:
                # Keep higher quantity or add guest quantity
                self.cart[p_id]['quantity'] = max(self.cart[p_id]['quantity'], db_item.quantity)
            else:
                self.cart[p_id] = {'quantity': db_item.quantity, 'price': str(db_item.product.price)}

        # 3. Save merged state back to session and DB
        self.save()

    def __iter__(self):
        """Iterate over items in the cart and fetch corresponding Product model objects."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = {k: v.copy() for k, v in self.cart.items()}

        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        """Count total items in cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Remove cart from session and database if authenticated."""
        if self.user and self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]
            self.save()

