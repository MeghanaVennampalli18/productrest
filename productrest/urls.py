"""
URL configuration for productrest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from productrest import views


urlpatterns = [
    path('admin', admin.site.urls),
    path('api/rest/v1/all',views.Fetch_All),
    path('api/rest/v1/product/register',views.Product_Register),
    path('api/rest/v1/product/update/<uuid:product_id>',views.Product_Update),
    path('api/rest/v1/product/delete/<uuid:product_id>',views.Product_Delete), 
    path('api/rest/v1/<uuid:product_id>',views.Fetch_Product),
    path('api/rest/v1/user/register',views.User_Register),
    path('api/rest/v1/user/login',views.User_Login),
    path('api/rest/v1/validate/user',views.User_Validate),
    path('api/rest/v1/admin/register',views.Admin_Register),
    path('api/rest/v1/admin/login',views.Admin_Login),
    path('api/rest/v1/validate/admin',views.Admin_Validate),
    path('api/rest/v1/quantityincrease',views.Quantity_Increase),
    path('api/rest/v1/quantitydecrease',views.Quantity_Decrease),
    path('api/rest/v1/usercartitems',views.User_CartItems),
    path('api/rest/v1/cartitemdelete/<uuid:cart_id>',views.CartItem_Delete),
    path('api/rest/v1/clearallitems',views.Clear_all_CartItems),
    path('api/rest/v1/orderplace',views.Order_Place),
    path('api/rest/v1/orderview',views.Order_View),
    path('api/rest/v1/ordercart',views.Order_Cart),


    # path('api/rest/v1/cartview',views.Cart_View),
    # path('api/rest/v1/cartadd',views.Cart_Add),
    # path('api/rest/v1/cartitemdelete/<uuid:cartitem_id>',views.CartItem_Delete),
    # path('api/rest/v1/usercartitems/<uuid:cart_id>',views.User_CartItems),
    # path('api/rest/v1/clearallitems/<uuid:cart_id>',views.Clear_all_CartItems),
]
