from django.db import models

class LabelQuerySet(models.query.QuerySet):
    def visible(self):
        return self.filter(is_visible=True)

class LabelManager(models.Manager):
    def get_query_set(self):
        return LabelQuerySet(self.model)

    def visible(self):
        return self.get_query_set().visible()
