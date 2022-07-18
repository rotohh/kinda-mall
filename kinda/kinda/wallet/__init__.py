from django.utils.translation import pgettext_lazy


class ShippingPaymentStatus:
    PENDING = 'pending'
    PAID = 'paid'

    CHOICES = [
        (PENDING, pgettext_lazy(
            'Status for an order which has not yet been paid for',
            'pending')),
        (PAID, pgettext_lazy(
            'Status for an order which has been PAID',
            'paid'))]

class OrderPaymentStatus:
    PENDING = 'pending'
    PAID = 'paid'

    CHOICES = [
        (PENDING, pgettext_lazy(
            'Status for an order which has not yet been paid for',
            'pending')),
        (PAID, pgettext_lazy(
            'Status for an order which has been PAID',
            'paid'))]