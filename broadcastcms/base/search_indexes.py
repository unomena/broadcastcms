import datetime

from haystack import indexes
from haystack import site

from broadcastcms.base.models import ContentBase
from broadcastcms.lite.models import Settings


class ContentBaseIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True, template_name='mobile/search/indexes/base_contentbase.txt')
    description = indexes.CharField(model_attr='description')
    owner = indexes.CharField(model_attr='owner', default='')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        settings = Settings.objects.get_or_create(pk='1')[0]
        update_types = [update_type.model_class().__name__ for update_type in settings.update_types.all()]
        return ContentBase.permitted.filter(classname__in=update_types)

site.register(ContentBase, ContentBaseIndex)
