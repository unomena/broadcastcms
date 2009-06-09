from broadcastcms.base.models import ContentBase


class setupView(object):
    def __init__(self, template=None, view_class=None):
        self.template = template
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

            return f(request, context, template=self.template, *args, **kwargs)
        return wrapped_f
