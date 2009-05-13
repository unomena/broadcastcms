from django.db import models

class WorkflowedObject(model.Models):
    public = models.BooleanField(default=False)

    class Meta:
        abstract = True
