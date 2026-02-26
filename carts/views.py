from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
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
    product = Product.objects.get(id=product_id)
    product_variation = []
    if req.method == 'POST':
        for key in req.POST:
            value = req.POST[key]
            
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(req))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(req)
        )
        cart.save()
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing_variations -> database
        # current_variation -> variation
        # item_id -> database
        
        ex_var_list = []
        id=[]
        for item in cart_item:
            ex_var = item.variations.all()
            ex_var_list.append(list(ex_var))
            id.append(item.id)
        


        if product_variation in ex_var_list:
            # Increase the cart item quantity
            
            index = ex_var_list.index(product_variation)
            item_id=id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity+=1
            item.save()

        else:
            # Create new Cart item
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
            )

            if len(product_variation)>0:
            # cart_item.variations.clear()
                #for item in product_variation:
                cart_item.variations.add(*product_variation)
        # cart_item.quantity+=1
                cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1,
        )
        if len(product_variation)>0:
            cart_item.variations.clear()
            for item in product_variation:
                cart_item.variations.add(item)
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

def remove_cart(req, product_id, card_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(req))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart, id=card_item_id)
    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def delete_cart(req, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(req))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')