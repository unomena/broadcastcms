import threading

from django.conf import settings
from django.db.models import get_model
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist

def mail_user(subject, message, user, content_subtype=None, fail_silently=False):
    current_site = Site.objects.get_current()
    site_name = current_site.name
    domain = current_site.domain
    from_address = "%s <%s>" % (site_name, settings.EMAIL_HOST_USER)
    recipients = [user.email,]

    mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})

    if content_subtype:
        mail.content_subtype = "html"
    
    t = threading.Thread(target=mail.send, kwargs={'fail_silently': fail_silently})
    t.setDaemon(True)
    t.start()
