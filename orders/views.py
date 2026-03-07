from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
import json
from store.views import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# Create your views here.


def place_order(req, total=0, quantity=0):
    
    current_user = req.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    # If cart item is 0, then redirect to store
    if cart_count<=0:
        return redirect('store')
    
    
    grand_total = 0
    tax=0
    
    
    for cart_item in cart_items:
        total+=(cart_item.product.price * cart_item.quantity)
        quantity+=cart_item.quantity
    tax=(2*total)/100
    grand_total=total+tax
    
    
    if req.method=='POST':
        form = OrderForm(req.POST)
        
        if form.is_valid():
            
            # Store all the billing information inside order table
            
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = req.META.get('REMOTE_ADDR')
            
            data.save()
            
            # # Generate Order number
            
            yr= int(datetime.date.today().strftime('%Y'))
            dt= int(datetime.date.today().strftime('%d'))
            mt= int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date+str(data.id)
            
            data.order_number = order_number
            data.save()
            
            # Sending Order and cart_items in checkout page
            order = Order.objects.get(user=current_user, is_ordered=False, order_number = order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(req, 'orders/payment.html', context)
    else:
        return redirect('checkout')
    


def payments(req):
    
    if req.method == 'POST':
        body = json.loads(req.body)     
        
        order = Order.objects.get(user=req.user, is_ordered=False, order_number=body['order_id'])
        payment = Payment(
            user = req.user,
            payment_id=body['trans_id'],
            payment_method=body['payment_method'],
            amount_paid=order.order_total,
            status=body['status'],            
        )
        payment.save()
        
        order.payment=payment
        order.is_ordered=True
        order.save()
        
        # Move the cart items to Order product table
        cart_items = CartItem.objects.filter(user=req.user)
        for cart_item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = order.user.id
            order_product.product_id = cart_item.product_id
            order_product.quantity = cart_item.quantity
            order_product.product_price = cart_item.product.price
            order_product.ordered = True
            order_product.save()
            
            cart_item = CartItem.objects.get(id=cart_item.id)
            product_variation = cart_item.variations.all()
            order_product=OrderProduct.objects.get(id=order_product.id)
            order_product.variations.set(product_variation)
            order_product.save()
        
            # Reduce the quantity of the sold product 
            product = Product.objects.get(id=cart_item.product_id)
            product.stock-=cart_item.quantity
            product.save()

        
        # clear cart
        CartItem.objects.filter(user=req.user).delete()
        
        # Send order details mail to the user
        
        # mail_subject = "Please activate your account."
        # message = render_to_string("orders/recieved_email.html", {
        #     'user': req.user,
        #     'order': order
        # })
        # to_email = req.user.email  
        # send_email = EmailMessage(mail_subject, message, to=[to_email])
        # send_email.send()
                    
        # Send order number and transaction id back to Send data method via JSONResponse 
        data = {
            'order_number': order.order_number,
            'trans_id': payment.payment_id,
        }
        
        return JsonResponse(data)
    
    return render(req, 'orders/payment.html')

def order_complete(req):
    order_number = req.GET.get('order_number')
    trans_id = req.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id )
        payment = Payment.objects.get(payment_id=trans_id)
        
        sub_total = 0 
        for i in ordered_products:
            sub_total+=i.product_price*i.quantity
            
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'trans_id': payment.payment_id,
            'payment': payment,
            'subtotal': sub_total,
        }
    
        return render(req, 'orders/order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        
        pass 