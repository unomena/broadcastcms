from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from user_messages.signals import message_sent


def email_user_on_message(sender, message, thread, **kwargs):
    ctx = {
        "message": message,
        "thread": thread,
        "site": Site.objects.get_current(),
    }
    for userthread in thread.userthread_set.exclude(user=message.sender):
        ctx["user"] = userthread.user
        subject = render_to_string("desktop/mailers/account/new_message_subject.txt", ctx).strip()
        body = render_to_string("desktop/mailers/account/new_message_body.html", ctx)
        userthread.user.email_user(subject, body)

message_sent.connect(email_user_on_message)
