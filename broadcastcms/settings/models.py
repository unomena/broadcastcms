from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Setting(models.Model):
    TYPE_CHOICES = (
        ('n', 'Number'),
        ('t', 'Text'),
        ('o', 'Object'),
    )

    name = models.CharField(max_length=255, unique=True)
    type = models.CharField('Type', max_length=1, choices=TYPE_CHOICES, default='n', blank=False)
    int_value = models.IntegerField('Integer Value', blank=True, null=True)
    text_value = models.TextField('Text Value', blank=True, null=True)
    object_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_value = generic.GenericForeignKey('object_type', 'object_id')

    def __unicode__(self):
        return self.name

    def getvalue(self):
        if self.type == 'n': return self.int_value
        elif self.type == 't': return self.text_value
        elif self.type == 'o': return self.object_value
        else: return None

    def setvalue(self, value):
        if self.type == 'n': self.int_value = value
        elif self.type == 't': self.text_value = value
        elif self.type == 'o': self.object_value = value
        else: return None

    value = property(getvalue, setvalue)
