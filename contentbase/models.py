from django.db import models

def ContentBase(models.Model):
    title = models.CharField(max_length='512')
    description = models.TextField()

    class Meta:
        abstract = True
