from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Enquiry, CATEGORY_CHOICES
from .forms import EnquiryForm
from .utils import generate_product_whatsapp_url, generate_enquiry_whatsapp_url, get_whatsapp_number

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

    # Handle Enquiry Form submission on homepage
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
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
            enquiry = form.save()
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
