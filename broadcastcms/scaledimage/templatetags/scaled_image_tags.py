from django import template

register = template.Library()

class ScaledImageURLNode(template.Node):
    def __init__(self, obj, width=None, height=None):
        self.obj = template.Variable(obj)
        self.width = width
        self.height = height

    def render(self, context):
        width, height = self.width, self.height
        obj = self.obj.resolve(context)
        image = obj.image
        original_url = image.url
        if width and height:
            if '.' in original_url:
                dot_index = original_url.rindex('.')
                scaled_name = '%sx%s%s' % (width, height, original_url[dot_index:])
            else:
                scaled_name = '%sx%s' % (width, height)
            scaled_url = '%s/%s' % ('/'.join(original_url.split('/')[:-1]), scaled_name)
            return scaled_url
        else:
            return original_url

@register.tag       
def scaled_image_url(parser, token):
    token = token.split_contents()
    if len(token) == 2:
        return ScaledImageURLNode(token[1])
    elif len(token) == 4:
        return ScaledImageURLNode(*token[1:3])
    else:
        raise Exception('%s tag requires either 3 or 1 arguments (obj, width, height)' % token[0])
