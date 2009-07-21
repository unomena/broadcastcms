from django.db import models
from broadcastcms.label.models import Label
from broadcastcms.base.models import ModelBase, ContentBase
from broadcastcms.calendar.managers import CalendarManager
from broadcastcms.richtext.fields import RichTextField
import calendar


class CastMember(ContentBase):
    content = RichTextField(help_text='Full article detailing this event.')

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
    rating = models.CharField(
        max_length=128, blank=True, default='All Ages', help_text='Age restriction rating.'
    )
    castmembers = models.ManyToManyField(CastMember, blank=True, help_text='Show cast members.')
    homepage_url = models.URLField(
        max_length=512, blank=True, verbose_name='Homepage URL',
        help_text="External URL to show's homepage."
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
            if time_dict.has_key(start_time):
                time_dict[start_time].append(start_date)
            else:
                time_dict[start_time] = [start_date,]
        time_list = []
        for time in time_dict:
            days = []
            for date in time_dict[time]:
                days.append(date.weekday())

            days = [day for day in set(days)]
            days.sort()
            item = {'time': time, 'days': days}
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
