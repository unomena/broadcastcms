from django.db import models

from broadcastcms.base.admin import ModelBaseStackedInline

from models import Image


class ImageInline(ModelBaseStackedInline):
    model = Image
    extra = 1
