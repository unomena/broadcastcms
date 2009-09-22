from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from broadcastcms.banner.models import Banner
from broadcastcms.base.models import ContentBase
from broadcastcms.label.models import Label
from broadcastcms.post.models import Post
from broadcastcms.richtext.fields import RichTextField
from broadcastcms.scaledimage import ScaledImageField

def get_update_choices():
    choices = []
    apps = models.get_apps()
    for app in apps:
            for model in models.get_models(app):
                if issubclass(model, ContentBase) and not model == ContentBase:
                    choices.append(model._meta.object_name)
    return choices

class Settings(models.Model):
    homepage_featured_labels = models.ManyToManyField(
        Label, 
        null=True, 
        blank=True, 
        limit_choices_to={'is_visible': False},
        verbose_name='Homepage Featured Labels',
        help_text='Content labeled with these labels will be featured on the homepage.',
    )
    terms_post = models.ForeignKey(
        Post, 
        null=True, 
        blank=True, 
        limit_choices_to={'is_public': True},
        verbose_name='Terms and Conditions Post',
        help_text='A post to be used for the Terms and Conditions page.',
    )
    update_types = models.ManyToManyField(
        ContentType, 
        null=True, 
        blank=True, 
        limit_choices_to={'model__in': get_update_choices},
        help_text="Content type(s) to be displayed in update sections."
    )
    competition_general_rules = RichTextField(
        help_text='General competition rules page.',
        blank=True, 
        null=True,
    )
    studio_cam_urls = models.TextField(
        help_text='URLs to studio cam images (full URL, one per line).',
        blank=True, 
        null=True,
    )
    gcs_partner_id = models.CharField(
        max_length=128,
        verbose_name='Search Partner ID',
        help_text='Google Custom Search Partner ID (cx form field value).',
        blank=True, 
        null=True,
    )
   
    # Adds
    banner_section_home = models.ManyToManyField(Banner, 
                                            related_name='banner_section_home', 
                                            null=True, 
                                            blank=True, 
                                            limit_choices_to={'is_public': True},
                                            verbose_name='Home')
    banner_section_shows = models.ManyToManyField(Banner, 
                                                    related_name='banner_section_shows', 
                                                    null=True, 
                                                    blank=True, 
                                                    limit_choices_to={'is_public': True},
                                                    verbose_name='Shows')
    banner_section_chart = models.ManyToManyField(Banner, 
                                                  related_name='banner_section_chart', 
                                                  null=True, 
                                                  blank=True, 
                                                  limit_choices_to={'is_public': True},
                                                  verbose_name='Chart')
    banner_section_competitions = models.ManyToManyField(Banner, 
                                                         related_name='banner_section_competitions', 
                                                         null=True, 
                                                         blank=True, 
                                                         limit_choices_to={'is_public': True},
                                                         verbose_name='Competitions')
    banner_section_news = models.ManyToManyField(Banner, 
                                                  related_name='banner_section_news', 
                                                  null=True, 
                                                  blank=True, 
                                                  limit_choices_to={'is_public': True},
                                                  verbose_name='News')
    banner_section_events = models.ManyToManyField(Banner, 
                                                   related_name='banner_section_events', 
                                                   null=True, 
                                                   blank=True, 
                                                   limit_choices_to={'is_public': True},
                                                   verbose_name='Events')
    banner_section_galleries = models.ManyToManyField(Banner, 
                                                 related_name='banner_section_galleries', 
                                                 null=True, 
                                                 blank=True, 
                                                 limit_choices_to={'is_public': True},
                                                 verbose_name='Galleries')
    
    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'

    def get_section_banners(self, section, permitted=True):
        banners = getattr(self, "banner_section_%s" % section, None)
        if banners:
            banners = banners.permitted() if permitted else banners.all()
            banners = [banner.as_leaf_class() for banner in banners]
        return banners

class UserProfile(models.Model):
    user = models.ForeignKey(
        User, 
        unique=True
    )
    email_subscribe = models.BooleanField(default=False)
    sms_subscribe = models.BooleanField(default=False)
    facebook_url = models.URLField(
        blank=True,
        null=True,
    )
    twitter_url = models.URLField(
        blank=True,
        null=True,
    )
    image = ScaledImageField()

    def __unicode__(self):
        return self.user.username
   
    
    #def save(self, *args, **kwargs):
    #    settings = Settings.objects.all()
    #    if settings:
    #        settings = settings[0]
    #        list_id = settings.pmailer_list_id
    #        form_id = settings.pmailer_form_id
    #        email = self.user.email
    #        if email and list_id and form_id:
    #            pmailer = PMailer(list_id=list_id, form_id=form_id, email=email)
    #            if self.newsletter_subscribe:
    #                pmailer.subscribe()
    #            else:
    #                pmailer.unsubscribe()

    #    super(UserProfile, self).save(*args, **kwargs)
