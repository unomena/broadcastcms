from django.db import models

from broadcastcms.workflow.models import WorkflowedObject
from broadcastcms.label.models import Label

class ContentBase(WorkflowedObject):
    title = models.CharField(max_length='512')
    description = models.TextField()
    labels = models.ManyToManyField(Label, blank=True)
