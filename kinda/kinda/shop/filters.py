from django import forms
from django.utils.translation import npgettext, pgettext_lazy
from django_filters import (
    CharFilter, ChoiceFilter, ModelMultipleChoiceFilter, OrderingFilter,
    RangeFilter)

from ..core.filters import SortedFilterSet
from ..product.models import Category, Attribute #Product, ProductType 
from ..shop.models import Shop
#from ..widgets import MoneyRangeWidget

SHOP_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Shop list sorting option', 'name')}
    #'price': pgettext_lazy('Product type list sorting option', 'price')

SHOP_ATTRIBUTE_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Shop attribute list sorting option', 'name')}

CATEGORY_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Category list sorting option', 'name')}

PUBLISHED_CHOICES = (
    ('1', pgettext_lazy('Is publish filter choice', 'Published')),
    ('0', pgettext_lazy('Is publish filter choice', 'Not published')))


class ShopFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Shop list filter label', 'Name'),
        lookup_expr='icontains')
    category = ModelMultipleChoiceFilter(
        label=pgettext_lazy('Shop list filter label', 'Category'),
        field_name='category',
        queryset=Category.objects.all())
    #product_type = ModelMultipleChoiceFilter(
    #    label=pgettext_lazy('Product list filter label', 'Product type'),
    #    field_name='product_type',
    #    queryset=ProductType.objects.all())
    #price = RangeFilter(
    #    label=pgettext_lazy('Product list filter label', 'Price'),
    #    field_name='price',
    #    widget=MoneyRangeWidget)
    is_published = ChoiceFilter(
        label=pgettext_lazy('Shop list filter label', 'Is published'),
        choices=PUBLISHED_CHOICES,
        empty_label=pgettext_lazy('Filter empty choice label', 'All'),
        widget=forms.Select)
    sort_by = OrderingFilter(
        label=pgettext_lazy('Shop list filter label', 'Sort by'),
        fields=SHOP_SORT_BY_FIELDS.keys(),
        field_labels=SHOP_SORT_BY_FIELDS)

    class Meta:
        model = Shop
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            'Number of matching records in the dashboard shop list',
            'Found %(counter)d matching shop',
            'Found %(counter)d matching shops',
            number=counter) % {'counter': counter}


class AttributeFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Attribute list filter label', 'Name'),
        lookup_expr='icontains')
    sort_by = OrderingFilter(
        label=pgettext_lazy('Attribute list filter label', 'Sort by'),
        fields=CATEGORY_SORT_BY_FIELDS.keys(),
        field_labels=CATEGORY_SORT_BY_FIELDS)

    class Meta:
        model = Attribute
        fields = []

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            'Number of matching records in the dashboard attributes list',
            'Found %(counter)d matching attribute',
            'Found %(counter)d matching attributes',
            number=counter) % {'counter': counter}


class CategoryFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Category list filter label', 'Name'),
        lookup_expr='icontains')
    sort_by = OrderingFilter(
        label=pgettext_lazy('Category list filter label', 'Sort by'),
        fields=CATEGORY_SORT_BY_FIELDS.keys(),
        field_labels=CATEGORY_SORT_BY_FIELDS)
    product_attributes = ModelMultipleChoiceFilter(
        label=pgettext_lazy(
            'Product type list filter label', 'Product attributes'),
        field_name='product_attributes',
        queryset=Attribute.objects.all())
    #variant_attributes = ModelMultipleChoiceFilter(
    #    label=pgettext_lazy(
    #        'Product type list filter label', 'Variant attributes'),
    #    field_name='variant_attributes',
    #    queryset=Attribute.objects.all())

    class Meta:
        model = Category
        fields = ['name'] #'product_attributes', 'variant_attributes'

    def get_summary_message(self):
        counter = self.qs.count()
        return npgettext(
            'Number of matching records in the dashboard Category list',
            'Found %(counter)d matching category',
            'Found %(counter)d matching categories',
            number=counter) % {'counter': counter}
	#
	#
	#