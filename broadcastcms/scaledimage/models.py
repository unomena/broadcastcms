from django.db import models

from broadcastcms.base.models import ModelBase

from fields import ScaledImageField


class Image(ModelBase):
    image = ScaledImageField()
