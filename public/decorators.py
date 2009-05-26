from broadcastcms.base.models import ContentBase


class setupSection(object):
    def __init__(self, view_template, view_class=None):
        self.view_template = view_template
        self.view_class = view_class

    def __call__(self, f):
        def wrapped_f(request, *args, **kwargs):
            instance_id = kwargs.get('instance_id', None)
            if instance_id:
                instance = ContentBase.objects.get(pk=instance_id)
                instance = instance.as_leaf_class()
            else:
                instance = self.view_class

            context = {
                'request': request,
                'instance': instance,
            }

            return f(request, context, template=self.view_template, *args, **kwargs)
        return wrapped_f
