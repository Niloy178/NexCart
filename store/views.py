from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
# Create your views here.
def store(req, category_slug=None):
    if category_slug != None:
        print(category_slug)
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
    
    count = products.count()
    context = {
        'products': products,
        'count': count
        }
    return render(req, 'store/store.html', context)