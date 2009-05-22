from django.db import models

class Label(models.Model):
    title = models.CharField(max_length='64')
    is_visible = models.BooleanField(default=True)

    class Meta():
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'

    def __unicode__(self):
        return str(self.title)
