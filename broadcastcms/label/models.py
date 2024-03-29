from django.db import models

from broadcastcms.fields import modelfields
from broadcastcms.base.models import slugify

from managers import LabelManager

class Label(models.Model):
    objects = LabelManager()

    slug = models.SlugField(
        editable=False,
        max_length='275',
    )
    title = models.CharField(
        max_length='64', 
        help_text='A short descriptive title.'
    )
    restricted_to = modelfields.CommaSeperatedCharField(
        blank=True, 
        help_text="Field(s) to which this label will be restricted. This allows you to have per type/field specific labels. So for instance if you select 'Show - Labels' this label will only be available for shows under labels."
    )
    is_visible = models.BooleanField(
        default=True, 
        verbose_name='Visible', 
        help_text="Check to make this label visible to the public. Labels that are not visible will never be displayed on the public facing portal."
    )

    class Meta():
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self)
        super(Label, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for related in self._meta.get_all_related_objects():
            field = getattr(self, related.get_accessor_name())
            field.clear()
        super(Label, self).delete(*args, **kwargs)
