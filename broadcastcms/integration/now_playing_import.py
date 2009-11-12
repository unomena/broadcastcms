import urllib
import xml.dom.minidom
from random import randint

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

def create_song(artist_title, song_title, role):
    song = None
    created = False
    
    artist, created = Artist.objects.get_or_create(title=artist_title)
    if not artist.is_public:
        artist.is_public = True
        artist.save()
    
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
