from django.core.cache import cache
    

def get_inclusion_view_function_cache_key(node, context, respect_path, f):
    key = str(node.__class__) + str(f.__name__)
    if respect_path:
        request = context['request']
        path_info = request.META['PATH_INFO']
        key += path_info
    key = key.replace(' ', '')
    return key

def cache_inclusion_view_function(seconds, respect_path=False):
    def wrap(f):
        def wrap_f(self, context):
            key = get_inclusion_view_function_cache_key(self, context, respect_path, f)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(self, context)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap
