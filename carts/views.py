from django.shortcuts import render, redirect,get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product=product, user=current_user)
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(product=product, quantity=1, user=current_user)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(product=product, quantity=1, cart=cart)
    return redirect('cart')
    
    
    # product = Product.objects.get(id = product_id)   # get the product
    # try:
    #     cart = Cart.objects.get(cart_id = _cart_id(request))  # get the cart using the cart_id present in the session
    # except Cart.DoesNotExist:
    #     cart = Cart.objects.create(
    #         cart_id = _cart_id(request)
    #     )
    # cart.save()
    
    # is_cart_item_exists = CartItem.objects.filter(product = product, cart = cart).exists()   #here
    # if is_cart_item_exists:
    #     cart_item = CartItem.objects.filter(product = product, cart = cart)
    #     cart_item.quantity += 1
    #     cart_item.save()
    # else:
    #     cart_item = CartItem.objects.create(
    #         product = product,
    #         quantity = 1,
    #         cart = cart,
    #     )
    #     cart_item.save()   #to here
    # return redirect('cart')
    
    
    
    # try:
    #     cart_item = CartItem.objects.get(product = product, cart = cart)
    #     cart_item.quantity += 1
    #     cart_item.save()
        
    # except CartItem.DoesNotExist:
    #     cart_item = CartItem.objects.create(
    #         product = product,
    #         quantity = 1,
    #         cart = cart,
    #     )
    #     cart_item.save()
    # return redirect('cart')


# def remove_cart(request, product_id, cart_item_id):
#     product = get_object_or_404(Product, id=product_id)
#     try:
#         if request.user.is_authenticated:
#             cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
#         else:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#             cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
#         if cart_item.quantity > 1:
#             cart_item.quantity -= 1
#             cart_item.save()
#         else:
#             cart_item.delete()
#     except:
#         pass
#     return redirect('cart')


def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    else:
        # Check if the cart exists before querying
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()
        
        if cart:
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()
            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()

    return redirect('cart')


# def remove_cart_item(request, product_id):
#     cart = Cart.objects.get(cart_id = _cart_id(request))
#     product = get_object_or_404(Product, id = product_id)
#     cart_item = CartItem.objects.get(product = product, cart = cart)
#     cart_item.delete()
#     return redirect('cart')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Remove the cart item for logged-in users
        cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        if cart_item:
            cart_item.delete()
    else:
        # Check if the cart exists before querying for cart items
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()

        if cart:
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()
            if cart_item:
                cart_item.delete()

    return redirect('cart')

        

def cart(request, total=0, quantity=0, cart_items = None):  
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (3 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        
    }
      
    return render(request, 'store/cart.html', context)

@login_required(login_url = 'login')
def checkout(request, total=0, quantity=0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        
    }
    return render(request, 'store/checkout.html', context)