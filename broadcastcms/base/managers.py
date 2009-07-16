from django.db import models


class ModelBaseQuerySet(models.query.QuerySet):
    def permitted(self):
        return self.filter(is_public=True)


class ModelBaseManager(models.Manager):
    """
    This manager adds BroadcastCMS specific queryset behaviour to all objects.
    """

    use_for_related_fields = True

    def get_query_set(self):
        return ModelBaseQuerySet(self.model)


class PermittedManager(ModelBaseManager):
    def get_query_set(self):
        return super(PermittedManager, self).get_query_set().permitted()
