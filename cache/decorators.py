from django.core.cache import cache
    

def get_inclusion_tag_function_cache_key(node, f):
    return (str(node.__class__) + str(f.__name__)).replace(' ','')

def cache_inclusion_tag_function(seconds):
    def wrap(f):
        def wrap_f(*args):
            key = get_inclusion_tag_function_cache_key(args[0], f)
            cached_result = cache.get(key)
            if cached_result:
                return cached_result
            else:
                result = f(*args)
                cache.set(key, result, seconds)
                return result
        return wrap_f
    return wrap
