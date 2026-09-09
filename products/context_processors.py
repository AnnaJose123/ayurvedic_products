from .cart import Cart

def cart_context(request):
    """Context processor exposing cart to all templates."""
    return {'cart': Cart(request)}
