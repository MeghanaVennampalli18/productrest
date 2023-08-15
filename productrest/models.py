from django.db import models
import uuid
import jwt
from django.conf import settings
from datetime import datetime,timedelta
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import django


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100,unique=True,blank=False,validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]+$', message='Usertype must be a string.')])
    category = models.CharField(max_length=100,blank=False)
    brand = models.CharField(max_length=50,blank=False)
    price = models.IntegerField(blank=False)
    description = models.CharField(max_length=300)
    image = models.URLField()
 
    def __unicode__(self):
        return self.product_id
    
    
# @receiver(post_save, sender=Product)
# def update_cart_items_on_product_price_change(sender, instance, **kwargs):
#     cart_items = CartItems.objects.filter(product=instance)
#     for cart_item in cart_items:
#         cart_item.price = instance.price
#         cart_item.save()      


class UserDetails(models.Model):
    user_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    # usertype = models.CharField(max_length=50,blank=False,validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]+$', message='Usertype must be a string.')])
    username = models.CharField(max_length=50,blank=False,unique=True,validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]+$', message='Usertype must be a string.')])
    password = models.CharField(max_length=50,blank=False)
    email = models.EmailField(blank=False,unique=True)

    def __unicode__(self):
        return self.user_id
 
    
class AdminDetails(models.Model):
    admin_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    # usertype = models.CharField(max_length=50,blank=False,validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]+$', message='Usertype must be a string.')]) 
    username = models.CharField(max_length=50,blank=False,unique=True,validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z]+$', message='Usertype must be a string.')])
    password = models.CharField(max_length=50,blank=False)
    email = models.EmailField(blank=False,unique=True)

    def __unicode__(self):
        return self.admin_id   

class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.UUIDField(default=uuid.uuid4,editable=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    # total_price = models.FloatField(default=0)
    def __unicode__(self):
        return self.cart_id 
    
    # def update_total_price(self):
    #     cart_items = CartItems.objects.filter(cart=self)
    #     total_price = sum(cart_item.price * cart_item.quantity for cart_item in cart_items)
    #     self.total_price = total_price
    #     print(total_price)
    #     self.save()

# class CartItems(models.Model):
#     cartitem_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
#     cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
#     product = models.ForeignKey(Product,on_delete=models.CASCADE)
#     price = models.FloatField(default=0)
#     quantity = models.IntegerField(default=1)


# @receiver(pre_save, sender = CartItems)
# def correct_price(sender, **kwargs):
#     cart_items = kwargs['instance']
#     price_of_product = Product.objects.get(id = cart_items.product.id)
#     cart_items.price = cart_items.quantity * float(price_of_product.price)
#     total_cart_items = CartItems.objects.filter(user = cart_items.user)

#     cart = Cart.objects.get(id = cart_items.cart.id)
#     cart.total_price  =cart.total_price + cart_items.price
#     cart.save()


