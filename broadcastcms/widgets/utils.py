from django.conf import settings

class SSIContentResolver(object):
    """
    Renders either an SSI tag or normal content based on SSI mode and user uniqueness.
    """
    user_unique = False

    def get_leaf(self):
        try:
            return self.as_leaf_class()
        except AttributeError:
            return self
        
    def render(self, context):
        """
        Returns either self.render_ssi or self.render_content based on self.user_unique 
        and settings.SSI_ENABLED.  self.render_content to be implimented by subclasses.
        """
        if self.user_unique and settings.SSI_ENABLED:
            return self.render_ssi(context)
        else:
            return self.get_leaf().render_content(context)
                
        
    def render_ssi(self, context):
        """
        Renders SSI tag. URL is reversed ssi view and added get params determined
        through nginx passed key.
        """
        leaf = self.get_leaf()
        request = context['request']
       
        cache_key = request.META.get('MEMCACHED_KEY', request.get_full_path())
        url = self.get_ssi_url()
        try:
            url += '?%s' % cache_key.split('?')[1]
        except IndexError:
            pass

        # XXX: investigate why wait has to be set to true in order
        # for nginx to correctly fetch includes from cache.
        return '<!--# include virtual="%s" wait="yes" -->' % url

    def render_content(self, context):
        raise NotImplementedError("Should have implemented this")
    
    def get_ssi_url(self):
        raise NotImplementedError("Should have implemented this")
