from django.utils.translation import pgettext_lazy


class ShippingMethodType:
    PRICE_BASED = 'price'
    WEIGHT_BASED = 'weight'

    CHOICES = [
        (PRICE_BASED, pgettext_lazy(
            'Type of shipping', 'Price based shipping')),
        (WEIGHT_BASED, pgettext_lazy(
            'Type of shipping', 'Weight based shipping'))]

class ShippingPaymentStatus:
    REFUNDED = 'refunded'
    PENDING = 'pending'
    PAID = 'paid'

    CHOICES = [
        (REFUNDED, pgettext_lazy(
            'Status for a REFUNDED order',
            'refunded')),
        (PENDING, pgettext_lazy(
            'Status for an order which has not yet been paid for',
            'pending')),
        (PAID, pgettext_lazy(
            'Status for an order which has been PAID',
            'paid'))]