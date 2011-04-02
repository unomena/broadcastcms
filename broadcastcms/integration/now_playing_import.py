import cStringIO
import md5
import mimetypes
import pylast
import random
import urllib
import xml.dom.minidom
from random import randint
from datetime import datetime, timedelta

from django.core.files.uploadedfile import InMemoryUploadedFile

from broadcastcms.radio.models import Artist, Song, Credit
from broadcastcms.calendar.models import Entry

def fetch_dom():
    data = urllib.urlopen("http://mailers.trufm.co.za/nowplaying/onair.xml?%s" % randint(1,9999999)).read()
    try:
        dom = xml.dom.minidom.parseString(data)
    except:
        return None
    return dom
    
def get_text_by_tag_name(parent, name):
    elements = parent.getElementsByTagName(name)
    if elements:
        text_nodes = elements[0].childNodes
        if text_nodes:
            return text_nodes[0].data
    return None

def get_cover_image(url):
    invalid_md5s = ['833dccc04633e5616e9f34ae5d5ba057', 'fe252bebef963b73ff557a537c853104',]

    data = urllib.urlopen(url).read()
    if md5.new(data).hexdigest() in invalid_md5s:
        return None

    return data
    
def load_file(field, data, file_name):
    f = cStringIO.StringIO()
    f.write(data)
    field_name = str(field)
    content_type=mimetypes.guess_type(file_name)[0]
    elements = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456890'
    file_name = '%s.%s' % (''.join([random.choice(elements) for n in range(8)]), file_name.split('.')[-1])
    return InMemoryUploadedFile(f, field_name, file_name, content_type, len(data), None)

def load_artist_image(artist): 
    API_KEY = "f6b4b668e2c5e8db7350ea539c87f76a"
    API_SECRET = "5654158e5b5eccc51e9f37d36f589298"
    lastfm_network = pylast.get_lastfm_network(api_key = API_KEY, api_secret = API_SECRET)
    lastfm_artist = lastfm_network.get_artist(artist.title)
    try:
        cover_image_url = lastfm_artist.get_cover_image()
    except pylast.WSError:
        cover_image_url = None
        
    if cover_image_url:
        cover_image = get_cover_image(cover_image_url)
        if cover_image:
            f = load_file(artist.image, cover_image, cover_image_url.split('/')[-1])
            artist.image.save(f.name, f)

def create_song(artist_title, song_title, role):
    song = None
    created = False
   
    artist, artist_created = Artist.objects.get_or_create(title=artist_title)
    if not artist.is_public:
        artist.is_public = True
        artist.save()

    if not artist.image:
        load_artist_image(artist)
    
    songs = Song.objects.filter(title__iexact=song_title)
    if songs:
        for match in songs:
            if list(match.artists.all()) == [artist]:
                song = match
                
    if not song:
        song = Song.objects.create(title=song_title)
        credit = Credit.objects.get_or_create(artist=artist, song=song, role=role)
        created = True

    if not song.is_public:
        song.is_public = True
        song.save()

    return song

def import_now_playing():
    entry_created = False

    dom = fetch_dom()
    if not dom:
        print "Error fetching xml, no import made"
        return

        
    current_nodes = dom.getElementsByTagName("Current")
    next_nodes = dom.getElementsByTagName("Next")
    
    if current_nodes and next_nodes:
        current = current_nodes[0]
        next = next_nodes[0]

        item_code = get_text_by_tag_name(current, "itemCode")
        if item_code:
            try:
                int(item_code)
                valid_song = True
            except:
                valid_song = False

            if valid_song:
                song_title = get_text_by_tag_name(current, "titleName")
                artist_title = get_text_by_tag_name(current, "artistName")
                start = get_text_by_tag_name(current, "startTime")
                end = get_text_by_tag_name(next, "startTime")

                if artist_title and song_title and start and end:
                    artist_title = artist_title.title()
                    song_title = song_title.title()
                    start = start.replace('T', ' ')
                    end = end.replace('T', ' ')

                    song = create_song(artist_title, song_title, "Performer")
                    entry, entry_created = Entry.objects.get_or_create(start=start, end=end, content=song, is_public=True)

    if entry_created:
        print "Created entry %s for song %s" % (entry, song)
    else:
        print "No import made"

def import_now_playing_rcs(feed_url):
    """
    Create now playing instances from a badly-delimited now playing list on
    sabc.
    """
    data = urllib.urlopen('%s?%s' % (feed_url, randint(0, 99999))).read()

    # Parse as accurately as we can.
    parts_per_line = 6
    lines = data.split('\r\n')
    feed_items = []
    for line in lines:
        elements = [el.strip() for el in line.split('  ') if el]
        if len(elements) == parts_per_line:
            feed_items.append(elements)

    valid_song = False
    for feed_item in feed_items:
        try:
            if feed_item[2].lower() == 'song':
                artist_title = feed_item[3]
                song_title = feed_item[4]
                length = feed_item[5]
                valid_song = True
                break
        except IndexError:
            pass

    entry_created = False
    if valid_song:
        # calculate start and end times. since the feed doesn't include exact play times,
        # we let the imported song's start time be import time (now)
        now = datetime.now()
        start = now
        minutes = int(length.split(':')[0])
        seconds = int(length.split(':')[1].split('.')[0])
        length = timedelta(minutes=minutes, seconds=seconds)
        end = start + length
       
        # create song if it's not still playing
        song = create_song(artist_title, song_title, "Performer")
        existing_entries = Entry.objects.permitted().by_content_type(Song).now().filter(content=song.contentbase)

        # In case the feed gets stuck, do not duplicate the last song:
        last_song = None
        if not existing_entries:
            all_song_entries = Entry.objects.permitted()\
                                    .by_content_type(Song)\
                                    .filter(content=song.contentbase)\
                                    .order_by('-start')
            if all_song_entries.count():
                last_song = all_song_entries[0].content.as_leaf_class()

        if not existing_entries and not last_song == song :
            entry, entry_created = Entry.objects.get_or_create(start=start, end=end, content=song, is_public=True)
       
    if entry_created:
        print "Created entry %s for song %s" % (entry, song)
    else:
        print "No import made"
