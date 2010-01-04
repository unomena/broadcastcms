import os
import sys
import simplejson as json
import urllib
import hashlib
import cStringIO 
import unicodedata
#from BeautifulSoup import BeautifulSoup

from django.db.models import get_model
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
from django.core.files.uploadedfile import InMemoryUploadedFile

from broadcastcms.richtext.fields import RichTextField
from broadcastcms.scaledimage.fields import ScaledImageField

SCRIPT_PATH = os.path.dirname( os.path.realpath( __file__ ) )
USE_CACHE = True

def load_image(instance, source):
    source = fetch_from_cache(source)
    size = os.path.getsize(source)
    image_file = cStringIO.StringIO()
    image_file.write(open(source, 'r').read())
    field_name = u'image'
    name = source.split('/')[-1]
    content_type = 'image/jpeg'
    return InMemoryUploadedFile(image_file, 'image', name, 'image/jpeg', size, None)

def format_rich_text(rich_text):
    #rich_text = unicodedata.normalize('NFKD', rich_text).encode('ascii','ignore')
    rich_text = rich_text.encode("utf-8")
    return rich_text
    #soup = BeautifulSoup(rich_text)
    #for img in soup.findAll('img'):
    #    img.extract()

    #return str(soup)

def fetch_from_cache(source):
    destination = source
    if source.startswith('http'):
        destination = '%s/json_loader_cache/%s' % (SCRIPT_PATH, hashlib.md5(source).hexdigest())
        if not USE_CACHE or not os.path.exists(destination):
            #print "Fetching %s..." % source
            f = open(destination, 'w')
            f.write(urllib.urlopen(source).read())
            f.close()
    return destination

def generate_item(item):
    app, model = item['model'].split('.')
    model = get_model(app, model)
    model_instance = model(pk='dummy_pk')
    fields = {}
    many_to_many_fields = {}
    scaled_image_fields = {}
    password_field = ''

    for field, value in item['fields'].items():
        
        if value.__class__ == list:
            value_items = []
            for item in value:
                if item.__class__ == dict:
                    value_items.append(generate_item(item))
                else:
                    value_items.append(item)
            value = value_items
        elif value.__class__ == dict:
            value = generate_item(value)

        model_field = model_instance._meta.get_field(field)
        if isinstance(model_field, ManyToManyField):
            many_to_many_fields[str(field)] = value
        elif isinstance(model_field, ScaledImageField):
            if value:
                scaled_image_fields[str(field)] = value
        elif isinstance(model_field, RichTextField):
            value = format_rich_text(value)
            fields[str(field)] = value
        elif field == 'password':
            password_field = value
        else:
            fields[str(field)] = value

    obj, created = model.objects.get_or_create(**fields)

    if created:
        #print "Created %s" % obj

        for field, value in many_to_many_fields.items():
            obj_field = getattr(obj, field)
            if value.__class__ == list:
                for val in value:
                    obj_field.add(val)
            else:
                obj_field.add(value)
    
        for field, value in scaled_image_fields.items():
            field = getattr(obj, field)
            image = load_image(model_instance, value)
            field.save(image.name, image)

        if password_field:
            obj.set_password(password_field)

        obj.save()    

    return obj

def load_json(source, data_formatter=None):
    if source.__class__ == str:
        source = fetch_from_cache(source)
        source = open(source, 'r')
        data = source.read()
        json_data = json.loads(data)
        source.close()
    elif source.__class__ == list:
        source = [str(item).replace("False", "false").replace("True", "true").replace("'", '"') for item in source]
        json_data = json.loads("[%s]" % ','.join(source))
   
    if data_formatter:
        json_data = data_formatter(json_data)

    i = 1
    previous_status = ""
    for item in json_data:
        generate_item(item)
        status = "Generating items, please wait... %s%%" % (100 * i / len(json_data))
        if status != previous_status:
            sys.stdout.write("\b" * len(status))
            sys.stdout.write(status)
            sys.stdout.flush()
        i += 1
    print ""
