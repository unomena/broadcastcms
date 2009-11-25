from haystack import indexes
from haystack import site

from broadcastcms.base.models import ContentBase
from broadcastcms.show.models import CastMember


INDEXED_MODELS = ['Competition', 'Event', 'Post', 'CastMember', 'Gallery', 'Show']

class ContentBaseIndex(indexes.SearchIndex):
    
    text = indexes.CharField(document=True, use_template=True, template_name='mobile/search/indexes/base_contentbase.txt')
    owner = indexes.CharField(model_attr='owner', default='')
    content = indexes.CharField(default='')
    
    def prepare_owner(self, obj):
        castmember_list = CastMember.permitted.filter(owner=obj.owner) if obj.owner else [] 
        if castmember_list:
            return castmember_list[0].title
    
    def prepare_content(self, obj):
        try:
            return '%s %s' % (obj.description, obj.as_leaf_class().content)
        except AttributeError:
            return '%s' % obj.description

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return ContentBase.permitted.filter(classname__in=INDEXED_MODELS)
    
site.register(ContentBase, ContentBaseIndex)
