from django.test import TestCase
from django.conf import settings
from django.db.models import register_models, get_model
from broadcastcms.base.models import ContentBase
from models import get_image_scales


class ImageScalesTest(TestCase):
    def setUp(self):
        class Branch(ContentBase):
            pass
        register_models('scaledimage', Branch)

        class Leaf(Branch):
            pass
        register_models('scaledimage', Leaf)

        settings.IMAGE_SCALES = {
            'base': {'ContentBase': {'image': ((50, 50), (100, 100))}},
            'scaledimage': {
                'Branch': {'image': ((200, 200), (500, 500))},
                'Leaf': {'image': ((150, 150), (300, 300))},
            },
        }
        
    def test_image_scales(self):
        instance = get_model('base', 'ContentBase')()
        self.assertEquals(
            get_image_scales(instance),
            set(((50, 50), (100, 100)))
        )

        instance = get_model('scaledimage', 'Branch')()
        self.assertEquals(
            get_image_scales(instance),
            set(((50, 50), (100, 100), (200, 200), (500, 500)))
        )

        instance = get_model('scaledimage', 'Leaf')
        self.assertEquals(
            get_image_scales(instance),
            set(((50, 50), (100, 100), (200, 200), (500, 500), (150, 150), (300, 300)))
        )
