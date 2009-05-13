from django.contrib import admin
from broadcastcms.shortcuts import comma_seperated_admin_links
from django.db import models

from broadcastcms.workflow.admin import WorkflowedObjectAdmin

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

#class ContentBaseAdminManager(models.Manager):
#
#    def __init__(self, model, *args, **kwargs):
#        self.model = model
#        super(ContentBaseAdminManager, self).__init__(*args, **kwargs)
#    
#    def get_query_set(self):
#        return super(ContentBaseAdminManager, self).get_query_set()


class ContentBaseAdmin(WorkflowedObjectAdmin):
    list_display = ('title', 'description', comma_seperated_admin_label_links, 'is_public')

    #def __init__(self, *args, **kwargs):
    #    super(ContentBaseAdmin, self).__init__(*args, **kwargs)
    #    if not getattr(self.model, 'admin_objects', None):
    #        self.model.add_to_class('admin_objects', models.Manager())

    #def queryset(self, request):
    #    """
    #    Returns a QuerySet of all model instances that can be edited by the
    #    admin site. This is used by changelist_view.
    #    """

    #    #self.model.admin_objects = models.Manager()

    #    qs = self.model.admin_objects.get_query_set()
    #    # TODO: this should be handled by some parameter to the ChangeList.
    #    ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
    #    if ordering:
    #        qs = qs.order_by(*ordering)
    #    return qs
