from django import template


register = template.Library()


class CallViewNode(template.Node):
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def render(self, context):
        instance = self.instance.resolve(context)
        return getattr(instance, self.method)(context)


@register.tag
def call_view(parser, token):
    tag_name, instance_str, method = token.split_contents()
    instance = template.Variable(instance_str)
    return CallViewNode(instance, method)
