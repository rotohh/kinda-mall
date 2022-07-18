from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[a-z0-9-_]+?)-(?P<shop_pk>[0-9]+)/$',
        views.shop_details, name='shop-details'),
    url(r'^(?P<slug>[a-z0-9-_]+?)-(?P<shop_pk>[0-9]+)/(?P<slug1>[a-z0-9-_]+?)-(?P<product_id>[0-9]+)/$',
        views.shop_product_details, name='shop-product-details')]