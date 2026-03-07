from django.contrib import admin
from .models import Payment, Order, OrderProduct

# ModelsAdmin
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra=0
    readonly_fields=('payment',  'user', 'product', 'quantity', 'product_price', 'ordered')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    inlines = [OrderProductInline]
# Register your models here.

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
