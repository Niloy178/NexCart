from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def _cart_id(req):
    cart_id = req.session.session_key
    
    if not cart_id:
        cart_id = req.session.create()
    return cart_id





# Adding item into cart

# If the product is not available, we can raise it from here also.(Personal thoughts)
def add_cart(req, product_id):
    color = req.GET['color']
    size = req.GET['size']
    print(color, size)
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(req))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(req)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity+=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        cart_item.save()   
    return redirect('cart')


def cart(req, total=0, quantity=0, cart_items=None):
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(req))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total+=(cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity
        tax = (2*total)/100
        grand_total=total+tax
    except ObjectDoesNotExist:
        print('loop except') 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(req, 'store/cart.html', context)

def remove_cart(req, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(req))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def delete_cart(req, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(req))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')