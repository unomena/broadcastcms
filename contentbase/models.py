from django.db import models
from broadcastcms.label.models import Label

class ContentBase(models.Model):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label)
