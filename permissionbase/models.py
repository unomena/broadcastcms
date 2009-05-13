from django.db import models
from django.template import Context

class PermissionManager(models.Manager):
    """
    This manager in the form of Model.permitted_objects is to be used as main object query instead of conventional Model.objects, as it pre-filters objects to exclude those not accessable by the current user
    TODO: Implement actual permissions, currently its a simple is_public check.
    """
    def get_query_set(self):
        return super(PermissionManager, self).get_query_set().filter(is_public=True)

class PermissionBase(models.Model):
    is_public = models.BooleanField(default=False, verbose_name="Public")
    
    class Meta():
        abstract = True
