from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
import logging
import datetime
from .utils import cookieCart,cartData,guestOrder
# Create your views here.
logger = logging.getLogger(__name__)

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)
@api_view(http_method_names=['POST'])
def updateItem(request):
    
    data = request.data
    print(data)
    productID = data['productId']
    
    action = data['action']
    print('Action:',action)
    print('Product:',productID)
    
    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity+1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity-1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
@api_view(http_method_names=['POST'])
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = request.data
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        
    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Payment Complete!',safe=False)