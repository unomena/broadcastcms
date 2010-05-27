#
# Management command to automatically fetch videos from GHFM channel on Zoopy.
#
# Thane
# 

try:
    import json
except:
    import simplejson as json
    
import urllib
import datetime
import traceback

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from broadcastcms.video.models import Video
from broadcastcms.video.thumbnails import get_zoopy_thumbnail
from broadcastcms.video.constants import *
from broadcastcms.video.utils import calculate_height
from broadcastcms.lite.forms import SubmitVideoForm
from broadcastcms.lite.utils import non_threaded_mail


#------------------------------------------------------------------------------
def zoopy_fetch_media(page=1, exclude=None):
    """
    Submits the given parameters as a Zoopy request, returning a decoded JSON
    object (the response from Zoopy).
    """
    
    exclude_str = '&%s' % ('&'.join([('exclude[]=%s' % id) for id in exclude]) if exclude else '')
    # just to be safe
    if len(exclude_str) > 1024:
        exclude_str = ''
        
    response = urllib.urlopen('http://api.zoopy.com/zoopy/0.1/rest/media/search.json?channel=37&perPage=99&page=%d%s' % (page, exclude_str)).read()
    # decode the response as a JSON object
    obj = json.loads(response)
    
    return obj


#------------------------------------------------------------------------------
def zoopy_process_videos(media, owner):
    """
    Runs through the given "media" array and creates the videos in the database if necessary.
    
    "owner" is the user to be assigned as the owner of the video.
    """
    
    video_count = 0
    
    # run through all of the returned videos
    for cur_video in media:
        if cur_video['typeNoun'] == 'video':
            # check that the video with the given ID doesn't exist yet
            if Video.objects.filter(video_type='z', video_id=cur_video['id']).count() == 0:
                print "Creating video (and fetching thumbnail for) \"%s\"..." % cur_video['title']
                
                video_width = DEFAULT_VIDEO_WIDTH
                video_height = calculate_height(int(cur_video['width']), int(cur_video['height']), video_width)
                
                # work out an embed code for this video
                embed_code = ZOOPY_DEFAULT_EMBED_CODE % {
                    'width': video_width, 'height': video_height, 'zoopyid': cur_video['id'],
                }
                
                print "Video date: %s" % cur_video['created']
                
                # create the video in the database
                video = Video(title=cur_video['title'], description=cur_video['description'], video_id=cur_video['id'], code=embed_code,
                    video_type='z', image=get_zoopy_thumbnail(cur_video['id']), owner=owner, is_public=True, created=datetime.datetime.strptime(cur_video['created'], VIDEO_TIMESTAMP_FORMAT))
                video.save()
                video_count += 1
            else:
                print "Video with ID %s already exists in database, skipping" % cur_video['id']
    
    return video_count


#------------------------------------------------------------------------------
class Command(BaseCommand):
    """
    The class that handles the "zoopyfetch" management command.
    """
    
    help = """Automatically fetches the latest GHFM channel videos from Zoopy"""
    
    
    #------------------------------------------------------------------------------
    def handle(self, *args, **options):
        """
        Command handler function.
        """
        
        error_str = ''
        
        # first check if the Zoopy admin user has been created
        try:
            zoopyuser = User.objects.get(username='zoopyadmin')
        except:
            print "Zoopy admin user does not exist. Attempting to create 'zoopyadmin'..."
            zoopyuser = User.objects.create_user('zoopyadmin', 'thane@praekelt.com', 'kaNFpqh8cYWV')
            zoopyuser.is_staff = True
            zoopyuser.is_superuser = True
            zoopyuser.save()
            # if we get this far without exceptions...
            print "Success."
            
        if not zoopyuser:
            error_str += "Could not create or access Zoopy admin user\n"
        
        print "Retrieving existing Zoopy videos from database..."
        zoopy_videos = Video.objects.filter(video_type='z')
        # build an exclude string
        exclude_videos = [video.video_id for video in zoopy_videos]
        print "Found %d existing Zoopy videos." % zoopy_videos.count()
        
        print "Fetching Zoopy channel contents..."
        contents = None
        try:
            contents = zoopy_fetch_media(1, exclude_videos)
        except:
            error_str += traceback.format_exc()+'\n\n'
        
        if contents:
            print "Zoopy status: %s" % contents['status']
            if contents['status'] != 'ok':
                print "Unacceptable status returned"
            else:
                results = contents['result']
                print "Pagination: %s" % results['pagination']
                print "Total videos: %s" % results['total']
                
                media = results['media']
                videos_created = 0
                
                for cur_page in results['pagination']:
                    try:
                        videos_created += zoopy_process_videos(media, zoopyuser)
                        print "%d videos created so far" % videos_created
                        # if we're to fetch the next page of media
                        if len(results['pagination']) > 1:
                            contents = zoopy_fetch_media(cur_page+1, exclude_videos)
                            media = contents['result']['media']
                            if not contents:
                                error_str += 'Unable to fetch media from page %d\n' % (cur_page+1)
                    except:
                        error_str += traceback.format_exc()+'\n\n'
        else:
            error_str += "Could not fetch any JSON object from Zoopy\n"
            print "Error while fetching Zoopy channel contents"
        
        if error_str:
            non_threaded_mail('Error(s) in GoodHopeFM automatic Zoopy fetch', error_str, 'GoodHopeFM <goodhopefmmailbox@gmail.com>', ['thane@praekelt.com'])
