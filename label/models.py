from django.db import models
from broadcastcms.fields import modelfields

class Label(models.Model):
    title = models.CharField(max_length='64')
    restricted_to = modelfields.CommaSeperatedCharField(blank=True)
    is_visible = models.BooleanField(default=True, verbose_name='Visible')

    class Meta():
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'

    def __unicode__(self):
        return str(self.title)
