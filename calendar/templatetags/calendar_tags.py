from django import template

register = template.Library()

class EntryLengthNode(template.Node):
    def __init__(self, obj):
        self.obj = template.Variable(obj)

    def render(self, context):
        obj = self.obj.resolve(context)
        length = obj.end_date_time - obj.start_date_time
        return length.seconds / 60

@register.tag       
def entry_length(parser, token):
    tag_name, obj = token.split_contents()
    return EntryLengthNode(obj)
