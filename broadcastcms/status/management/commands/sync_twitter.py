import collections
import logging

from dateutil.parser import parse as parse_date

from django.core.management.base import NoArgsCommand, CommandError
from django.db.models import Q
from django.utils.hashcompat import sha_constructor

import twitter

from broadcastcms.lite.models import UserProfile
from broadcastcms.status.models import StatusUpdate


class Command(NoArgsCommand):
    def handle(self, **options):
        verbosity = int(options["verbosity"])
        api = twitter.Api()
        
        profiles = UserProfile.objects.exclude(
            Q(twitter_url=None) | Q(twitter_url="")
        ).select_related("user")
        
        usernames = collections.defaultdict(list)
        
        # group twitter usernames with profiles (in any case they overlap)
        for profile in profiles:
            # @@@ how does twitter_url get set?
            username = profile.twitter_url.split("/")[-1]
            usernames[username].append(profile)
        
        for username, profiles in usernames.iteritems():
            if verbosity > 1:
                print "[%s] fetching timeline" % username
            tweets = api.GetUserTimeline(username)
            
            for tweet in tweets:
                # mysql does not support timezone-aware datetime objects
                created_at = parse_date(tweet.created_at).replace(tzinfo=None)
                
                for profile in profiles:
                    # look for existing status update
                    key = sha_constructor(str(tweet.id)).hexdigest()
                    try:
                        status = StatusUpdate.objects.get(key=key, user=profile.user)
                    except StatusUpdate.DoesNotExist:
                        if verbosity > 1:
                            print "[%s] adding %s to %s" % (username, tweet.id, profile.user)
                        status = StatusUpdate()
                        status.key = key
                        status.user = profile.user
                        status.timestamp = created_at
                        status.text = tweet.text
                        status.source = StatusUpdate.TWITTER_SOURCE
                        status.raw_extra_data = str(tweet)
                        #status.save()
                    else:
                        if verbosity > 1:
                            print "[%s] kipping %s for %s" % (username, tweet.id, profile.user)