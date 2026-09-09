from urllib.parse import quote
from django.conf import settings

def get_whatsapp_number():
    """Returns configured WhatsApp business number from settings or default."""
    return getattr(settings, 'WHATSAPP_NUMBER', '919778256391')


def generate_product_whatsapp_url(product):
    """
    Generates a WhatsApp click-to-chat URL with pre-filled message for a product.
    Format: https://wa.me/<BUSINESS_NUMBER>?text=<ENCODED_MESSAGE>
    """
    number = get_whatsapp_number()
    raw_message = (
        f"Hello, I am interested in the {product.name}.\n\n"
        f"Product: {product.name}\n"
        f"Price: ₹{product.price}\n\n"
        f"I would like to know more about this product."
    )
    encoded_message = quote(raw_message)
    return f"https://wa.me/{number}?text={encoded_message}"

def generate_enquiry_whatsapp_url(enquiry):
    """
    Generates a WhatsApp click-to-chat URL for an submitted customer enquiry.
    """
    number = get_whatsapp_number()
    product_str = enquiry.product.name if enquiry.product else "General Product Enquiry"
    raw_message = (
        f"Hello, I would like to enquire about your product.\n\n"
        f"Name: {enquiry.name}\n"
        f"Phone: {enquiry.phone}\n"
        f"Product: {product_str}\n\n"
        f"Message:\n{enquiry.message}"
    )
    encoded_message = quote(raw_message)
    return f"https://wa.me/{number}?text={encoded_message}"
