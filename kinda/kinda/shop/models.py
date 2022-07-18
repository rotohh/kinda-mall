from decimal import Decimal
from operator import attrgetter
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ExpressionWrapper, F, Max, Sum
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_measurement.models import MeasurementField
from django_prices.models import MoneyField, TaxedMoneyField
from measurement.measures import Weight
from text_unidecode import unidecode
from prices import Money
from ..core.models import SortableModel

from django.conf import settings
#from . import FulfillmentStatus, OrderEvents, OrderStatus, display_order_event
#from ..account.models import Address
#from ..core.utils.json_serializer import CustomJsonEncoder
#from ..core.utils.taxes import ZERO_TAXED_MONEY, zero_money
#from ..core.weight import WeightUnits, zero_weight
#from ..discount.models import Voucher
#from ..payment import ChargeStatus, TransactionKind
#from ..shipping.models import ShippingMethod
#from ..product.models import Category
from versatileimagefield.fields import PPOIField, VersatileImageField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from .validators import validate_possible_number

class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class Shop(models.Model):
    shop_name = models.CharField(max_length=256) #, blank=True
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='shop',
        on_delete=models.SET_NULL)
    shop_link = models.URLField(max_length=200, blank=True, null=True)
    logo = VersatileImageField(
        upload_to='logos', blank=True, null=True)
    logo_alt = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True, null=True)
    phone = PossiblePhoneNumberField()    
    city = models.CharField(max_length=256)
    street_address = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    #location =
		
    class Meta:
        ordering = ('pk', )
	
    def __str__(self):
        return self.shop_name

    def get_absolute_url(self):
        return reverse(
            'shop:shop-details',
            kwargs={'slug': self.get_slug(), 'shop_pk': self.id})

    def get_slug(self):
        return slugify(smart_text(unidecode(self.shop_name)))

#class ShopCategory(models.Model):
 #   name = models.CharField(max_length=128)
 #   shop = models.ForeignKey(
  #      Shop, related_name='categories', on_delete=models.CASCADE, null=True, blank=True)
    
    
	
   # def __str__(self):
    #    return self.name	
    
	