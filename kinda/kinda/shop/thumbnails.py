from celery import shared_task

from ..core.utils import create_thumbnails
from .models import Category, ShopImage #, Collection


@shared_task
def create_shop_thumbnails(image_id):
    """Takes a ShopImage model, and creates thumbnails for it."""
    create_thumbnails(pk=image_id, model=ShopImage, size_set='shops')

#{% if shop_categories %} {% endif %}

#@shared_task
#def create_category_background_image_thumbnails(category_id):
#    """Takes a Product model,
#    and creates the background image thumbnails for it."""
#    create_thumbnails(
#        pk=category_id, model=Category,
#        size_set='background_images', image_attr='background_image')


#@shared_task
#def create_collection_background_image_thumbnails(collection_id):
#    """Takes a Collection model,
#    and creates the background image thumbnails for it."""
#    create_thumbnails(
#        pk=collection_id, model=Collection,
#        size_set='background_images', image_attr='background_image')
