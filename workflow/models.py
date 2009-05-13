from django.db import models

class WorkflowedObject(models.Model):
    public = models.BooleanField(default=False)

    class Meta:
        abstract = True
