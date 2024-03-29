import os
from PIL import Image
from django.test import TestCase
from django.conf import settings
from django.db import models
from django.core.management import call_command
from django.core.files import File
from ..fields import ScaledImageField, ScaledImageFieldFile, get_image_scales

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

        class UnspecifiedBranch(Trunk):
            pass
        models.register_models('scaledimage', UnspecifiedBranch)
        
        class UnspecifiedLeaf(Branch):
            pass
        models.register_models('scaledimage', UnspecifiedLeaf)

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
        
        obj = models.get_model('scaledimage', 'UnspecifiedBranch')()
        self.assertEquals(
            get_image_scales(obj),
            set(((50, 50), (100, 100),))
        )
        
        obj = models.get_model('scaledimage', 'UnspecifiedLeaf')()
        self.assertEquals(
            get_image_scales(obj),
            set(((50, 50), (100, 100), (200, 200), (500, 500)))
        )

    def test_scaling(self):
        image_file = open('%s/1.jpg' % SCRIPT_PATH, 'r')
        model = models.get_model('scaledimage', 'Trunk')
        obj = model()
        
        # test scaling to 50x100
        image = obj.image.scale_and_crop_image(image_file, 50, 100)
        image = Image.open(image)
        self.assertEquals(image.size, (50, 100))
        # test scaling to 100x50
        image = obj.image.scale_and_crop_image(image_file, 100, 50)
        image = Image.open(image)
        self.assertEquals(image.size, (100, 50))

    def test_storage(self):
        model = models.get_model('scaledimage', 'Trunk')
        file = File(open('%s/1.jpg' % SCRIPT_PATH, 'r'))
        obj = model()
        obj.image.save('', file, save=True)
        obj.save()
        # test the created files
        original_size = (obj.image.width, obj.image.height)
        path = obj.image.path(obj.image.name)
        path = path[:path.rindex('/')]
        self.assertImageSize('%s/original.jpeg' % path, original_size) 
        self.assertImageSize('%s/50x50.jpeg' % path, (50, 50)) 
        self.assertImageSize('%s/100x100.jpeg' % path, (100, 100)) 
        # test removal
        obj.delete()
        self.assertEquals(os.access(path, os.F_OK), False)

    def tearDown(self):
        settings.IMAGE_SCALES = self.original_scales
