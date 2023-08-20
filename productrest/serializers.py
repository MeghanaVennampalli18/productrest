from rest_framework import serializers
from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id','name','category','brand','price','description','image']


class UserRegisterSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model = UserDetails
        fields = ['user_id','username','password','email']
        
    
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['user_id','email','password']   


class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model = AdminDetails
        fields = ['admin_id','username','password','email']
    

class AdminLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminDetails
        fields = ['email','password'] 

       
class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name',read_only = True)
    product_image = serializers.CharField(source='product.image',read_only = True)
    class Meta:
        model = Cart
        fields = ['cart_id','user','product','quantity','product_name','product_image']

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name',read_only = True)
    product_image = serializers.CharField(source='product.image',read_only = True)
    class Meta:
        model = Order
        fields = ['order_id','user','product','quantity','order_date','order_price','address','product_name','product_image']

# class CartSerializer(serializers.ModelSerializer):
#     items=CartItemSerializer(many = True, read_only = True)
#     class Meta:
#         model = Cart
#         fields = '__all__'

    
     
       

