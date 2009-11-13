import datetime

from django import template

register = template.Library()

@register.tag
def smart_query_string(parser, token):
    args = token.split_contents()
    additions = args[1:]
   
    addition_pairs = []
    while additions:
        addition_pairs.append(additions[0:2])
        additions = additions[2:]

    return SmartQueryStringNode(addition_pairs)


class SmartQueryStringNode(template.Node):
    def __init__(self, addition_pairs):
        self.addition_pairs = []
        for key, value in addition_pairs:
            self.addition_pairs.append((template.Variable(key) if key else None, template.Variable(value) if value else None))

    def render(self, context):
        q = dict([(k, v) for k, v in context['request'].GET.items()])
        for key, value in self.addition_pairs:
            if key:
                key = key.resolve(context)
                if value:
                   value = value.resolve(context)
                   q[key] = value
                else:
                    q.pop(key, None)
            qs = '&amp;'.join(['%s=%s' % (k, v) for k, v in q.items()])
        return '?' + qs if len(q) else ''
    
    
@register.tag
def get_time_difference(parser, token):
    try:
        tag_name, obj_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires exactly one argument" % token.contents
    
    return HumanizeTimeDifference(obj_name)

class HumanizeTimeDifference(template.Node):
    """
    Adapted from Django Snippet 412
    
    Returns a humanized string representing time difference
    between now() and the input timestamp.
    
    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    def __init__(self, obj_name):
        self.obj_name = obj_name

    def render(self, context):
        time_difference = datetime.datetime.now() - context[self.obj_name].created
        days = time_difference.days
        hours = time_difference.seconds / 3600
        minutes = time_difference.seconds % 3600 / 60
        seconds = time_difference.seconds % 3600 % 60
        
        if days > 0:
            if days == 1: return 'Yesterday'
            else: dt_str = "Days"
            return "%s %s" % (days, dt_str)
        elif hours > 0:
            if hours == 1: dt_str = "Hour"
            else: dt_str = "Hours"
            return "%s %s" % (hours, dt_str)
        elif minutes > 0:
            if minutes == 1: dt_str = "Min"
            else: dt_str = "Mins"
            return "%s %s" % (minutes, dt_str)
        elif seconds > 0:
            if seconds == 1: dt_str = "Sec"
            else: dt_str = "Secs"
            return "%s %s" % (seconds, dt_str)
        else:
            return ""

