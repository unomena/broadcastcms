from django.core.cache import cache
    

def get_inclusion_view_function_cache_key(node, context, respect_path, respect_get, f):
    """
    TODO: Refactor to generate keys more succinctly.
    """
    key = str(node.__class__) + str(f.__name__)
    request = context['request']
    if respect_path:
        path_key = str(request.path)
        key += path_key
    if respect_get:
        #TODO: Generate a proper get_key instead of a simple string
        get_key = str(request.GET)
        key += get_key
    
    key = key.replace(' ', '')
    return key

def cache_inclusion_view_function(seconds, respect_path=False, respect_get=False):
    def wrap(f):
        def wrap_f(self, context):
            key = get_inclusion_view_function_cache_key(self, context, respect_path, respect_get, f)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(self, context)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap
