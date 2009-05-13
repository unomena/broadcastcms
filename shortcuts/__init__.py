def get_obj_admin_path(obj):
    """
    Returns the root relative URL to the object in the Django admin site.
    Semi hardcoded for now until per view admin urlresolvers are implimented, see:
    http://docs.djangoproject.com/en/dev/ref/contrib/admin/#ref-contrib-admin
    """
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(obj)
    return '/admin/%s/%s/%s' % (content_type.app_label, content_type.model, str(obj.pk))

def comma_seperated_admin_links(objs):
    """
    Returns an HTML formatted string of links to object admin pages.
    Requires obects to have titles
    """
    anchors = []
    for obj in objs:
        anchors.append('<a href="%s">%s</a>' % (get_obj_admin_path(obj), obj.title))
    return ', '.join(anchors)    
