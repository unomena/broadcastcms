from django import template

register = template.Library()

class ScaledImageURLNode(template.Node):
    def __init__(self, obj, width, height):
        self.obj = template.Variable(obj)
        self.width = width
        self.height = height

    def render(self, context):
        obj = self.obj.resolve(context)
        image = obj.image
        try:
            original_url = image.url
        except ValueError:
            original_url = None
        if original_url:
            if '.' in original_url:
                dot_index = original_url.rindex('.')
                scaled_url = '%s%sx%s%s' % (original_url[:dot_index], self.width, self.height, original_url[dot_index:])
            else:
                scaled_url = '%s%sx%s' % (original_url, self.width, self.height)

            return scaled_url
        return ''

@register.tag       
def scaled_image_url(parser, token):
    tag_name, obj, width, height = token.split_contents()
    return ScaledImageURLNode(obj, width, height)
