from broadcastcms.base.models import ContentBase


class setupSection(object):
    def __init__(self, view_template, view_class=None):
        self.view_template = view_template
        self.view_class = view_class

    def __call__(self, f):
        def wrapped_f(request, id=None):
            if id:
                instance = ContentBase.objects.get(pk=id)
                instance = instance.as_leaf_class()
            else:
                instance = self.view_class

            return f(request, template=self.view_template, instance=instance)
        return wrapped_f
