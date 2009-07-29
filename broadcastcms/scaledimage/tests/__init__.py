import os
from PIL import Image
from django.test import TestCase
from django.conf import settings
from django.db import models
from django.core.management import call_command
from django.core.files import File
from ..fields import ScaledImageField, get_image_scales
from ..storage import ScaledImageStorage


SCRIPT_PATH = os.path.dirname( os.path.realpath( __file__ ) )


class ScalesImageTest(TestCase):
    def setUp(self):
        class Trunk(models.Model):
            image = ScaledImageField(max_length=512)
        models.register_models('scaledimage', Trunk)

        class Branch(Trunk):
            pass
        models.register_models('scaledimage', Branch)

        class Leaf(Branch):
            pass
        models.register_models('scaledimage', Leaf)

        call_command('syncdb', verbosity=0, interactive=False)

        self.original_scales = settings.IMAGE_SCALES
        settings.IMAGE_SCALES = {
            'scaledimage': {
                'Trunk': {'image': ((50, 50), (100, 100))},
                'Branch': {'image': ((200, 200), (500, 500))},
                'Leaf': {'image': ((150, 150), (300, 300))},
            },
        }

    def assertImageSize(self, filename, size):
        self.assertEquals(os.access(filename, os.F_OK), True)
        image = Image.open(filename)
        self.assertEquals(image.size, size)

    def test_image_scales(self):
        obj = models.get_model('scaledimage', 'Trunk')()
        self.assertEquals(
            get_image_scales(obj),
            set(((50, 50), (100, 100)))
        )

        obj = models.get_model('scaledimage', 'Branch')()
        self.assertEquals(
            get_image_scales(obj),
            set(((50, 50), (100, 100), (200, 200), (500, 500)))
        )

        obj = models.get_model('scaledimage', 'Leaf')()
        self.assertEquals(
            get_image_scales(obj),
            set(((50, 50), (100, 100), (200, 200), (500, 500), (150, 150), (300, 300)))
        )

    def test_scaling(self):
        file = File(open('%s/1.jpg' % SCRIPT_PATH, 'r'))
        orig_image = Image.open(file)
        storage = ScaledImageStorage()
        # test scaling to 50x100
        image = storage.scale_and_crop_image(file, 50, 100)
        self.assertEquals(image.size, (50, 100))
        # test scaling to 100x50
        image = storage.scale_and_crop_image(file, 100, 50)
        self.assertEquals(image.size, (100, 50))

    def test_storage(self):
        model = models.get_model('scaledimage', 'Trunk')
        file = File(open('%s/1.jpg' % SCRIPT_PATH, 'r'))
        obj = model()
        obj.image.save('', file, save=True)
        # test the created files
        original_size = (obj.image.width, obj.image.height)
        path = obj.image.path
        path = path[:path.rindex('/')]
        self.assertImageSize('%s/original.jpeg' % path, original_size) 
        self.assertImageSize('%s/50x50.jpeg' % path, (50, 50)) 
        self.assertImageSize('%s/100x100.jpeg' % path, (100, 100)) 
        # test removal
        obj.delete()
        self.assertEquals(os.access(path, os.F_OK), False)

    def tearDown(self):
        settings.IMAGE_SCALES = self.original_scales
