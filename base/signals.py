from django.db.models import signals
from models import PermissionManager

def ensure_permitted_objects(sender, **kwargs):
    sender.add_to_class('permitted_objects', PermissionManager())

signals.class_prepared.connect(ensure_permitted_objects)
