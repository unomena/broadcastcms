from django.db import models
from broadcastcms.base.models import ContentBase, ModelBase


class Poll(ContentBase):
    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'
    
    def vote(self, option_id):
        option = self.options.permitted().get(id=option_id)
        
        if not option:
            # TODO: raise a vote error
            return False
        else:
            option.votes += 1
            option.save()
            return True

    def set_cookie(self, request, response):
        voted_polls = request.COOKIES.get('voted_polls', None)
        if not voted_polls: 
            voted_polls = []
        else: 
            voted_polls = voted_polls.split(',')

        voted_polls.append(str(self.id))
        response.set_cookie('voted_polls', value=','.join(voted_polls))
        return response

    def voted(self, request):
        cookies = request.COOKIES
        return str(self.id) in cookies.get('voted_polls', '').split(',')


class PollOption(ModelBase):
    poll = models.ForeignKey(Poll, related_name='options')
    title = models.CharField(max_length=512)
    votes = models.PositiveIntegerField(default=0)
    percentage = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'

    def __unicode__(self):
        return '%s - %s' % (self.poll, self.title)

    def save(self, *args, **kwargs):
        super(PollOption, self).save(*args, **kwargs)
        # set the percentages for all optoins relative to this one
        options = self.poll.options.all()
        total = float(0)
        for option in options: total += option.votes
        if total != 0:
            for option in options:
                option.percentage = (option.votes / total) * 100
                super(PollOption, option).save()
