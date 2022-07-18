from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils import timezone
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from decimal import Decimal
import datetime

from .validators import validate_possible_number

from ..order.models import Order, SubOrder
from ..shop.models import Shop
from . import ShippingPaymentStatus, OrderPaymentStatus

class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class PaymentsTemporary(models.Model):
    #order = models.IntegerField(blank=True, null=True)
    order = models.OneToOneField(
        Order, blank=True, null=True, related_name='temppayments',
        on_delete=models.SET_NULL)
    shipping_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))
    order_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))
    shipping_payment_status = models.CharField(
        max_length=32, default=ShippingPaymentStatus.PENDING,
        choices=ShippingPaymentStatus.CHOICES)
    order_payment_status = models.CharField(
        max_length=32, default=OrderPaymentStatus.PENDING,
        choices=OrderPaymentStatus.CHOICES)
    ref_number_shipping = models.CharField(max_length=100, blank=True)
    ref_number_order = models.CharField(max_length=100, blank=True)
	
    class Meta:
        ordering = ('-pk', )

    @receiver(post_save, sender=Order)
    def create_payments(sender, instance, created, **kwargs):
        if created:
            PaymentsTemporary.objects.create(order=instance) 
	
class MpesaPayments(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='mpesa',
        on_delete=models.SET_NULL)

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='wallet',
        on_delete=models.SET_NULL)
    phone = PossiblePhoneNumberField(blank=True, default='')
    name = models.CharField(max_length=256, blank=True)
    wallet_balance = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))

class CommissionPayments(models.Model):
    created_time = models.DateTimeField(default=timezone.now, editable=False)
    order = models.OneToOneField(
        Order, related_name='commissions',
        on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=256, blank=True)
    amount =  models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))
class ShippingPayments(models.Model):
    created_time = models.DateTimeField(default=timezone.now, editable=False)
    order = models.OneToOneField(
        Order, related_name='shipping',
        on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=256, blank=True)
    amount =  models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))

class SuborderPayments(models.Model):
    created_time = models.DateTimeField(default=timezone.now, editable=False)
    order = models.ForeignKey(
        Order, related_name='suborder',
        on_delete=models.CASCADE)
    suborder = models.ForeignKey(
        SubOrder, related_name='suborder',
        on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=256, blank=True)
    shop = models.ForeignKey(
        Shop, related_name='shop',
        on_delete=models.CASCADE)
    amount =  models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal('0.0'))

