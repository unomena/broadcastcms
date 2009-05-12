from django.db import models

class Label(models.Model):
    title = models.CharField(max_length='64')
    visible = models.BooleanField()

    class Meta():
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'

    def __unicode__(self):
        return str(self.title)
