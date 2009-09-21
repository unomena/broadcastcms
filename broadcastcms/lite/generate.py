import os
import sys
import random
import pexpect
from datetime import date, datetime, timedelta

from django.conf import settings

from broadcastcms.label.models import Label
from broadcastcms.post.models import Post
from broadcastcms.show.models import CREDIT_CHOICES as SHOW_CREDIT_CHOICES
from broadcastcms.radio.models import CREDIT_CHOICES as RADIO_CREDIT_CHOICES

from json_loader import load_json

SCRIPT_PATH = os.path.dirname( os.path.realpath( __file__ ) )
IMAGES = ['%s/generate_resources/0.jpg' % SCRIPT_PATH,
          '%s/generate_resources/1.jpg' % SCRIPT_PATH,
          '%s/generate_resources/2.jpg' % SCRIPT_PATH,
          '%s/generate_resources/3.jpg' % SCRIPT_PATH,
          '%s/generate_resources/4.jpg' % SCRIPT_PATH,
          '%s/generate_resources/5.jpg' % SCRIPT_PATH,
          '%s/generate_resources/6.jpg' % SCRIPT_PATH,
          '%s/generate_resources/7.jpg' % SCRIPT_PATH,
          '%s/generate_resources/8.jpg' % SCRIPT_PATH,
          '%s/generate_resources/9.jpg' % SCRIPT_PATH]
SHOW_COUNT =    10 
SHOW_CREDIT_COUNT =  20 
CASTMEMBER_COUNT =  10
LABEL_COUNT = 5
POST_COUNT = 200
BANNER_COUNT = 5
SONG_COUNT = 10
ARTIST_COUNT = 10
RADIO_CREDIT_COUNT =  20 
CHART_ENTRY_COUNT =  40
COMPETITION_COUNT =  20
GALLERY_COUNT =  40
GALLERY_IMAGE_COUNT = 200
EVENT_COUNT = 10
EVENT_ENTRY_COUNT = 20
LOCATION_COUNT = 5

def clear_and_sync():
    ADMIN_USER = 'admin'
    ADMIN_PASS = 'admin'
    ADMIN_EMAIL = 'admin@admin.com'

    db_name = settings.DATABASE_NAME
    db_user = settings.DATABASE_USER
    db_pass = settings.DATABASE_PASSWORD
    
    # Clear db
    child = pexpect.spawn('mysql -u%s -p' % db_user)
    child.expect('Enter password:')
    child.sendline(db_pass)
    child.expect('mysql> ')
    child.sendline('drop schema %s;' % db_name)
    child.expect('mysql> ')
    child.sendline('create schema %s;' % db_name)

    # Sync db
    child = pexpect.spawn('%s syncdb' % sys.argv[0])
    child.expect('Would you like to create one now.*')
    child.sendline('yes')
    child.expect('Username.*')
    child.sendline(ADMIN_USER)
    child.expect('E-mail.*')
    child.sendline(ADMIN_EMAIL)
    child.expect('Password.*')
    child.sendline(ADMIN_PASS)
    child.expect('Password.*')
    child.sendline(ADMIN_PASS)

    child.expect(pexpect.EOF, timeout=None)

def create_labels():
    restricted_to_choices = ["post-labels", "event-labels", "competition-labels", "show-labels", "gallery-labels", "chart-labels", "imagebanner-labels"]

    labels = []
    for i in range (1, LABEL_COUNT + 1):
        labels.append({
            "model": "label.label", 
            "fields": {
                "title": "Label %s Title" % i, 
                "is_visible": random.randint(0, 1) == 1,
                "restricted_to": random.sample(restricted_to_choices, random.randint(0, len(restricted_to_choices))),
            }
        })
    return labels

def create_posts():
    labels = Label.objects.filter(restricted_to__contains='post-labels')

    posts = []
    for i in range(1, POST_COUNT + 1):
        posts.append({
            "model": "post.post",
            "fields": {
                "title": "Post %s Title" % i,
                "description": "Post %s Description" % i,
                "content": "Post %s Content" % i,
                "is_public": True,
                "labels": [str(label.pk) for label in random.sample(labels, random.randint(0, len(labels)))],
                "image": random.sample(IMAGES, 1)[0],
                "owner": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % random.randint(1, CASTMEMBER_COUNT),
                    },
                },
            }
        })
    return posts

def create_banners():
    banners = []
    for i in range(1, BANNER_COUNT + 1):
        banners.append({
            "model": "banner.imagebanner",
            "fields": {
                "title": "Banner %s Title" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0],
                "url": "/",
            }
        })
    return banners

def create_entries():
    now = datetime.now()
    abs_start = now - timedelta(days = 7)
    abs_start = datetime(abs_start.year, abs_start.month, abs_start.day)
    start = abs_start
    end = start + timedelta(days = 18)
    
    entries = []

    # show entries
    lengths = [60, 120, 180, 240]
    while start < end:
        length = random.sample(lengths, 1)[0]
        entries.append({
            "model": "calendar.entry", 
            "fields": {
                "is_public": True,
                "start": str(start),
                "end": str(start + timedelta(minutes=length)),
                "content": {
                    "model": "show.show",
                    "fields": {
                        "title": "Show %s Title" % random.randint(1,SHOW_COUNT),
                    }
                },
            }
        })
        start += timedelta(minutes=length)
    
    # song entries
    start = abs_start
    lengths = [30, 60]
    while start < end:
        length = random.sample(lengths, 1)[0]
        entries.append({
            "model": "calendar.entry", 
            "fields": {
                "is_public": True,
                "start": str(start),
                "end": str(start + timedelta(minutes=length)),
                "content": {
                    "model": "radio.song",
                    "fields": {
                        "title": "Song %s Title" % random.randint(1,SONG_COUNT),
                    }
                },
            }
        })
        start += timedelta(minutes=length)
    
    # event entries
    day_span = 14
    start = abs_start
    end = start + timedelta(day_span)
    for i in range(1, EVENT_ENTRY_COUNT + 1):
        entry_start = start + timedelta(days=random.randint(1,day_span))
        entry_end = entry_start + timedelta(days=random.randint(1,3))
        entries.append({
            "model": "calendar.entry", 
            "fields": {
                "is_public": True,
                "start": str(entry_start),
                "end": str(entry_end),
                "content": {
                    "model": "event.event",
                    "fields": {
                        "title": "Event %s Title" % random.randint(1,EVENT_COUNT),
                    }
                },
            }
        })

    return entries

def create_castmembers():
    castmembers = []
    for i in range(1, CASTMEMBER_COUNT + 1):
        castmembers.append({
            "model": "show.castmember", 
            "fields": {
                "title": "Castmember %s Title" % i,
                "description": "Castmember %s Description" % i,
                "content": "Castmember %s Content" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0],
                "owner": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % i,
                    }
                },
            }
        })
    return castmembers

def create_profiles():
    profiles = []
    for i in range(1, CASTMEMBER_COUNT + 1):
        profiles.append({
            "model": "lite.userprofile", 
            "fields": {
                "facebook_url": "http://www.facebook.com/kabelom?_fb_noscript=1",
                "twitter_url": "http://twitter.com/gustavp",
                "user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % i,
                    }
                },
            }
        })
    return profiles
    
def create_shows():
    shows = []
    for i in range(1, SHOW_COUNT + 1):
        shows.append({
            "model": "show.show", 
            "fields": {
                "title": "Show %s Title" % i,
                "description": "Show %s Description" % i,
                "extended_description": "Show %s Extended Description" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0],
            }
        })
    return shows

def create_show_credits():
    credits = []
    for i in range(1, SHOW_CREDIT_COUNT + 1):
        credits.append({
            "model": "show.credit",
            "fields": {
                "castmember": {
                    "model": "show.castmember",
                    "fields": {
                        "title": "Castmember %s Title" % random.randint(1, CASTMEMBER_COUNT),
                    },
                },
                "show": {
                    "model": "show.show",
                    "fields": {
                        "title": "Show %s Title" % random.randint(1, SHOW_COUNT),
                    },
                },
                "role": random.sample(SHOW_CREDIT_CHOICES, 1)[0][0],
            },
        })
    return credits

def create_artists():
    artists = []
    for i in range(1, ARTIST_COUNT + 1):
        artists.append({
            "model": "radio.artist", 
            "fields": {
                "title": "Artist %s Title" % i,
                "description": "Artist %s Description" % i,
                "content": "Artist %s Content" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
            }
        })
    return artists

def create_songs():
    songs = []
    for i in range(1, SONG_COUNT + 1):
        songs.append({
            "model": "radio.song",
            "fields": {
                "title": "Song %s Title" % i,
                "description": "Song %s Description" % i,
                "album": "Album %s Title" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0],
            }
        })
    return songs

def create_radio_credits():
    credits = []
    for i in range(1, RADIO_CREDIT_COUNT + 1):
        credits.append({
            "model": "radio.credit",
            "fields": {
                "artist": {
                    "model": "radio.artist",
                    "fields": {
                        "title": "Artist %s Title" % random.randint(1, ARTIST_COUNT),
                    },
                },
                "song": {
                    "model": "radio.song",
                    "fields": {
                        "title": "Song %s Title" % random.randint(1, SONG_COUNT),
                    },
                },
                "role": random.sample(RADIO_CREDIT_CHOICES, 1)[0][0],
            },
        })
    return credits

def create_chart():
    charts = [{
            "model": "chart.chart",
            "fields": {
                "title": "Chart 1 Title",
                "description": "Chart 1 Description",
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
            }
        }]
    return charts
    
def create_chart_entries():
    entries = []
    for i in range(1, CHART_ENTRY_COUNT + 1):
        entries.append({
            "model": "chart.chartentry",
            "fields": {
                "chart": {
                    "model": "chart.chart",
                    "fields": {
                        "title": "Chart 1 Title",
                    },
                },
                "song": {
                    "model": "radio.song",
                    "fields": {
                        "title": "Song %s Title" % random.randint(1, SONG_COUNT),
                    },
                },
                "is_public": True,
                "current_position": i,
                "previous_position": CHART_ENTRY_COUNT + 1 - i,
            }
        })
    return entries

def create_competitions():
    competitions = []
    for i in range(1, COMPETITION_COUNT + 1):
        competitions.append({
            "model": "competition.competition",
            "fields": {
                "title": "Competition %s Title" % i,
                "description": "Competition %s Description" % i,
                "content": "Competition %s Content" % i,
                "rules": "Competition %s Rules" % i,
                "end": str(date.today() + timedelta(days=i)),
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
            }
        })
    return competitions

def create_galleries():
    galleries = []
    for i in range(1, GALLERY_COUNT + 1):
        galleries.append({
            "model": "gallery.gallery",
            "fields": {
                "title": "Gallery %s Title" % i,
                "description": "Gallery %s Description" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
                "owner": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % random.randint(1, CASTMEMBER_COUNT),
                    },
                },
            }
        })
    return galleries

def create_gallery_images():
    images = []
    for i in range(1, GALLERY_IMAGE_COUNT + 1):
        images.append({
            "model": "gallery.galleryimage",
            "fields": {
                "title": "Image %s Title" % i,
                "description": "Image %s Description" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
                "gallery": {
                    "model": "gallery.gallery",
                    "fields": {
                        "title": "Gallery %s Title" % random.randint(1, GALLERY_COUNT),
                    },
                },
            }
        })
    return images

def create_events():
    events = []
    for i in range(1, EVENT_COUNT + 1):
        events.append({
            "model": "event.event",
            "fields": {
                "title": "Event %s Title" % i,
                "description": "Event %s Description" % i,
                "content": "Event %s Content" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0], 
            }
        })
    return events

def create_locations():
    locations = []
    for i in range(1, LOCATION_COUNT + 1):
        locations.append({
            "model": "event.location",
            "fields": {
                "venue": "Location %s Venue" % i,
                "is_public": True,
                "event": {
                    "model": "event.event",
                    "fields": {
                        "title": "Event %s Title" % random.randint(1,EVENT_COUNT),
                    }
                },
                "city": {
                    "model": "event.city",
                    "fields": {
                        "name": "City %s Name" % i,
                        "is_public": True,
                    }
                },
            }
        })
    return locations

def create_settings():
    labels = Label.objects.filter(is_visible=False)
    settings = [{
        "model": "lite.settings",
        "fields": {
            "id": "1",
            "homepage_featured_labels": [str(label.pk) for label in labels[:3]],
            "terms_post": {
                "model": "post.post",
                "fields": {
                    "title": "Post 1 Title",
                }
            },
            "update_types": {
                "model": "contenttypes.contenttype",
                "fields": {
                    "app_label": "post",
                    "model": "post",
                }
            },
            "banner_section_home": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_shows": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_chart": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_competitions": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_news": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_events": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "banner_section_galleries": {
                "model": "banner.banner",
                "fields": {
                    "title": "Banner %s Title" % random.randint(1, BANNER_COUNT),
                }
            },
            "competition_general_rules": "Competition General Rules",
            "studio_cam_urls": "http://mailers.trufm.co.za/cam/studio1.jpg\nhttp://mailers.trufm.co.za/cam/studio2.jpg\nhttp://mailers.trufm.co.za/cam/studio1.jpg\nhttp://mailers.trufm.co.za/cam/studio2.jpg\nhttp://mailers.trufm.co.za/cam/studio1.jpg",
        }
    }]
    return settings
    
def generate():
    choice = raw_input('Do you want to clear and sync the db? Warning: All data will be lost! y/n: ').lower()
    if choice == 'y':
        clear_and_sync()

    objects = []
    objects += create_labels()
    objects += create_banners()
    objects += create_castmembers()
    objects += create_profiles()
    objects += create_posts()
    objects += create_shows()
    objects += create_show_credits()
    objects += create_songs()
    objects += create_artists()
    objects += create_radio_credits()
    objects += create_chart()
    objects += create_chart_entries()
    objects += create_competitions()
    objects += create_galleries()
    objects += create_gallery_images()
    objects += create_events()
    objects += create_locations()
    objects += create_entries()
    
    load_json(objects)
   
    # Create post labels
    labels = Label.objects.filter(restricted_to__contains='post-labels')
    for i in range(1, POST_COUNT + 1):
        post = Post.objects.get(title__exact="Post %s Title" % i)
        post.labels = [str(label.pk) for label in random.sample(labels, random.randint(0, len(labels)))]
        post.save()
    
    load_json(create_settings())
