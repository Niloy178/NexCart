from .models import Cart, CartItem
from .views import _cart_id

def counter(req):
    count=0
    if('admin' in req.path):
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(req))
            cart_items=CartItem.objects.all().filter(cart=cart[:1])
            for item in cart_items:
                count+=item.quantity
        except Cart.DoesNotExist:
                count=0
    return dict(cart_count=count)
