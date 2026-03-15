from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q
from .models import ReviewRatings
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


# Create your views here.

def search(req):

    if 'keyword' in req.GET:
        keyword = req.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword), is_available=True)
            count=products.count()
            context={
                'per_page_products': products,
                'count': count,
            }
            return render(req, 'store/store.html', context)
        else:
            return render(req, 'store/store.html')

    

def store(req, category_slug=None):
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
    
    count = products.count() # This is for showing the 
    paginator = Paginator(products, 1)
    page_number = req.GET.get('page')
    per_page_products = paginator.get_page(page_number)

    context = {
        'products': products,
        'count': count,
        'per_page_products': per_page_products,
        }
    return render(req, 'store/store.html', context)




def product_details(req, category_slug, product_slug):
    # product = get_object_or_404(Product, slug=product_slug)

    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        is_added = CartItem.objects.filter(cart__cart_id=_cart_id(req), product=product).exists()
    except Exception as e:
        raise e     
    
    if (req.user.id):
        try: 
            order_product = OrderProduct.objects.filter(user=req.user, product_id = product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product=None
    else:
        order_product=None
        
    # Get the reviews
    reviews = ReviewRatings.objects.filter(product_id=product.id, status = True)
    
    context = {
        'product': product,
        'is_added': is_added,
        'order_product': order_product,
        'reviews': reviews,
    }
    return render(req, 'store/product_details.html', context)


def submit_review(req, product_id):
    url=req.META.get('HTTP_REFERER')
    print(url)
    if req.method=="POST":
        try:
            reviews = ReviewRatings.objects.get(user__id=req.user.id, product__id=product_id)
            form = ReviewForm(req.POST, instance=reviews)
            form.save()
            messages.success(req, "Thank you, your review has been updated.")
            return redirect(url)
        except ReviewRatings.DoesNotExist:
            form = ReviewForm(req.POST)
            if form.is_valid():
                data = ReviewRatings()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = req.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = req.user.id
                data.save()
                messages.success('Thank you, You review has been submitted.')
                return redirect('url')
                
             