from django.db import models

from broadcastcms.base.models import ContentBase, ModelBase
from ckeditor.fields import RichTextField


class Artist(ContentBase):
    content = RichTextField()
    songs = models.ManyToManyField('Song', through='Credit')


class Song(ContentBase):
    album = models.CharField(max_length=255, blank=True, null=True)
    artists = models.ManyToManyField('Artist', through='Credit')
    video_embed = models.TextField('Video Embed Tag', blank=True, null=True)

    def get_primary_artist(self):
        """
        Returns the primary artist for a song.
        Primary artist is determined by credit roles.
        """
        credits = self.credits.all().filter(artist__is_public=True).order_by('role')
        return credits[0].artist if credits else None
        

CREDIT_CHOICES = [('1', 'Performer'), ('2', 'Contributor'), ('3', 'Writer'), ('4', 'Producer')]
class Credit(models.Model):
    artist = models.ForeignKey(
        Artist, 
        related_name='credits'
    )
    song = models.ForeignKey(
        Song, 
        related_name='credits'
    )
    role = models.CharField(
        max_length=255, 
        choices = CREDIT_CHOICES,
        blank=True, 
        null=True,
    )

    def __unicode__(self):
        return "%s credit for %s" % (self.artist.title, self.song.title)
