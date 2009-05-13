from django.db import models
from django.template import Context

class WorkflowedObjectManager(models.Manager):

    def get_query_set(self):
        return super(WorkflowedObjectManager, self).get_query_set().filter(is_public=True)

class WorkflowedObject(models.Model):
    is_public = models.BooleanField(default=False, verbose_name="Public")
    objects = WorkflowedObjectManager() 

    class Meta:
        abstract = True
