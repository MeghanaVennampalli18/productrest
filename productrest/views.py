from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import AuthenticationFailed
import jwt,datetime
from jwt.exceptions import ExpiredSignatureError
from django.conf import settings
from rest_framework.permissions  import IsAuthenticated
from django.http import Http404
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from datetime import date,datetime



@api_view(['POST'])
def User_Register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    if not serializer.is_valid():
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def User_Login(request):  
    usertype = "user"
    try:
        email = request.data['email']
        password = request.data['password']  
    except KeyError:
        error_message = {'error': 'Both email and password are required.'}
        return Response(error_message, status=400) 
    user = UserDetails.objects.filter(email=email).first()
    if user is None:
        # return Response({'error':'user not found'},status=status.HTTP_401_UNAUTHORIZED)
        raise AuthenticationFailed('user not found')
    
    if password!=user.password:
        # return Response({'error':'incorrect password'},status=status.HTTP_401_UNAUTHORIZED)
        raise AuthenticationFailed('incorrect password')
    payload = {'id':str(user.user_id),
               'username':user.username,
               'usertype' :usertype, 
               'exp':datetime.utcnow()+timedelta(minutes=60),
               'iat':datetime.utcnow()
               }
    token = jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
    response = Response()
    # response.set_cookie(key='jwt',value=token,httponly=True)
    response.data={'id':str(user.user_id),'name':user.username,'jwt': token}
    return response


@api_view(['GET'])
def User_Validate(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    token = auth_header.split(' ')[1]
    # token = request.COOKIES.get('jwt')
    # if not token:
    #     raise AuthenticationFailed('unauthenticated')
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    user = UserDetails.objects.filter(username = payload['username'],user_id = payload['id']).first()
    serializer = UserLoginSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
def Admin_Register(request):
    serializer = AdminRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    if not serializer.is_valid():
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def Admin_Login(request):
    usertype = "admin"
    try:
        email = request.data['email']
        password = request.data['password']  
    except KeyError:
        error_message = {'error': 'Both email and password are required.'}
        return Response(error_message, status=400) 
    
    admin = AdminDetails.objects.filter(email=email).first()
    if admin is None:
        raise AuthenticationFailed('admin not found')
    if password!=admin.password:
        raise AuthenticationFailed('incorrect password')
    payload = {'id' :str(admin.admin_id),
               'username':admin.username,
               'usertype' :usertype, 
               'exp':datetime.utcnow()+timedelta(minutes=60),
               'iat':datetime.utcnow()
               }
    token = jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
    response = Response()
    # response.set_cookie(key='jwt',value=token,httponly=True)
    response.data={'id':str(admin.admin_id),'name':admin.username,'jwt': token}
    return response



@api_view(['GET'])
def Admin_Validate(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    admin = AdminDetails.objects.filter(username = payload['username'],admin_id = payload['id']).first()
    serializer = AdminLoginSerializer(admin)
    return Response(serializer.data)


@api_view(['GET'])
def Fetch_All(request):
    pagination_class = LimitOffsetPagination
    products = Product.objects.all()
    brand = request.GET.getlist('brand')
    category = request.GET.getlist('category')
    price_gt = request.GET.get('price__gt')
    price_lt = request.GET.get('price__lt')
    search_query = request.GET.get('search')
    order_by = request.GET.get('orderby')
    if brand:
        products = products.filter(brand__in=brand)
    if category:
        products = products.filter(category__in=category)
    if price_gt:
        products = products.filter(price__gt=price_gt)
    if price_lt:
        products = products.filter(price__lt=price_lt)
    if search_query:
        name_filtered = products.filter(name__icontains=search_query)    
        description_filtered = products.filter(description__icontains=search_query)
        products = name_filtered.union(description_filtered)
    if order_by == 'low_to_high':
        products = products.order_by('price')
    elif order_by == 'high_to_low':
        products = products.order_by('-price')
    # serializer = ProductSerializer(products, many = True)
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['brand','category','price_lt','price_gt']
    search_fields = ['name','description']
    ordering_fields = ['price']

    paginator = pagination_class()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)

    return paginator.get_paginated_response(serializer.data)
    # return Response(serializer.data)


@api_view(['POST'])
def Product_Register(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    if payload['usertype']=='admin':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        if not serializer.is_valid(): 
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if payload['usertype']!='admin':    
        return Response({'message':'Only admin have access to register'},status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
def Product_Update(request,product_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    if payload['usertype']=='admin':
        try:
            product=Product.objects.get(pk=product_id)
        except:
            raise Http404('Product not found')
        serializer = ProductSerializer(product,data = request.data)
        if serializer.is_valid():
            serializer.save()
            # carts = Cart.objects.all()
            # for cart in carts:
            #     cart.update_total_price()
            return Response(serializer.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if payload['usertype']!='admin':    
        return Response({'message':'Only admin have access to update'},status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
def Product_Delete(request,product_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    if payload['usertype']=='admin':
        try:
            product=Product.objects.get(pk=product_id)
        except:
            raise Http404('Product not found')
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if payload['usertype']!='admin':
        return Response({'message':'Only admin have access to update'},status=status.HTTP_403_FORBIDDEN)
    

@api_view(['GET'])
def Fetch_Product(request,product_id):
    try:
        product=Product.objects.get(pk=product_id)
    except:
        return Response({'error','Product not found'},status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['POST'])
def Quantity_Increase(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    
    product_id = request.data.get('product')
    existing_cart_item = Cart.objects.filter(user=payload['id'], product=product_id).first()

    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.save()
        serializer = CartSerializer(existing_cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if not existing_cart_item:
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = payload['id'],product_id = product_id)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def Quantity_Decrease(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    
    product_id = request.data.get('product')
    existing_cart_item = Cart.objects.filter(user=payload['id'], product=product_id).first()

    if existing_cart_item:
        existing_cart_item.quantity -= 1
        if existing_cart_item.quantity <= 0:
            existing_cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)   
        if existing_cart_item.quantity > 0:
            existing_cart_item.save()
            serializer = CartSerializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
    if not existing_cart_item:    
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def User_CartItems(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    user_id = payload['id']
    cart_items = Cart.objects.filter(user=user_id)
    cart_item_details = []
    for cart_item in cart_items:
        product = get_object_or_404(Product, product_id=cart_item.product.product_id)
        cart_item_details.append({
            'cart_id':cart_item.cart_id,
            'product_id':product.product_id,
            'product_name': product.name,
            'product_image': product.image,
            'quantity': cart_item.quantity,
        })
    return Response(cart_item_details, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def CartItem_Delete(request,cart_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    user_id = payload['id']
    try:
        cart_item = Cart.objects.get(pk=cart_id, user=user_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Cart.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)  
    

@api_view(['DELETE'])
def Clear_all_CartItems(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    user_id = payload['id']
    try:
        cart = Cart.objects.filter(user=user_id)
        cart.delete()
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "All items cleared from the cart."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def Order_Place(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    try:
        user_id = payload['id']
        address = request.data.get("Address")
        orders_data = request.data.get("Orders")
        payment_data = request.data.get("Payment")
        credit_card_number = payment_data.get("creditCardNumber")
        expiry_year = payment_data.get("ExpiryYear")
        cvv = payment_data.get("Cvv")

        if not (credit_card_number.isdigit() and len(credit_card_number) == 12):
            return Response({"error": "Invalid credit card number"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            expiry_date = datetime.strptime(expiry_year, "%m/%y")
        except ValueError:
            return Response({"error": "Invalid expiry year format"}, status=status.HTTP_400_BAD_REQUEST)
        if expiry_date < datetime.now():
            return Response({"error": "Expired card"}, status=status.HTTP_400_BAD_REQUEST)
        if not (cvv.isdigit() and len(cvv) == 3):
            return Response({"error": "Invalid CVV"}, status=status.HTTP_400_BAD_REQUEST)

        orders = []
        for order_data in orders_data:
            try:
                product_id = order_data.get("product_id")
                product = Product.objects.get(pk=product_id)
            except:
                return Response({'error':'invalid product_id'},status=status.HTTP_400_BAD_REQUEST)
            
            quantity=order_data.get("quantity")
            order = Order(
                order_id=uuid.uuid4(),
                product=product,
                user= user_id,
                order_date=date.today(),
                quantity=quantity,
                order_price = quantity * product.price,
                address=address
            )
            order.save()
            orders.append(order)
        serializer = OrderSerializer(orders, many=True)
        output = {
            "Address": address,
            "Orders": serializer.data,
            "Payment": payment_data
        }
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def Order_View(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    user_id = payload['id']
    order_items = Order.objects.filter(user=user_id)
    order_item_details = []
    for order_item in order_items:
        product = get_object_or_404(Product, product_id=order_item.product.product_id)
        order_item_details.append({
            'order_id':order_item.order_id,
            'product_id':product.product_id,
            'product_name': product.name,
            'product_image': product.image,
            'product_price': product.price,
            'quantity': order_item.quantity,
            'order_price': order_item.order_price,
            'order_date': order_item.order_date,
            'Address': order_item.address
        })
    return Response(order_item_details, status=status.HTTP_200_OK)  

@api_view(['POST'])
def Order_Cart(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise AuthenticationFailed('unauthenticated')
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error':'token_expired'},status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error':'token_invalid'},status=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response({'error':'token_invalid'},status=status.HTTP_403_FORBIDDEN)
    try:
        user_id = payload['id']
        address = request.data.get("Address")
        payment_data = request.data.get("Payment")
        credit_card_number = payment_data.get("creditCardNumber")
        expiry_year = payment_data.get("ExpiryYear")
        cvv = payment_data.get("Cvv")

        if not (credit_card_number.isdigit() and len(credit_card_number) == 12):
            return Response({"error": "Invalid credit card number"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            expiry_date = datetime.strptime(expiry_year, "%m/%y")
        except ValueError:
            return Response({"error": "Invalid expiry year format"}, status=status.HTTP_400_BAD_REQUEST)
        if expiry_date < datetime.now():
            return Response({"error": "Expired card"}, status=status.HTTP_400_BAD_REQUEST)
        if not (cvv.isdigit() and len(cvv) == 3):
            return Response({"error": "Invalid CVV"}, status=status.HTTP_400_BAD_REQUEST)
    
        cart_items = Cart.objects.filter(user=user_id)
        print(cart_items)
        orders = []
        for cart_item in cart_items:
            try:
                product = cart_item.product
            except Product.DoesNotExist:
                return Response({'error': 'invalid product_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            quantity = cart_item.quantity
            order_price = quantity * product.price
            order = Order(
                order_id=uuid.uuid4(),
                product=product,
                user=user_id,
                order_date=date.today(),
                quantity=quantity,
                order_price=order_price,
                address=request.data.get("Address")
            )
            order.save()
            cart_item.delete()
            orders.append(order)
        
        serializer = OrderSerializer(orders, many=True)   
        output = {
            "Address": request.data.get("Address"),
            "Orders": serializer.data,
            "Payment": payment_data
        }
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





# @api_view(['GET'])
# def Cart_View(request):
#     # auth_header = request.headers.get('Authorization')
#     # if not auth_header or not auth_header.startswith('Bearer '):
#     #     raise AuthenticationFailed('unauthenticated')
#     # token = auth_header.split(' ')[3]
#     # try:
#     #     payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
#     # except jwt.ExpiredSignatureError:
#     #     raise AuthenticationFailed('unauthenticated')
#     # if payload['usertype']=='admin' or payload['usertype']=='login':
#     carts = Cart.objects.all()
#     serializer = CartSerializer(carts,many = True)
#     return Response(serializer.data)
#     # return Response(status=status.HTTP_401_UNAUTHORIZED)


# # @api_view(['POST'])
# # def Cart_Add(request):
# #     serializer = CartSerializer(data=request.data)
# #     if serializer.is_valid():
# #         serializer.save()
# #         return Response(serializer.data,status=status.HTTP_201_CREATED)
# #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# @api_view(['POST'])
# def Quantity_Decrease(request):
#     try:
#         cart_id = request.data.get("cart")
#         cart = Cart.objects.get(pk=cart_id)
#         product_id = request.data.get('product')
#         product = Product.objects.get(pk=product_id)
#     except:    
#         return Response({'errors':'Inavlid input'},status=status.HTTP_400_BAD_REQUEST)   
#     quantity = int(request.data.get('quantity', 1))
#     price = quantity * float(product.price)
#     existing_cart_item = CartItems.objects.filter(cart=cart, product=product).first()
#     if existing_cart_item:
#         existing_cart_item.quantity-=quantity
#         if existing_cart_item.quantity == 0:
#             existing_cart_item.price -= price
#             existing_cart_item.save()
#             cart.total_price -= price
#             cart.save()
#             existing_cart_item.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         elif existing_cart_item.quantity < 0:
#             existing_cart_item.delete()    
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         existing_cart_item.price -= price
#         existing_cart_item.save()
#         cart.total_price -= price
#         cart.save()
#         return Response(status=status.HTTP_200_OK)  
#     return Response(status=status.HTTP_404_NOT_FOUND)  


# @api_view(['POST'])
# def Quantity_Increase(request):
#     try:
#         cart_id = request.data.get("cart")
#         cart = Cart.objects.get(pk=cart_id)
#         product_id = request.data.get('product')
#         product = Product.objects.get(pk=product_id)
#     except:    
#         return Response({'errors':'Inavlid input'},status=status.HTTP_400_BAD_REQUEST)   
#     quantity = int(request.data.get('quantity', 1))
#     price = quantity * float(product.price)
#     existing_cart_item = CartItems.objects.filter(cart=cart, product=product).first()
#     if existing_cart_item:
#         existing_cart_item.quantity+=quantity
#         existing_cart_item.price += price
#         existing_cart_item.save()
#         cart.total_price += price
#         cart.save()
#         return Response(status=status.HTTP_200_OK)
#     serializer = CartItemSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(cart=cart, product=product, price=product.price)
#         cart.total_price += price
#         cart.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['DELETE'])
# def CartItem_Delete(request,cartitem_id):
#     try:
#         item = CartItems.objects.get(pk=cartitem_id)
#         cart = item.cart
#         cart.total_price -= (item.price * item.quantity)
#         cart.save()
#         item.delete()
#         remaining_items = CartItems.objects.filter(cart=cart)
#         total_price = sum(item.price * item.quantity for item in remaining_items)
#         cart.total_price = total_price
#         cart.save() 
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     except CartItems.DoesNotExist:
#         return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)    

# @api_view(['GET'])
# def User_CartItems(request,cart_id): 
#     try:
#         user=Cart.objects.get(pk=cart_id)
#         cart_items = CartItems.objects.filter(cart = user.cart_id)     
#     except:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     serializer = CartItemSerializer(cart_items, many=True)
#     product_ids = cart_items.values_list('product', flat=True).distinct()
#     # product_details = [{'total_price':user.total_price}]
#     usercartitems=[{'total_price':user.total_price}]
#     for product_id in product_ids:
#         product=Product.objects.get(pk=product_id)
#         product_list={}
#         product_list['product_id']=product_id
#         product_list['name']=product.name
#         product_list['image']=product.image
#         cart_item = cart_items.get(product=product_id)
#         product_list['price'] = product.price
#         product_list['quantity'] = cart_item.quantity
#         usercartitems.append(product_list)
#     return Response(usercartitems)   

#     #     product = Product.objects.filter(pk=product_id)
#     #     product_serializer = ProductSerializer(product, many=True)
#     #     product_data = product_serializer.data[0]
#     #     print(product_data)
#     #     cart_item = cart_items.get(product=product_id)
#     #     product_data['price'] = cart_item.price
#     #     product_data['quantity'] = cart_item.quantity
#     #     product_details.append(product_data)   
#     # return Response(product_details)


# @api_view(['DELETE'])
# def Clear_all_CartItems(request,cart_id):
#     try:
#         user_cart = Cart.objects.get(pk=cart_id)
#         cart_items = CartItems.objects.filter(cart=user_cart)
#         total_price = 0
#         user_cart.total_price = 0
#         user_cart.save()
#         cart_items.delete()
#     except Cart.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     return Response({"message": "All items cleared from the cart."}, status=status.HTTP_200_OK)

# # @api_view(['PUT'])
# # def Update_Price(request):
# #     try:
# #         cart_id = request.data.get('id')
# #         cart = Cart.objects.get(id=cart_id)
# #     except Cart.DoesNotExist:
# #         return Response({"message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
# #     cart.update_total_price()
# #     return Response({"message": "Product price updated successfully."}, status=status.HTTP_200_OK)



# # @api_view(['PUT'])
# # def CartItem_Update(request,id):
# #     try:
# #         cart_item=CartItems.objects.get(pk=id)
# #         quantity = request.data.get('quantity')     
# #     except:
# #         return Response(status=status.HTTP_404_NOT_FOUND)
# #     cart_id = request.data.get("cart")
# #     cart = Cart.objects.get(pk=cart_id)
# #     serializer = CartItemSerializer(cart_item,data = request.data)
# #     product_id = request.data.get('product')
# #     product = Product.objects.get(pk=product_id)
# #     # quantity = int(request.data.get('quantity', 1))
# #     price = (quantity-cart_item.quantity) * float(product.price)
# #     print(price)
# #     if serializer.is_valid():
# #         serializer.save(cart=cart, product=product, price=price)
# #         cart.total_price += price
# #         cart.save()
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)
# #     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)   

#     # if serializer.is_valid():
#     #     serializer.save()
#     #     return Response(serializer.data)
#     # return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




