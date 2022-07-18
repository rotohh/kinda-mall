import datetime
import json

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from ..core.utils import get_paginator_items
from .utils import (
    collections_visible_to_user, get_product_images, get_product_list_context,
    handle_cart_form, products_for_cart, products_for_products_list,
    products_with_details)
from ..shop.models import Shop

def shop_details(request, slug, shop_pk):
    shops = Shop.objects.prefetch_related('shop_products', 'shop_orders')
    shop = get_object_or_404(shops, pk=shop_pk)
    my_shop_products_paginated = get_paginator_items(
        shop.shop_products.all(), settings.PAGINATE_BY, request.GET.get('page'))
    my_orders = shop.shop_orders.filter(user=request.user.is_authenticated)
    my_orders_paginated = get_paginator_items(
            my_orders, settings.PAGINATE_BY, request.GET.get('page'))
    if shop.get_slug() != slug:
        return HttpResponsePermanentRedirect(shop.get_absolute_url())
    today = datetime.date.today()
    ctx = {
        'products': my_shop_products_paginated, 'my_orders' : my_orders_paginated,
        'shop': shop}
    return TemplateResponse(request, 'shop/details.html', ctx)
	
def shop_product_details(request, slug, shop_pk, slug1, product_id, form=None):
    products = products_with_details(user=request.user)
    product = get_object_or_404(products, id=product_id)
    shop = Shop.objects.get(id=product.shop.id)
    shops = Shop.objects.prefetch_related('shop_orders')
    myshop = get_object_or_404(shops, pk=shop_pk)
    my_orders = myshop.shop_orders.filter(user=request.user.is_authenticated)
    my_orders_paginated = get_paginator_items(
        my_orders, settings.PAGINATE_BY, request.GET.get('page'))
    if product.get_slug() != slug:
        return HttpResponsePermanentRedirect(product.get_absolute_url())
    today = datetime.date.today()
    is_visible = (
        product.available_on is None or product.available_on <= today)
    if form is None:
        form = handle_cart_form(request, product, create_cart=False)[0]
    availability = get_availability(
        product, discounts=request.discounts, taxes=request.taxes,
        local_currency=request.currency)
    product_images = get_product_images(product)
    variant_picker_data = get_variant_picker_data(
        product, request.discounts, request.taxes, request.currency)
    product_attributes = get_product_attributes_data(product)
    # show_variant_picker determines if variant picker is used or select input
    show_variant_picker = all([v.attributes for v in product.variants.all()])
    json_ld_data = product_json_ld(product, product_attributes)
    ctx = {
        'is_visible': is_visible,
        'form': form,
        'availability': availability,
        'product': product,
        'shop': shop,
        'my_orders' : my_orders_paginated,
        'product_attributes': product_attributes,
        'product_images': product_images,
        'show_variant_picker': show_variant_picker,
        'variant_picker_data': json.dumps(
            variant_picker_data, default=serialize_decimal),
        'json_ld_product_data': json.dumps(
            json_ld_data, default=serialize_decimal)}
    return TemplateResponse(request, 'shop/product/details.html', ctx)

