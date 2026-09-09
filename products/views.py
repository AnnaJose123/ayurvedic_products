from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Product, Enquiry, CATEGORY_CHOICES, CartItem
from .forms import EnquiryForm, CustomerRegistrationForm, CustomerLoginForm
from .utils import (
    generate_product_whatsapp_url,
    generate_enquiry_whatsapp_url,
    generate_cart_whatsapp_url,
    get_whatsapp_number
)
from .cart import Cart


def home_view(request):
    """
    Renders the main homepage featuring Hero, About, Products showcase,
    Why Choose Us, Enquiry Form, Contact section, and Footer.
    """
    category_filter = request.GET.get('category', '').strip()
    
    # Retrieve products dynamically using Django ORM
    products = Product.objects.filter(is_available=True)
    if category_filter and category_filter != 'All':
        products = products.filter(category=category_filter)

    # Attach dynamic WhatsApp click-to-chat link for each product
    for product in products:
        product.whatsapp_url = generate_product_whatsapp_url(product)

    # Pre-select product in form if query parameter 'enquire_product' is present
    initial_data = {}
    enquire_product_id = request.GET.get('enquire_product')
    if enquire_product_id:
        try:
            initial_data['product'] = int(enquire_product_id)
        except ValueError:
            pass

    # Pre-fill user name if logged in
    if request.user.is_authenticated:
        initial_data['name'] = request.user.get_full_name() or request.user.username

    # Handle Enquiry Form submission on homepage
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()
            messages.success(request, "Thank you! Your enquiry has been submitted successfully. We will contact you soon.")
            return redirect('enquiry_success', enquiry_id=enquiry.id)
        else:
            messages.error(request, "There was an issue with your submission. Please check the errors below.")
    else:
        form = EnquiryForm(initial=initial_data)

    categories = ['All'] + [choice[0] for choice in CATEGORY_CHOICES]

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_filter if category_filter else 'All',
        'form': form,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/home.html', context)


def product_detail_view(request, slug):
    """
    Renders detailed information page for a specific product.
    URL: /products/<slug>/
    """
    product = get_object_or_404(Product, slug=slug, is_available=True)
    product.whatsapp_url = generate_product_whatsapp_url(product)

    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:3]
    
    for rel in related_products:
        rel.whatsapp_url = generate_product_whatsapp_url(rel)

    context = {
        'product': product,
        'related_products': related_products,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/product_detail.html', context)


def enquiry_view(request):
    """
    Standalone view for enquiry form processing.
    Redirects to homepage #enquiry section or enquiry success page.
    """
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()
            messages.success(request, "Thank you! Your enquiry has been submitted successfully.")
            return redirect('enquiry_success', enquiry_id=enquiry.id)
    return redirect('/#enquiry')


def enquiry_success_view(request, enquiry_id):
    """
    Renders confirmation page after successful customer enquiry submission.
    Provides direct option to open pre-filled WhatsApp message.
    """
    enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
    whatsapp_url = generate_enquiry_whatsapp_url(enquiry)

    context = {
        'enquiry': enquiry,
        'whatsapp_url': whatsapp_url,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/enquiry_success.html', context)


def register_view(request):
    """
    Customer Registration View (`/register/`).
    Registers new customer account and logs them in automatically.
    """
    if request.user.is_authenticated:
        return redirect('my_enquiries')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            cart = Cart(request)
            cart.merge_on_login(user)
            messages.success(request, f"Welcome to HerbaCare, {user.first_name or user.username}! Account created successfully.")
            return redirect('my_enquiries')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = CustomerRegistrationForm()

    context = {
        'form': form,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/register.html', context)


def login_view(request):
    """
    Customer Login View (`/login/`).
    Authenticates existing customer account and restores saved shopping cart.
    """
    if request.user.is_authenticated:
        return redirect('my_enquiries')

    redirect_to = request.GET.get('next', 'my_enquiries')

    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            cart = Cart(request)
            cart.merge_on_login(user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(redirect_to)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomerLoginForm(request)

    context = {
        'form': form,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/login.html', context)


def logout_view(request):
    """
    Customer Logout View (`/logout/`).
    Saves cart items to DB before logging out session.
    """
    if request.user.is_authenticated:
        cart = Cart(request)
        cart._sync_to_db()
    logout(request)
    messages.info(request, "You have been logged out successfully. Visit us again!")
    return redirect('home')


@login_required(login_url='login')
def my_enquiries_view(request):
    """
    Customer Dashboard (`/my-enquiries/`).
    Lists all product enquiries submitted by the logged-in user.
    """
    enquiries = Enquiry.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    
    # Attach WhatsApp URLs to each enquiry for convenient customer action
    for enquiry in enquiries:
        enquiry.whatsapp_url = generate_enquiry_whatsapp_url(enquiry)

    context = {
        'enquiries': enquiries,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/my_enquiries.html', context)


# --------------------------------------------------------------------------
# SHOPPING CART VIEWS
# --------------------------------------------------------------------------

def cart_detail_view(request):
    """
    Renders Shopping Cart page (`/cart/`) with items list and total order sum.
    """
    cart = Cart(request)
    whatsapp_checkout_url = generate_cart_whatsapp_url(
        cart,
        customer_name=request.user.get_full_name() or request.user.username if request.user.is_authenticated else None
    )

    context = {
        'cart': cart,
        'whatsapp_checkout_url': whatsapp_checkout_url,
        'whatsapp_number': get_whatsapp_number(),
    }
    return render(request, 'products/cart.html', context)


def cart_add_view(request, product_id):
    """
    Adds a product to the shopping cart.
    Accepts quantity parameter via POST or GET (default 1).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added '{product.name}' (x{quantity}) to your shopping cart!")
    
    # Redirect back to referring page or cart
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'cart_detail'
    return redirect(next_url)


def cart_remove_view(request, product_id):
    """
    Removes a product from the shopping cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed '{product.name}' from your cart.")
    return redirect('cart_detail')


def cart_update_view(request, product_id):
    """
    Updates the quantity of a product in the shopping cart directly.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f"Removed '{product.name}' from your cart.")
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f"Updated quantity for '{product.name}' to {quantity}.")

    return redirect('cart_detail')


def cart_checkout_whatsapp_view(request):
    """
    Generates itemized order details and redirects to WhatsApp click-to-chat.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your shopping cart is empty.")
        return redirect('cart_detail')

    customer_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else None
    whatsapp_url = generate_cart_whatsapp_url(cart, customer_name=customer_name)
    return redirect(whatsapp_url)


def cart_checkout_enquiry_view(request):
    """
    Converts all items in the cart into a customer enquiry log and clears the cart.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your shopping cart is empty.")
        return redirect('cart_detail')

    # Build summary message of all cart items
    items_summary = []
    for item in cart:
        items_summary.append(f"• {item['product'].name} (x{item['quantity']}) - ₹{item['total_price']:.2f}")

    message_text = "Bulk Order Request from Cart:\n" + "\n".join(items_summary) + f"\n\nTotal Sum: ₹{cart.get_total_price():.2f}"

    # Pick first product as main interested product reference if available
    first_item = list(cart)[0]
    main_product = first_item['product']

    cust_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else "Shopping Customer"

    enquiry = Enquiry.objects.create(
        user=request.user if request.user.is_authenticated else None,
        name=cust_name,
        phone=request.user.email if (request.user.is_authenticated and request.user.email) else "Provided via Checkout",
        product=main_product,
        message=message_text
    )

    cart.clear()
    messages.success(request, "Your cart order request has been logged as an official enquiry! We will reach out to you shortly.")
    return redirect('enquiry_success', enquiry_id=enquiry.id)
