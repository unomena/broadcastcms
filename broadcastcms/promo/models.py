from django.db import models
from django.db.models.query import Q

from broadcastcms.base.models import ModelBase, ContentBase

class PromoWidget(ModelBase):
    title = models.CharField(max_length=255)
    class Meta:
        verbose_name = 'Promo Widget'
        verbose_name_plural = 'Promo Widgets'

class PromoWidgetSlot(ModelBase):
    title = models.CharField(max_length=255)
    widget = models.ForeignKey(PromoWidget)
    content = models.ForeignKey(
        ContentBase,
        limit_choices_to = ~Q(classname__in=['PromoWidget', 'PromoWidgetSlot', 'ModelBase', 'ContentBase',]) & Q(is_public=True),
        related_name="slot_content",
    )
    class Meta:
        verbose_name = 'Promo Widget Slot'
        verbose_name_plural = 'Promo Widget Slots'
