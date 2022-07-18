from datetime import date
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext, pgettext_lazy, ugettext_lazy as _ ,npgettext_lazy
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import (
    staff_member_required as _staff_member_required, user_passes_test)

from ..discount.models import Sale
from ..product.models import (
    Attribute, AttributeValue, Product, ProductImage, ProductType,
    ProductVariant)
from ..product.utils.availability import get_availability
from ..product.utils.costs import (
    get_margin_for_variant, get_product_costs_data)
#from ...views import staff_member_required
from ..dashboard.product.filters import AttributeFilter, ProductFilter, ProductTypeFilter
from . import forms
from ..shop.models import Shop#, ShopCategory #to be removed if it works
from ..order.models import SubOrder, OrderLine
from ..checkout.utils import find_and_assign_anonymous_cart
from ..core.utils import get_paginator_items
from .emails import send_account_delete_confirmation_email
from .forms import (
    ChangePasswordForm, LoginForm, NameForm, PasswordResetForm, SignupForm, ShopForm,# ShopCategoryForm,
    get_address_form, logout_on_password_change)
from ..dashboard.product.forms import (
    RichTextField,ProductTypeSelectorForm,get_tax_rate_type_choices,ProductTypeForm,
    AttributesMixin,ProductForm,ProductVariantForm,CachingModelChoiceIterator,CachingModelChoiceField,
    VariantBulkDeleteForm,ProductImageForm,VariantImagesSelectForm,AttributeForm,AttributeValueForm,
    ReorderAttributeValuesForm,ReorderProductImagesForm,UploadImageForm,ProductBulkUpdate )

IMAGE_FILE_TYPES = ['png','jpg','jpeg']

def staff_member_required(f):
    return _staff_member_required(f, login_url='account:login')
	
@find_and_assign_anonymous_cart()
def login(request):
    kwargs = {
        'template_name': 'account/login.html',
        'authentication_form': LoginForm}
    return django_views.LoginView.as_view(**kwargs)(request, **kwargs)


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect(settings.LOGIN_REDIRECT_URL)


def signup(request):
    form = SignupForm(request.POST or None)
    if form.is_valid():
        form.save()
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = auth.authenticate(
            request=request, email=email, password=password)
        if user:
            auth.login(request, user)
        messages.success(request, _('User has been created'))
        redirect_url = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        return redirect(redirect_url)
    ctx = {'form': form}
    return TemplateResponse(request, 'account/signup.html', ctx)


def password_reset(request):
    kwargs = {
        'template_name': 'account/password_reset.html',
        'success_url': reverse_lazy('account:reset-password-done'),
        'form_class': PasswordResetForm}
    return django_views.PasswordResetView.as_view(**kwargs)(request, **kwargs)


class PasswordResetConfirm(django_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_from_key.html'
    success_url = reverse_lazy('account:reset-password-complete')
    token = None
    uidb64 = None


def password_reset_confirm(request, uidb64=None, token=None):
    kwargs = {
        'template_name': 'account/password_reset_from_key.html',
        'success_url': reverse_lazy('account:reset-password-complete'),
        'token': token,
        'uidb64': uidb64}
    return PasswordResetConfirm.as_view(**kwargs)(request, **kwargs)


@login_required
def details(request):
    password_form = get_or_process_password_form(request)
    name_form = get_or_process_name_form(request)
    orders = request.user.orders.confirmed().prefetch_related('lines')
    orders_paginated = get_paginator_items(
        orders, settings.PAGINATE_BY, request.GET.get('page'))
    ctx = {'addresses': request.user.addresses.all(),
           'shop' : request.user.shop.all(),
           'orders': orders_paginated,
           'change_password_form': password_form,
           'user_name_form': name_form}

    return TemplateResponse(request, 'account/details.html', ctx)


def get_or_process_password_form(request):
    form = ChangePasswordForm(data=request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        logout_on_password_change(request, form.user)
        messages.success(request, pgettext(
            'Storefront message', 'Password successfully changed.'))
    return form


def get_or_process_name_form(request):
    form = NameForm(data=request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, pgettext(
            'Storefront message', 'Account successfully updated.'))
    return form

	
#@login_required
#def shop_add(request):
    #shop_form = get_or_process_shop_form(request)
    #return redirect('account:shop-details', pk=shop.pk)   
    #return TemplateResponse(
        #request, 'account/shop_add.html',
        #{'shop_form': shop_form})
    

#def get_or_process_shop_form(request):
    #if not request.user.is_authenticated :
	    #raise Http404
		
    #shop = Shop()
    #shop = get_object_or_404(Shop, pk=pk)
    #form = ShopForm(data=request.POST or None, instance=shop)
    #if form.is_valid():
        #instance = form.save(commit=False)
        #instance.user = request.user
        #instance.save()
        #messages.success(request, pgettext(
            #'Storefront message', 'Account successfully updated.'))
    #return form	

def shop_add(request):	
    if not request.user.is_authenticated :
	    raise Http404
		
    shop = Shop()
    #shop = get_object_or_404(Shop, pk=pk)
    shop_form = ShopForm(data=request.POST or None, instance=shop)
    if shop_form.is_valid():
        instance = shop_form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, pgettext(
            'Storefront message', 'Account successfully updated.'))
        return redirect('account:shop-details', pk=shop.pk)    
    return TemplateResponse(
        request, 'account/shop_add.html',
        {'shop_form': shop_form})
#to be removed if it works
def shop_details(request, pk):
    qs = Shop.objects.select_related('user').prefetch_related('shop_products', 'shop_orders')
    shop = get_object_or_404(qs, pk=pk) #request.user.shop
    #suborders = SubOrder.objects.filter(order_owner = request.user.id)    
    #products = Product.objects.select_related('shop').prefetch_related('images') #.filter(user = request.user)
    #products = products.order_by('name')
    #product_filter = ProductFilter(request.GET, queryset=products)
    #products = get_paginator_items(
        #product_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        #request.GET.get('page'))
    my_shop_products_paginated = get_paginator_items(
        shop.shop_products.all(), settings.PAGINATE_BY, request.GET.get('page'))
    product_types = ProductType.objects.all()
    suborders = shop.shop_orders.all()
    suborders_paginated = get_paginator_items(
        suborders, settings.PAGINATE_BY, request.GET.get('page'))
    shop_form = ShopForm(
        request.POST or None,instance=shop)
    if shop_form.is_valid():
        shop_form.save()
        message = pgettext(
            'Storefront message', 'Updated shop %s') % (shop,)
        messages.success(request, message)
        return redirect('account:shop-details', pk=shop.pk)
    ctx = {
        'shop': shop, 'suborders': suborders_paginated, 'product_types': product_types,
        'bulk_action_form': ProductBulkUpdate(),'shop_form': shop_form,
        'products': my_shop_products_paginated}
        #'filter_set': product_filter,
        #'is_empty': not product_filter.queryset.exists()
    return TemplateResponse(request, 'account/shop/detail.html', ctx)

def shop_product_details(request, pk, product_pk):
    shops = Shop.objects.all()
    shop = get_object_or_404(shops, pk=pk) 
    products = Product.objects.prefetch_related('variants', 'images')#.filter(user = request.user)
    product = get_object_or_404(products, pk=product_pk)
    variants = product.variants.all()
    images = product.images.all()
    availability = get_availability(
        product, discounts=request.discounts, taxes=request.taxes)
    sale_price = availability.price_range_undiscounted
    discounted_price = availability.price_range
    purchase_cost, margin = get_product_costs_data(product)

    # no_variants is True for product types that doesn't require variant.
    # In this case we're using the first variant under the hood to allow stock
    # management.
    no_variants = not product.product_type.has_variants
    only_variant = variants.first() if no_variants else None
    ctx = {
        'product': product, 'sale_price': sale_price, 'shop': shop,
        'discounted_price': discounted_price, 'variants': variants,
        'images': images, 'no_variants': no_variants,
        'only_variant': only_variant, 'purchase_cost': purchase_cost,
        'margin': margin, 'is_empty': not variants.exists()}
    return TemplateResponse(request, 'account/shop/product/detail.html', ctx)

######## remove this one	
def shop_edit(request, pk):
    shop = get_object_or_404(request.user.shop, pk=pk)
    shop_form = ShopForm(
        request.POST or None,instance=shop)
    if shop_form.is_valid():
        shop_form.save()
        message = pgettext(
            'Storefront message', 'Updated shop %s') % (shop,)
        messages.success(request, message)
        return redirect('account:shop-details', pk=shop.pk)
    return TemplateResponse(
        request, 'account/shop/shop_edit.html',
        {'shop_form': shop_form})

######remove this shop orders
def shop_orders(request, pk):
    shop = get_object_or_404(request.user.shop, pk=pk)
    suborders = SubOrder.objects.filter(order_owner = request.user.id)
    ctx = {
        'suborders': suborders,
        'shop':shop}
    return TemplateResponse(request, 'account/shop/order/list.html', ctx)
 

def shop_customers (request, pk):
    shop = get_object_or_404(request.user.shop, pk=pk)
    return

def shop_order_details(request, pk, sub_order_pk):
    shop = get_object_or_404(request.user.shop, pk=pk)
    #qs = SubOrder.objects.all()
    suborder = get_object_or_404(SubOrder, pk=sub_order_pk)
    orderitems = OrderLine.objects.filter(order=suborder.order, shop = suborder.shop)#  product_owner=suborder.order_owner)	
    ctx = {
        'orderitems': orderitems,
        'shop': shop,
        'suborder': suborder}
    return TemplateResponse(request, 'account/shop/order/detail.html', ctx)
	
"""def shop_add_category(request):
    View for add product modal embedded in the product list view.
    #shop = Shop()
    shopcategory = ShopCategory()
    form = ShopCategoryForm(request, data=request.POST or None, instance=shopcategory) #, instance=shopcategories
    if form.is_valid():
        shopcategory = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added shopcategory %s') % (shopcategory,)
        messages.success(request, msg)
        #return redirect('account:shop-details', pk=shop.pk)
    ctx = {'form': form}
    template = 'account/shop/shop_add_category.html'
    return TemplateResponse(request, template, ctx)"""

		
@login_required
def address_edit(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    address_form, preview = get_address_form(
        request.POST or None, instance=address,
        country_code=address.country.code)
    if address_form.is_valid() and not preview:
        address_form.save()
        message = pgettext(
            'Storefront message', 'Address successfully updated.')
        messages.success(request, message)
        return HttpResponseRedirect(reverse('account:details') + '#addresses')
    return TemplateResponse(
        request, 'account/address_edit.html',
        {'address_form': address_form})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(
            request,
            pgettext('Storefront message', 'Address successfully removed'))
        return HttpResponseRedirect(reverse('account:details') + '#addresses')
    return TemplateResponse(
        request, 'account/address_delete.html', {'address': address})


@login_required
@require_POST
def account_delete(request):
    user = request.user
    send_account_delete_confirmation_email.delay(str(user.token), user.email)
    messages.success(
        request, pgettext(
            'Storefront message, when user requested his account removed',
            'Please check your inbox for a confirmation e-mail.'))
    return HttpResponseRedirect(reverse('account:details') + '#settings')


@login_required
def account_delete_confirm(request, token):
    user = request.user

    if str(request.user.token) != token:
        raise Http404('No such page!')

    if request.method == 'POST':
        user.delete()
        msg = pgettext(
            'Account deleted',
            'Your account was deleted successfully. '
            'In case of any trouble or questions feel free to contact us.')
        messages.success(request, msg)
        return redirect('home')

    return TemplateResponse(
        request, 'account/account_delete_prompt.html')

@require_POST
#@staff_member_required
#@permission_required('product.manage_products')
def product_toggle_is_published(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_published = not product.is_published
    product.save(update_fields=['is_published'])
    return JsonResponse(
        {'success': True, 'is_published': product.is_published})

#to be removed if it works
#@staff_member_required
#@permission_required('product.manage_products')
def product_select_type(request, pk):
    """View for add product modal embedded in the product list view."""
    shop = get_object_or_404(Shop, pk=pk)
    form = ProductTypeSelectorForm(request.POST or None)
    status = 200
    if form.is_valid():
        redirect_url = reverse(
            'account:product-add',
            kwargs={'type_pk': form.cleaned_data.get('product_type').pk, 'shop_pk':shop.pk})
        return (
            JsonResponse({'redirectUrl': redirect_url})
            if request.is_ajax() else redirect(redirect_url))
    elif form.errors:
        status = 400
    ctx = {'form': form}
    template = 'account/product/select_type.html'
    return TemplateResponse(request, template, ctx, status=status)

#to be removed if it works
#@staff_member_required
#@permission_required('product.manage_products')
def product_create(request, shop_pk, type_pk):
    shop = get_object_or_404(Shop, pk=shop_pk)
    track_inventory = request.site.settings.track_inventory_by_default
    product_type = get_object_or_404(ProductType, pk=type_pk)
    create_variant = not product_type.has_variants
    product = Product()
    product.product_type = product_type
    product_form = ProductForm(request.POST or None, instance=product)
    if create_variant:
        variant = ProductVariant(
            product=product, track_inventory=track_inventory)
        variant_form = ProductVariantForm(
            request.POST or None,
            instance=variant, prefix='variant')
        variant_errors = not variant_form.is_valid()
    else:
        variant_form = None
        variant_errors = False

    if product_form.is_valid() and not variant_errors:
        product = product_form.save(commit = False)
        product.user = request.user
        product.shop = shop
        product.save()
        if create_variant:
            variant.product = product
            variant_form.save(commit = False)
            variant.user = request.user
            variant.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added product %s') % (product,)
        messages.success(request, msg)
        return redirect('account:shop-product-details', pk=product.pk)
    ctx = {
        'product_form': product_form, 'variant_form': variant_form,
        'product': product}
    return TemplateResponse(request, 'account/product/form.html', ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_edit(request, pk, shop_pk):
    shop = get_object_or_404(Shop, pk=shop_pk)
    product = get_object_or_404(
        Product.objects.prefetch_related('variants'), pk=pk)
    form = ProductForm(request.POST or None, instance=product)

    edit_variant = not product.product_type.has_variants
    if edit_variant:
        variant = product.variants.first()
        variant_form = ProductVariantForm(
            request.POST or None, instance=variant, prefix='variant')
        variant_errors = not variant_form.is_valid()
    else:
        variant_form = None
        variant_errors = False

    if form.is_valid() and not variant_errors:
        product = form.save(commit = False)
        product.user = request.user
        product.shop = shop
        product.save()
        if edit_variant:
            variant_form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product %s') % (product,)
        messages.success(request, msg)
        return redirect('account:shop-product-details', pk=shop.pk, product_pk=product.pk)
    ctx = {
        'product': product, 'product_form': form, 'variant_form': variant_form}
    return TemplateResponse(request, 'account/product/form.html', ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed product %s') % (product,)
        messages.success(request, msg)
        return redirect('dashboard:product-list')
    return TemplateResponse(
        request,
        'dashboard/product/modal/confirm_delete.html',
        {'product': product})


@require_POST
#@staff_member_required
#@permission_required('product.manage_products')
def product_bulk_update(request):
    form = ProductBulkUpdate(request.POST)
    if form.is_valid():
        form.save()
        count = len(form.cleaned_data['products'])
        msg = npgettext_lazy(
            'Dashboard message',
            '%(count)d product has been updated',
            '%(count)d products have been updated',
            number='count') % {'count': count}
        messages.success(request, msg)
    return redirect('dashboard:product-list')


#@staff_member_required
def ajax_products_list(request):
    """Return products filtered by request GET parameters.

    Response format is that of a Select2 JS widget.
    """
    queryset = (
        Product.objects.all()
        if request.user.has_perm('product.manage_products')
        else Product.objects.available_products())
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query))
    products = [
        {'id': product.id, 'text': str(product)} for product in queryset]
    return JsonResponse({'results': products})


#@staff_member_required
#@permission_required('product.manage_products')
def product_type_list(request):
    types = ProductType.objects.all().prefetch_related(
        'product_attributes', 'variant_attributes').order_by('name')
    type_filter = ProductTypeFilter(request.GET, queryset=types)
    types = get_paginator_items(
        type_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    types.object_list = [
        (pt.pk, pt.name, pt.product_attributes.all(),
         pt.variant_attributes.all()) for pt in types.object_list]
    ctx = {
        'product_types': types, 'filter_set': type_filter,
        'is_empty': not type_filter.queryset.exists()}
    return TemplateResponse(
        request,
        'dashboard/product/product_type/list.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_type_create(request):
    product_type = ProductType()
    form = ProductTypeForm(request.POST or None, instance=product_type)
    if form.is_valid():
        product_type = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added product type %s') % (product_type,)
        messages.success(request, msg)
        return redirect('dashboard:product-type-list')
    ctx = {'form': form, 'product_type': product_type}
    return TemplateResponse(
        request,
        'dashboard/product/product_type/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_type_edit(request, pk):
    product_type = get_object_or_404(ProductType, pk=pk)
    form = ProductTypeForm(request.POST or None, instance=product_type)
    if form.is_valid():
        product_type = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated product type %s') % (product_type,)
        messages.success(request, msg)
        return redirect('dashboard:product-type-update', pk=pk)
    ctx = {'form': form, 'product_type': product_type}
    return TemplateResponse(
        request,
        'dashboard/product/product_type/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_type_delete(request, pk):
    product_type = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        product_type.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed product type %s') % (product_type,)
        messages.success(request, msg)
        return redirect('dashboard:product-type-list')
    ctx = {
        'product_type': product_type,
        'products': product_type.products.all()}
    return TemplateResponse(
        request,
        'dashboard/product/product_type/modal/confirm_delete.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def variant_details(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants.all(), pk=variant_pk)

    # If the product type of this product assumes no variants, redirect to
    # product details page that has special UI for products without variants.
    if not product.product_type.has_variants:
        return redirect('dashboard:product-details', pk=product.pk)

    images = variant.images.all()
    margin = get_margin_for_variant(variant)
    discounted_price = variant.get_price(
        discounts=Sale.objects.active(date.today())).gross
    ctx = {
        'images': images, 'product': product, 'variant': variant,
        'margin': margin, 'discounted_price': discounted_price}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/detail.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def variant_create(request, product_pk):
    track_inventory = request.site.settings.track_inventory_by_default
    product = get_object_or_404(Product.objects.all(), pk=product_pk)
    variant = ProductVariant(product=product, track_inventory=track_inventory)
    form = ProductVariantForm(
        request.POST or None,
        instance=variant)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Saved variant %s') % (variant.name,)
        messages.success(request, msg)
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'form': form, 'product': product, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def variant_edit(request, product_pk, variant_pk):
    product = get_object_or_404(Product.objects.all(), pk=product_pk)
    variant = get_object_or_404(product.variants.all(), pk=variant_pk)
    form = ProductVariantForm(request.POST or None, instance=variant)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Saved variant %s') % (variant.name,)
        messages.success(request, msg)
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'form': form, 'product': product, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def variant_delete(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(product.variants, pk=variant_pk)
    if request.method == 'POST':
        variant.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed variant %s') % (variant.name,)
        messages.success(request, msg)
        return redirect('dashboard:product-details', pk=product.pk)
    ctx = {
        'is_only_variant': product.variants.count() == 1, 'product': product,
        'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/modal/confirm_delete.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def variant_images(request, product_pk, variant_pk):
    product = get_object_or_404(Product, pk=product_pk)
    qs = product.variants.prefetch_related('images')
    variant = get_object_or_404(qs, pk=variant_pk)
    form = VariantImagesSelectForm(request.POST or None, variant=variant)
    if form.is_valid():
        form.save()
        return redirect(
            'dashboard:variant-details', product_pk=product.pk,
            variant_pk=variant.pk)
    ctx = {'form': form, 'product': product, 'variant': variant}
    return TemplateResponse(
        request,
        'dashboard/product/product_variant/modal/select_images.html',
        ctx)


#@staff_member_required
def ajax_available_variants_list(request):
    """Return variants filtered by request GET parameters.

    Response format is that of a Select2 JS widget.
    """
    available_products = Product.objects.available_products().prefetch_related(
        'category',
        'product_type__product_attributes')
    queryset = ProductVariant.objects.filter(
        product__in=available_products).prefetch_related(
            'product__category',
            'product__product_type__product_attributes')

    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(sku__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(product__name__icontains=search_query))

    variants = [
        {'id': variant.id, 'text': variant.get_ajax_label(request.discounts)}
        for variant in queryset]
    return JsonResponse({'results': variants})


#@staff_member_required
#@permission_required('product.manage_products')
def product_images(request, product_pk):
    products = Product.objects.prefetch_related('images')
    product = get_object_or_404(products, pk=product_pk)
    images = product.images.all()
    ctx = {
        'product': product, 'images': images, 'is_empty': not images.exists()}
    return TemplateResponse(
        request, 'dashboard/product/product_image/list.html', ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_image_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product_image = ProductImage(product=product)
    form = ProductImageForm(
        request.POST or None, request.FILES or None, instance=product_image)
    if form.is_valid():
        product_image = form.save()
        msg = pgettext_lazy(
            'Dashboard message',
            'Added image %s') % (product_image.image.name,)
        messages.success(request, msg)
        return redirect('dashboard:product-image-list', product_pk=product.pk)
    ctx = {'form': form, 'product': product, 'product_image': product_image}
    return TemplateResponse(
        request,
        'dashboard/product/product_image/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_image_edit(request, product_pk, img_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product_image = get_object_or_404(product.images, pk=img_pk)
    form = ProductImageForm(
        request.POST or None, request.FILES or None, instance=product_image)
    if form.is_valid():
        product_image = form.save()
        msg = pgettext_lazy(
            'Dashboard message',
            'Updated image %s') % (product_image.image.name,)
        messages.success(request, msg)
        return redirect('dashboard:product-image-list', product_pk=product.pk)
    ctx = {'form': form, 'product': product, 'product_image': product_image}
    return TemplateResponse(
        request,
        'dashboard/product/product_image/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def product_image_delete(request, product_pk, img_pk):
    product = get_object_or_404(Product, pk=product_pk)
    image = get_object_or_404(product.images, pk=img_pk)
    if request.method == 'POST':
        image.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed image %s') % (image.image.name,)
        messages.success(request, msg)
        return redirect('dashboard:product-image-list', product_pk=product.pk)
    return TemplateResponse(
        request,
        'dashboard/product/product_image/modal/confirm_delete.html',
        {'product': product, 'image': image})


@require_POST
#@staff_member_required
def ajax_reorder_product_images(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = ReorderProductImagesForm(request.POST, instance=product)
    status = 200
    ctx = {}
    if form.is_valid():
        form.save()
    elif form.errors:
        status = 400
        ctx = {'error': form.errors}
    return JsonResponse(ctx, status=status)


@require_POST
#@staff_member_required
def ajax_upload_image(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = UploadImageForm(
        request.POST or None, request.FILES or None, product=product)
    ctx = {}
    status = 200
    if form.is_valid():
        image = form.save()
        ctx = {'id': image.pk, 'image': None, 'order': image.sort_order}
    elif form.errors:
        status = 400
        ctx = {'error': form.errors}
    return JsonResponse(ctx, status=status)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_list(request):
    attributes = (
        Attribute.objects.prefetch_related(
            'values', 'product_type', 'product_variant_type').order_by('name'))
    attribute_filter = AttributeFilter(request.GET, queryset=attributes)
    attributes = [(
        attribute.pk, attribute.name,
        attribute.product_type or attribute.product_variant_type,
        attribute.values.all()) for attribute in attribute_filter.qs]
    attributes = get_paginator_items(
        attributes, settings.DASHBOARD_PAGINATE_BY, request.GET.get('page'))
    ctx = {
        'attributes': attributes,
        'filter_set': attribute_filter,
        'is_empty': not attribute_filter.queryset.exists()}
    return TemplateResponse(
        request, 'dashboard/product/attribute/list.html', ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_details(request, pk):
    attributes = Attribute.objects.prefetch_related(
        'values', 'product_type', 'product_variant_type').all()
    attribute = get_object_or_404(attributes, pk=pk)
    product_type = attribute.product_type or attribute.product_variant_type
    values = attribute.values.all()
    ctx = {
        'attribute': attribute, 'product_type': product_type, 'values': values}
    return TemplateResponse(
        request, 'dashboard/product/attribute/detail.html', ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_create(request):
    attribute = Attribute()
    form = AttributeForm(request.POST or None, instance=attribute)
    if form.is_valid():
        attribute = form.save()
        msg = pgettext_lazy('Dashboard message', 'Added attribute')
        messages.success(request, msg)
        return redirect('dashboard:attribute-details', pk=attribute.pk)
    ctx = {'attribute': attribute, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/attribute/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_edit(request, pk):
    attribute = get_object_or_404(Attribute, pk=pk)
    form = AttributeForm(request.POST or None, instance=attribute)
    if form.is_valid():
        attribute = form.save()
        msg = pgettext_lazy('Dashboard message', 'Updated attribute')
        messages.success(request, msg)
        return redirect('dashboard:attribute-details', pk=attribute.pk)
    ctx = {'attribute': attribute, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/attribute/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_delete(request, pk):
    attribute = get_object_or_404(Attribute, pk=pk)
    if request.method == 'POST':
        attribute.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed attribute %s') % (attribute.name,)
        messages.success(request, msg)
        return redirect('dashboard:attributes')
    return TemplateResponse(
        request,
        'dashboard/product/attribute/modal/'
        'attribute_confirm_delete.html',
        {'attribute': attribute})


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_value_create(request, attribute_pk):
    attribute = get_object_or_404(Attribute, pk=attribute_pk)
    value = AttributeValue(attribute_id=attribute_pk)
    form = AttributeValueForm(request.POST or None, instance=value)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added attribute\'s value')
        messages.success(request, msg)
        return redirect('dashboard:attribute-details', pk=attribute_pk)
    ctx = {'attribute': attribute, 'value': value, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/attribute/values/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_value_edit(request, attribute_pk, value_pk):
    attribute = get_object_or_404(Attribute, pk=attribute_pk)
    value = get_object_or_404(AttributeValue, pk=value_pk)
    form = AttributeValueForm(request.POST or None, instance=value)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated attribute\'s value')
        messages.success(request, msg)
        return redirect('dashboard:attribute-details', pk=attribute_pk)
    ctx = {'attribute': attribute, 'value': value, 'form': form}
    return TemplateResponse(
        request,
        'dashboard/product/attribute/values/form.html',
        ctx)


#@staff_member_required
#@permission_required('product.manage_products')
def attribute_value_delete(request, attribute_pk, value_pk):
    value = get_object_or_404(AttributeValue, pk=value_pk)
    if request.method == 'POST':
        value.delete()
        msg = pgettext_lazy(
            'Dashboard message',
            'Removed attribute\'s value %s') % (value.name,)
        messages.success(request, msg)
        return redirect('dashboard:attribute-details', pk=attribute_pk)
    return TemplateResponse(
        request,
        'dashboard/product/attribute/values/modal/confirm_delete.html',
        {'value': value, 'attribute_pk': attribute_pk})


#@staff_member_required
#@permission_required('product.manage_products')
def ajax_reorder_attribute_values(request, attribute_pk):
    attribute = get_object_or_404(Attribute, pk=attribute_pk)
    form = ReorderAttributeValuesForm(
        request.POST, instance=attribute)
    status = 200
    ctx = {}
    if form.is_valid():
        form.save()
    elif form.errors:
        status = 400
        ctx = {'error': form.errors}
    return JsonResponse(ctx, status=status)
