from django.core.cache import cache
import md5 

def get_request_key(node, request, respect_path, respect_get, f):
    """
    TODO: Refactor to generate proper keys.
    """
    key = str(node.__class__) + str(f.__name__)
    if respect_path:
        path_key = str(request.path)
        key += path_key
    if respect_get:
        #TODO: Generate a proper get_key instead of a simple string
        get_key = str(request.GET)
        key += get_key
    
    key = md5.new(key).hexdigest()
    return key

def cache_view_function(seconds, respect_path=False, respect_get=False):
    def wrap(f):
        def wrap_f(self, context):
            key = get_request_key(self, context['request'], respect_path, respect_get, f)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(self, context)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap

def cache_context_processor(seconds, respect_path=False, respect_get=False):
    def wrap(f):
        def wrap_f(request):
            key = get_request_key(f, request, respect_path, respect_get, f)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(request)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap
