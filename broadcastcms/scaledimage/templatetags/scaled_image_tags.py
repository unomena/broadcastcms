from django import template


register = template.Library()


class ScaledImageURLNode(template.Node):
    def __init__(self, obj, width=None, height=None):
        self.obj = template.Variable(obj)

        try:
            self.width = int(width)
        except ValueError:
            self.width = template.Variable(width)
        try:
            self.height = int(height)
        except ValueError:
            self.height = template.Variable(height)

    def render(self, context):
        
        width, height = self.width, self.height
        if isinstance(self.width, int):
            width = self.width
        else:
            width = self.width.resolve(context)
        
        if isinstance(self.height, int):
            height = self.height
        else:
            height = self.height.resolve(context)
            
        obj = self.obj.resolve(context)
        image = obj.image
        try:
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
        except:
            return ''


@register.tag       
def scaled_image_url(parser, token):
    token = token.split_contents()
    if len(token) == 2:
        return ScaledImageURLNode(token[1])
    elif len(token) == 4:
        return ScaledImageURLNode(*token[1:4])
    else:
        raise Exception('%s tag requires either 1 or 3 arguments (obj, width, height)' % token[0])
