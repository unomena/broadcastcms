from django.core.cache import cache
import md5 

def get_request_key(function, self, request, respect_path, respect_get, respect_user, respect_self_attrs=[]):
    """
    TODO: Seems a little flacky :), refactor.
    """
    key = str(hash(function))
    if respect_path:
        path_key = str(request.path)
        key += path_key
    if respect_get:
        #TODO: Generate a proper get_key instead of a simple string
        get_key = str(request.GET)
        key += get_key
    if respect_user:
        user_key = str(request.user)
        key += user_key
    for attr in respect_self_attrs:
        attr_key = str(getattr(self, attr))
        key += attr_key
    
    key = md5.new(key).hexdigest()
    return key

def cache_view_function(seconds, respect_path=False, respect_get=False, respect_user=False, respect_self_attrs=[]):
    def wrap(f):
        def wrap_f(self, context):
            key = get_request_key(f, self, context['request'], respect_path, respect_get, respect_user, respect_self_attrs)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(self, context)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap

def cache_context_processor(seconds, respect_path=False, respect_get=False, respect_user=False):
    def wrap(f):
        def wrap_f(request):
            key = get_request_key(f, None, request, respect_path, respect_get, respect_user)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(request)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap
