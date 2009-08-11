from django.db import models

from broadcastcms.base.models import ContentBase, ModelBase
from broadcastcms.richtext.fields import RichTextField


class Artist(ContentBase):
    content = RichTextField()
    songs = models.ManyToManyField('Song', through='Credit')


class Song(ContentBase):
    album = models.CharField(max_length=255, blank=True, null=True)
    artists = models.ManyToManyField('Artist', through='Credit')
    video_url = models.CharField('Video URL', max_length=255, blank=True, null=True)

class Credit(models.Model):
    artist = models.ForeignKey(Artist, related_name='credits')
    song = models.ForeignKey(Song, related_name='credits')
    role = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return "%s credit for %s" % (self.artist.title, self.song.title)
