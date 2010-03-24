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
PODCASTS = ['%s/generate_resources/1.mp3' % SCRIPT_PATH,]
SHOW_COUNT =    10 
SHOW_CREDIT_COUNT =  20 
STATUS_UPDATE_COUNT =  20 
CASTMEMBER_COUNT =  10
LABEL_COUNT = 5
ADMIN_FRIENDS_COUNT = 25
POST_COUNT = 200
PODCAST_COUNT = 50
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
FRIENDSHIP_COUNT = 4
PROMO_WIDGET_SLOT_COUNT = 3

def clear_and_sync():
    ADMIN_USER = 'admin'
    ADMIN_PASS = 'admin'
    ADMIN_EMAIL = 'admin@admin.com'

    db_name = settings.DATABASE_NAME
    db_host = settings.DATABASE_HOST
    db_user = settings.DATABASE_USER
    db_pass = settings.DATABASE_PASSWORD
    
    flags = ['-u%s' % db_user]
    if db_host:
        flags.append('-h %s' % db_host)
    flags.append('-p')
    
    # Clear db
    child = pexpect.spawn('mysql %s' % ' '.join(flags))
    child.expect('Enter password:')
    child.sendline(db_pass)
    child.expect('mysql> ')
    child.sendline('drop schema %s;' % db_name)
    child.expect('mysql> ')
    child.sendline('create schema %s;' % db_name)
    child.expect('mysql> ')

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
    # minus 1 for the news and reviews labels
    for i in range (1, LABEL_COUNT + 1 - 2):
        labels.append({
            "model": "label.label", 
            "fields": {
                "title": "Label %s Title" % i, 
                "is_visible": True,
                "restricted_to": random.sample(restricted_to_choices, random.randint(0, len(restricted_to_choices))),
            }
        })

    # add news label
    labels += [{
        "model": "label.label", 
        "fields": {
            "title": "News", 
            "is_visible": False,
            "restricted_to": restricted_to_choices,
            }
        },
        {
        "model": "label.label", 
        "fields": {
            "title": "Reviews", 
            "is_visible": False,
            "restricted_to": restricted_to_choices,
            }
        }
    ]
    return labels

def create_posts():
    posts = []
    for i in range(1, POST_COUNT + 1):
        posts.append({
            "model": "post.post",
            "fields": {
                "title": "Post %s Title" % i,
                "description": "Post %s Description" % i,
                "content": "Post %s Content" % i,
                "is_public": True,
                "labels": [str(pk) for pk in random.sample(range(1, LABEL_COUNT + 1), random.randint(0, LABEL_COUNT))],
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

def create_podcasts():
    podcasts = []
    for i in range(1, PODCAST_COUNT + 1):
        podcasts.append({
            "model": "podcast.podcaststandalone",
            "fields": {
                "title": "Podcast %s Title" % i,
                "description": "Podcast %s Description" % i,
                "content": "Podcast %s Content" % i,
                "is_public": True,
                "image": random.sample(IMAGES, 1)[0],
                "audio": random.sample(PODCASTS, 1)[0],
                "owner": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % random.randint(1, CASTMEMBER_COUNT),
                    },
                },
            }
        })
    return podcasts

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
                "twitter_username": "gustavp",
                "image": random.sample(IMAGES, 1)[0],
                "user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % i,
                    }
                },
            }
        })
    return profiles

def create_friendships():
    friendships = []
    for i in range(1, FRIENDSHIP_COUNT+1):
        friendships.append({
            "model": "friends.friendship",
            "fields": {
                "to_user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % i,
                    }
                },
                "from_user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % (i + 2)
                    }
                }
            }
        })
    return friendships

def create_promo_widget_slots():
    slots = []
    for i in range(1, PROMO_WIDGET_SLOT_COUNT + 1):
        slots.append({
            "model": "promo.promowidgetslot",
            "fields": {
                "title": "Promo Widget Slot %s Title" % i,
                "is_public": True,
                "widget": {
                    "model": "promo.promowidget",
                    "fields": {
                        "title": "PromoWidget 1 Title",
                        "is_public": True,
                    }
                },
                "content": {
                    "model": "post.post",
                    "fields": {
                        "title": "Post %s Title" % i
                    }
                }
            }
        })
    return slots

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
                "question": "Competition %s Question" % i,
                "question_blurb": "Competition %s Question Blurb" % i,
                "correct_answer": "Competition %s Correct Answer" % i,
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

def create_provinces():
    provinces = []
    for province in ['Western Cape', 'Gauteng', 'Kwazulu Natal', 'Mpumalanga', 'Eastern Cape', 'North West', 'Free State', 'Limpopo', 'Northern Cape']:
        provinces.append({
            "model": "event.province",
            "fields": {
                "name": province,
                "is_public": True,
            },
        })
    return provinces

def create_settings():
    settings = [{
        "model": "lite.settings",
        "fields": {
            "id": "1",
            "homepage_promo_widget": { 
                "model": "promo.promowidget",
                "fields": {
                    "title": "PromoWidget 1 Title",
                }
            },
            "terms": "Terms Content",
            "privacy": "Privacy Content",
            "about": "About Content",
            "advertise": "Advertise Content", 
            "update_types": [
                {
                    "model": "contenttypes.contenttype",
                    "fields": {
                        "app_label": "post",
                        "model": "post",
                    },
                },
                {
                    "model": "contenttypes.contenttype",
                    "fields": {
                       "app_label": "event",
                        "model": "event",
                    },
                },
                {
                    "model": "contenttypes.contenttype",
                    "fields": {
                        "app_label": "gallery",
                        "model": "gallery",
                    },
                },
                {
                    "model": "contenttypes.contenttype",
                    "fields": {
                        "app_label": "competition",
                        "model": "competition",
                    },
                },
            ],
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
            "gcs_partner_id": "partner-pub-7837760522231511:xryca-9vmsb",
            "competition_general_rules": "Competition General Rules",
            "studio_cam_urls": "http://mailers.trufm.co.za/cam/studio1.jpg\nhttp://mailers.trufm.co.za/cam/studio2.jpg\nhttp://mailers.trufm.co.za/cam/studio1.jpg\nhttp://mailers.trufm.co.za/cam/studio2.jpg\nhttp://mailers.trufm.co.za/cam/studio1.jpg",
            "player_controls": "<strong>Player controls embed goes here</strong>",
            "phone": "phone",
            "fax": "fax",
            "email": "email@ddress.com",
            "sms": "sms",
            "physical_address": "physical address line 1\nphysical address line 2\nphysical address line 3",
            "postal_address": "postal address line 1\npostal address line 2\npostal address line 3",
        }
    }]
    return settings
   
def create_status_updates():
    timestamp = datetime.now()
    
    status_updates = []
    for i in range(1, STATUS_UPDATE_COUNT + 1):
        status_updates.append({
            "model": "status.statusupdate",
            "fields": {
                "text": "Status Update %s Title" % i,
                "timestamp": str(timestamp), 
                "source": random.randint(0,1),
                "user": {
                    "model": "auth.user",
                    "fields": {
                        "username": random.sample(["friend%s" % random.randint(1, ADMIN_FRIENDS_COUNT), "castmember%s" % random.randint(1, CASTMEMBER_COUNT)], 1)[0],
                    },
                },
            }
        })
        timestamp = timestamp - timedelta(minutes = 1)
    return status_updates

def create_admin_friends():
    friends = []
    profiles = []
    for i in range(1, ADMIN_FRIENDS_COUNT + 1):
        friends.append({
            "model": "friends.friendship",
            "fields": {
                "to_user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "friend%s" % i,
                    },
                },
                "from_user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "admin",
                    },
                },
            }
        })
        profiles.append({
            "model": "lite.userprofile", 
            "fields": {
                "image": random.sample(IMAGES, 1)[0],
                "user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "friend%s" % i,
                    }
                },
            }
        })

    return friends + profiles
   
def create_views_and_widgets():
    objects = []
    objects.append({
        "model": "widgets.LayoutTopLeftRightTopLeftSlot",
        "fields": {
            "layout": {
                "model": "widgets.LayoutTopLeftRight",
                "fields": {
                    "view_name": "home",
                    "is_public": True,
                },
            },
            "widget": {
                "model": "widgets.SlidingPromoWidget",
                "fields" : {
                    "title": "Sliding Promo Widget",
                    "is_public": True,
                },
            },
            "position": "1",
        },
    })
    objects.append({
        "model": "widgets.LayoutTopLeftRightTopLeftSlot",
        "fields": {
            "layout": {
                "model": "widgets.LayoutTopLeftRight",
                "fields": {
                    "view_name": "facebook_setup",
                    "is_public": True,
                    "background": True,
                },
            },
            "widget": {
                "model": "widgets.FacebookSetupWidget",
                "fields" : {
                    "title": "Facebook Setup Widget",
                    "is_public": True,
                },
            },
            "position": "1",
        },
    })
    return objects

def generate():
    choice = raw_input('Do you want to clear and sync the db? Warning: All data will be lost! y/n: ').lower()
    if choice == 'y':
        clear_and_sync()

    objects = []
    objects += create_labels()
    objects += create_banners()
    objects += create_castmembers()
    objects += create_profiles()
    objects += create_friendships()
    objects += create_posts()
    objects += create_podcasts()
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
    objects += create_provinces()
    objects += create_promo_widget_slots()
    objects += create_settings()
    objects += create_admin_friends()
    objects += create_status_updates()
    objects += create_views_and_widgets()
    
    load_json(objects)
