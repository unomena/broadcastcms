from datetime import date, datetime, timedelta
import random

from broadcastcms.lite.json_loader import load_json
from broadcastcms.show.models import CREDIT_CHOICES as SHOW_CREDIT_CHOICES

ADMIN_FRIENDS_COUNT = 25
CASTMEMBER_COUNT = 10
COMPETITION_COUNT =  20
CONTENTBASE_COUNT = 20
CASTMEMBER_COUNT =  10
EVENT_ENTRY_COUNT = 20
EVENT_COUNT = 10
LABEL_COUNT = 5
POST_COUNT = 100
SHOW_CREDIT_COUNT =  20 
SHOW_COUNT =    10 
STATUS_UPDATE_COUNT =  20 

def competitions():
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
            }
        })
    load_json(competitions)

def contentbase():
    contentbase = []
    for i in range(1, CONTENTBASE_COUNT + 1):
        contentbase.append({
            "model": "base.contentbase",
            "fields": {
                "title": "ContentBase %s Title" % i,
                "description": "ContentBase %s Description" % i,
                "is_public": True,
            }
        })
    load_json(contentbase)

def labels():
    restricted_to_choices = ["post-labels", "event-labels", "competition-labels", "show-labels", "gallery-labels", "chart-labels", "imagebanner-labels"]

    labels = []
    # minus 2 for the news and reviews labels
    for i in range (1, LABEL_COUNT + 1 - 2):
        labels.append({
            "model": "label.label", 
            "fields": {
                "title": "Label %s Title" % i, 
                "is_visible": True,
                "restricted_to": random.sample(restricted_to_choices, random.randint(0, len(restricted_to_choices))),
            }
        })

    # add news and reviews label
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
    load_json(labels)
    
    
def posts():
    # create labels for the posts first
    labels()

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
                "owner": {
                    "model": "auth.user",
                    "fields": {
                        "username": "castmember%s" % random.randint(1, CASTMEMBER_COUNT),
                    },
                },
            }
        })
    load_json(posts)

def upcomming_events():
    entries=[]
    now = datetime.now()
    abs_start = now - timedelta(days = 7)
    abs_start = datetime(abs_start.year, abs_start.month, abs_start.day)
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
    load_json(entries)

def status_updates():
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
    load_json(status_updates)

def show_credits():
    credits = []
    for i in range(1, SHOW_CREDIT_COUNT + 1):
        credits.append({
            "model": "show.credit",
            "fields": {
                "castmember": {
                    "model": "show.castmember",
                    "fields": {
                        "title": "Castmember %s Title" % random.randint(1, CASTMEMBER_COUNT),
                        "owner": {
                            "model": "auth.user",
                            "fields": {
                                "username": "castmember%s" % i,
                            }
                        },
                    },
                },
                "show": {
                    "model": "show.show",
                    "fields": {
                        "title": "Show %s Title" % random.randint(1, SHOW_COUNT),
                        "is_public": True,
                    },
                },
                "role": random.sample(SHOW_CREDIT_CHOICES, 1)[0][0],
            },
        })
    load_json(credits)

def admin_friends():
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
                "user": {
                    "model": "auth.user",
                    "fields": {
                        "username": "friend%s" % i,
                    }
                },
            }
        })

    load_json(friends + profiles)
