from django.db import models
from broadcastcms.base.models import ModelBase

class Page(ModelBase):
    title = models.CharField(
        max_length='256', help_text='A short descriptive title.'
    )
    query = models.TextField(
        help_text='Query used to populate this page.',
        blank=True,
        null=True,
    )
    menu = models.CharField(
        max_length='256', help_text='Menu to use for this page.',
        blank=True,
        null=True,
    )
    view = models.CharField(
        max_length='256', help_text='View to use for this page.',
        blank=True,
        null=True,
    )

    def get_queryset(self, context):
        query = self.query.replace('\r\n', '\n')
        compiled_query = compile(query, '<string>', 'exec')
        exec compiled_query
        return queryset

    def get_menu(self, request):
        """
        """
        from broadcastcms.lite.utils import *
        if self.menu:
            class_name = self.menu.replace('\r\n', '\n')
            compiled_class_name = compile(class_name, '<string>', 'eval')
            return eval(compiled_class_name)(request)
        else:
            return None
    
    def __unicode__(self):
        return self.title


class OutgoingPage(models.Model):
    content_type = models.CharField(max_length='256')
    page = models.ForeignKey(Page, related_name='outgoing_pages')
    outgoing_page = models.ForeignKey(Page, related_name='outgoing_page')
