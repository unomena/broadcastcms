import calendar

from django.db import models

from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.label.models import Label
from broadcastcms.richtext.fields import RichTextField


class CastMember(ContentBase):
    content = RichTextField(help_text='Full article detailing this castmember.')
    shows = models.ManyToManyField(
        'Show', 
        through='Credit'
    )

    class Meta:
        verbose_name = 'Cast Member'
        verbose_name_plural = 'Cast Members'


class Show(ContentBase):
    objects = CalendarManager()

    extended_description = RichTextField(
        verbose_name='Extended Description', help_text='Full article detailing this show.'
    )
    genres = models.ManyToManyField(
        Label, related_name='shows', blank=True,
        limit_choices_to={'restricted_to__contains': 'show-genres'}
    )
    classification = models.CharField(
        max_length=128, blank=True, default='All Ages', help_text='Classification of the show.'
    )
    homepage_url = models.URLField(
        max_length=512, blank=True, verbose_name='Homepage URL',
        help_text="External URL to show's homepage."
    )
    castmembers = models.ManyToManyField(
        'CastMember', 
        through='Credit'
    )

    def show_times(self):
        cats = {
            'every day': [0,1,2,3,4,5,6],
            'weekdays': [0,1,2,3,4],
            'weekends': [5,6],
        }
        entries = self.entries.all()
        time_dict = {}
        for entry in entries:
            start_date = entry.start.date()
            start_time = entry.start.time()
            end_time = entry.end.time()
            time = (start_time, end_time)
            if time_dict.has_key(time):
                time_dict[time].append(start_date)
            else:
                time_dict[time] = [start_date,]
        time_list = []
        for time in time_dict:
            days = []
            for date in time_dict[time]:
                days.append(date.weekday())

            days = [day for day in set(days)]
            days.sort()
            item = {'start_time': time[0], 'end_time': time[1], 'days': days}
            for cat in cats:
                if days == cats[cat]:
                    item['days'] = cat
            if item['days'] == days:
                item['days'] = [calendar.day_name[day] for day in days]
            if item['days'].__class__ == str:
                item['days'] = [item['days'],]
            time_list.append(item)
        return time_list

    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'


CREDIT_CHOICES = [('1', 'DJ'), ('2', 'Contributor'), ('3', 'News Reader')]
class Credit(models.Model):
    castmember = models.ForeignKey(CastMember, related_name='credits')
    show = models.ForeignKey(Show, related_name='credits')
    role = models.CharField(
        max_length=255, 
        choices = CREDIT_CHOICES,
        blank=True, 
        null=True)

    def __unicode__(self):
        return "%s credit for %s" % (self.castmember.title, self.show.title)
