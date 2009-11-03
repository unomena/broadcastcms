from django.db import models


class StatusUpdateManger(models.Manager):
    def current_status(self, user):
        try:
            return self.filter(user=user)[0]
        except IndexError:
            return None
