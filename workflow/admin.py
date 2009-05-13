from django.contrib import admin
from django.db import models

class WorkflowedObjectAdmin(admin.ModelAdmin):
    """
    Admin pages should list all objects, not just public ones. 
    TODO: Find a better solution than temporarily changing the default_manager.
    """
    
    def __init__(self, *args, **kwargs):
        super(WorkflowedObjectAdmin, self).__init__(*args, **kwargs)
        if not getattr(self.model, 'admin_objects', None):
            self.model.add_to_class('admin_objects', models.Manager())
    
    def queryset(self, request):
        current_manager = self.model._default_manager
        try:
            self.model._default_manager = self.model.admin_objects
            return super(WorkflowedObjectAdmin, self).queryset(request)
        finally:
            self.model._default_manager = current_manager

    def change_view(self, request, object_id, extra_context=None):
        current_manager = self.model._default_manager
        try:
            self.model._default_manager = self.model.admin_objects
            return super(WorkflowedObjectAdmin, self).change_view(request, object_id, extra_context)
        finally:
            self.model._default_manager = current_manager

    def delete_view(self, request, object_id, extra_context=None):
        current_manager = self.model._default_manager
        try:
            self.model._default_manager = self.model.admin_objects
            return super(WorkflowedObjectAdmin, self).delete_view(request, object_id, extra_context)
        finally:
            self.model._default_manager = current_manager
