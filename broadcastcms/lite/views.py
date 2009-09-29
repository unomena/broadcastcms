from datetime import date, datetime, timedelta
import calendar

from django.contrib import auth
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.comments import signals
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.util import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from broadcastcms import public
from broadcastcms.banner.models import CodeBanner, ImageBanner
from broadcastcms.base.models import ContentBase
from broadcastcms.calendar.models import Entry
from broadcastcms.chart.models import Chart, ChartEntry
from broadcastcms.competition.models import Competition
from broadcastcms.event.models import Event
from broadcastcms.gallery.models import Gallery
from broadcastcms.integration.captchas import ReCaptcha
from broadcastcms.post.models import Post
from broadcastcms.richtext.fields import RichTextField
from broadcastcms.scaledimage.fields import get_image_scales
from broadcastcms.scaledimage.storage import ScaledImageStorage
from broadcastcms.show.models import Show, CastMember
from broadcastcms.utils import mail_user

from forms import LoginForm, ProfileForm, ProfilePictureForm, RegistrationForm
from templatetags.inclusion_tags import AccountLinksNode
import utils

# Account

def account_picture(request):
    if not request.user.is_authenticated():
       raise Http404
        
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            if image:
                saver = ScaledImageStorage(scales=get_image_scales(profile))
                image = saver.save(profile.image.field.upload_to(profile, image.name), image)
                profile.image = image
                profile.save()
    else:
        form = ProfilePictureForm()

    context.update({
        'profile': profile,
        'form': form,
    })
    return render_to_response('content/account/picture.html', context)

def account_profile(request):
    """
    TODO: This view seems very flimsy, refactor.
    """
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    user = request.user
    profile = request.user.profile
        
    if request.method == "POST":
        form = ProfileForm(request.POST)

        # If no password supplied remove the password fields thereby ignoring them and not changing the password
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))
        password_confirm = form.fields['password_confirm'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password_confirm'))
        if not password:
            password_field = form.fields['password']
            del form.fields['password']
            password_confirm_field = form.fields['password_confirm']
            del form.fields['password_confirm']
        
        # Prevent user's own username triggering an error
        username = form.fields['username'].widget.value_from_datadict(form.data, form.files, form.add_prefix('username'))
        if user.username == username:
            username_field = form.fields['username']
            del form.fields['username']

        if form.is_valid():
            # Readd fields removed for validation
            if user.username == username:
                form.fields['username'] = username_field
                form.cleaned_data['username'] = username
            
            if not password:
                form.fields['password'] = password_field
                form.cleaned_data['password'] = password
                form.fields['password_confirm'] = password_confirm_field
                form.cleaned_data['password_confirm'] = password_confirm
            
            # Get cleaned form values
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_address = form.cleaned_data['email_address']
            mobile_number = form.cleaned_data['mobile_number']
            city = form.cleaned_data['city']
            province = form.cleaned_data['province']
            birth_date_day = form.cleaned_data['birth_date_day']
            birth_date_month = form.cleaned_data['birth_date_month']
            birth_date_year = form.cleaned_data['birth_date_year']
                
            # Create birth_date
            try:
                birth_date = datetime(
                    year=int(birth_date_year),
                    month=int(birth_date_month),
                    day=int(birth_date_day),
                    hour=0,
                    minute=0
                )
            except ValueError:
                birth_date = None

            # Update user
            user.username = username
            user.email = email_address
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.set_password(password)
            user.save()

            # Update profile
            profile.mobile_number = mobile_number
            profile.city = city
            profile.province = province
            profile.birth_date = birth_date
   
            profile.save()
        else:
            # Readd fields removed for validation
            if user.username == username:
                form.fields['username'] = username_field
            
            if not password:
                form.fields['password'] = password_field
                form.fields['password_confirm'] = password_confirm_field
    else:
        province = profile.province
        if province: province = province.id
            
        data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email_address': user.email,
            'mobile_number': profile.mobile_number,
            'city': profile.city,
            'province': province,
        }
        birth_date = profile.birth_date
        if birth_date:
            data.update({
                'birth_date_day': birth_date.day,
                'birth_date_month': birth_date.month,
                'birth_date_year': birth_date.year,
            })
            
        form = ProfileForm(initial=data)

    context.update({
        'form': form,
    })
    return render_to_response('content/account/profile.html', context)

def account_subscriptions(request):
    if not request.user.is_authenticated():
       raise Http404
    
    context = RequestContext(request, {})
    return render_to_response('content/account/subscriptions.html', context)

# Chart

def chart(request, slug):
    if slug:
        chart = get_object_or_404(Chart, slug=slug, is_public=True)
    else:
        charts = Chart.permitted.order_by('-modified')
        if not charts:
            raise Http404
        else:
            chart = charts[0]

    context = RequestContext(request, {})
    entries = chart.chartentries.permitted().order_by('current_position')
    pager = utils.paging(entries, 'page', request, 10)
    paginator = pager.paginator
    per_page = paginator.per_page
    
    pages = []
    for page in paginator.page_range:
        page_dict = {'number': page, 'start': per_page * page - 9, 'end': per_page * page}
        if page == pager.number:
            page_dict.update({'current': True})
        pages.append(page_dict)
        
    context.update({
        'chart': chart,
        'pager': pager,
        'pages': pages,
    })
    return render_to_response('content/charts/chart.html', context)

# Competitions

def competitions(request):
    context = RequestContext(request, {})
    competitions = Competition.permitted.order_by('-created')
    pager = utils.paging(competitions, 'page', request, 10)
    
    context.update({
        'pager': pager,
    })
    return render_to_response('content/competitions/competitions.html', context)

def competitions_rules(request):
    context = RequestContext(request, {})
    if not context['settings'].competition_general_rules:
        raise Http404
    return render_to_response('content/competitions/rules.html', context)

def competitions_content(request, slug):
    content = get_object_or_404(Competition, slug=slug, is_public=True)
    context = RequestContext(request, {})
    
    context.update({
        'content': content,
    })
    return render_to_response('content/competitions/content.html', context)


# Events
def events(request):
    context = RequestContext(request, {})
    
    entries = Entry.objects.permitted().by_content_type(Event).order_by('start')
    sorter = utils.EventSorter(entries, 'events', 'by', request)

    entry_dict = {}
    for entry in sorter.object_list:
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start = entry.start.replace(hour=0, minute=0, second=0, microsecond=0)
        if start < now:
            start = now
        end = entry.end
        content = entry.content
        if content:
            content = content.as_leaf_class()
            while start < end:
                if entry_dict.has_key(start):
                    entry_dict[start].append(content)
                else:
                    entry_dict[start] = [content]
                start += timedelta(days=1)
    

    days = entry_dict.keys()
    days.sort()
    entries = []
    for day in days:
        entries.append({'day': day, 'events': entry_dict[day]})
    
    pager = utils.paging(entries, 'page', request, 4)

    context.update({
        'today': date.today(),
        'pager': pager,
        'sorter': sorter,
    })
        
    return render_to_response('content/events/events.html', context)

def events_content(request, slug):
    content = get_object_or_404(Event, slug=slug, is_public=True)
    context = RequestContext(request, {})
    
    sorter = utils.EventSorter([], 'events', 'by', request)
    
    context.update({
        'content': content,
        'sorter': sorter,
    })
    return render_to_response('content/events/content.html', context)

# Validate
def validate_username(request):
    if not request.is_ajax():
        raise Http404
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        value = form.fields['username'].widget.value_from_datadict(form.data, form.files, form.add_prefix('username'))
        try:
            form['username'].field.clean(value)
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again'"

            # don't fail if the user already has the username 
            if request.user.is_authenticated():
                user = request.user
                if value == user.username:
                    response = "true" 

            return HttpResponse(response)

        return HttpResponse("true")
    raise Http404

def validate_password(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))

        response = "true"
        try:
            form['password'].field.clean(password)
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again'"

        return HttpResponse(response)
    
    raise Http404

def validate_password_confirm(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        password_confirm = form.fields['password_confirm'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password_confirm'))
        password = form.fields['password'].widget.value_from_datadict(form.data, form.files, form.add_prefix('password'))

        response = "true"
        try:
            form['password_confirm'].field.clean(password_confirm)
            if password != password_confirm:
                response = "'Passwords do not match.'"
                
        except ValidationError, e:
            if e.messages:
                response = "'%s'" % str(e.messages[0])
            elif e.message:
                response = ("'%s'" % str(e.message))
            else:
                response = "'Error, please try again.'"

        return HttpResponse(response)
    
    raise Http404


def validate_captcha(request):
    if not request.is_ajax():
        raise Http404

    if request.method == 'POST':
        if ReCaptcha().verify(request):
            return HttpResponse("true")
        else:
            return HttpResponse("'Incorrect, please try again.'")

    raise Http404

# Galleries
def galleries(request):
    context = RequestContext(request, {})
    sorter = utils.Sorter(Gallery.permitted, 'galleries', 'by', request)
    pager = utils.paging(sorter.object_list, 'page', request, 18)

    context.update({
        'pager': pager,
        'sorter': sorter,
    })
    return render_to_response('content/galleries/galleries.html', context)

def galleries_content(request, slug):
    content = get_object_or_404(Gallery, slug=slug, is_public=True)
    context = RequestContext(request, {})
    
    sorter = utils.Sorter([], 'galleries', 'by', request)
    context.update({
        'content': content,
        'sorter': sorter,
    })
    return render_to_response('content/galleries/content.html', context)


# Misc
def account_links(request):
    """
    Wrapper exposing the account_links inclusion tag as a view.
    """
    context = RequestContext(request, {})
    return HttpResponse(AccountLinksNode().render(context))

def contact(request):
    context = RequestContext(request, {})
    return render_to_response('content/search_results.html', context)

def comment_add(request):
    """
    Post a comment. Taken from django.contrib.comments.views.comments and adjusted for ajax submition and anonymous users
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email
    
    if not request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = 'Anonymous'
        if not data.get('email', ''):
            data["email"] = 'anonymous@anonymous.com'

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        form.fields['comment'].error_messages['required'] = 'Please enter your comment'
        template_list = [
            "comments/%s_%s_preview.html" % tuple(str(model._meta).split(".")),
            "comments/%s_preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "instance": target,
                "errors": form.errors
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    # Ajx additions
    context = RequestContext(request, {})
    context.update({
        'instance': target
    })
    from templatetags.inclusion_tags import CommentsNode
    return HttpResponse(CommentsNode('instance').render(context))

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return account_links(request)
    
def home(request):
    context = RequestContext(request, {})
    return render_to_response('content/home.html', context)

def search_results(request):
    context = RequestContext(request, {})
    return render_to_response('content/search_results.html', context)

def info_content(request, section):
    context = RequestContext(request, {})
    settings = context['settings']

    # Check is section is valid and has content
    try:
        field = settings._meta.get_field_by_name(section)
    except models.FieldDoesNotExist:
        raise Http404
    
    if not isinstance(field[0], RichTextField):
        raise Http404

    section_verbose_name = field[0].verbose_name
    content = getattr(settings, section)
    if not content:
        raise Http404
        
    menu_items = []
    if settings.about: menu_items.append({'title': 'About Us', 'current': (section == 'about'), 'url': reverse('info_content', kwargs={'section': 'about'})})
    if settings.advertise: menu_items.append({'title': 'Advertise', 'current': (section == 'advertise'), 'url': reverse('info_content', kwargs={'section': 'advertise'})})
    if settings.terms: menu_items.append({'title': 'Terms &amp; Conditions', 'current': (section == 'terms'), 'url': reverse('info_content', kwargs={'section': 'terms'})})
    if settings.privacy: menu_items.append({'title': 'Privacy Policy', 'current': (section == 'privacy'), 'url': reverse('info_content', kwargs={'section': 'privacy'})})
    context.update({
        'content': content,
        'section_verbose_name': section_verbose_name,
        'menu_items': menu_items,
    })
    return render_to_response('content/info/content.html', context)
    

# Mailers
def mailer_new_user(request, username, password):
    current_site = Site.objects.get_current()
    site_name = current_site.name
    host = "http://%s" % request.META['HTTP_HOST']
    subject = "Welcome to %s" % site_name
    
    return (render_to_string('mailers/new_user.html', {
        'username': username, 
        'password': password,
        'host': host,
        'site_name': site_name,
    }), subject)


# Modals
def modals_login(request):
    if not request.is_ajax():
        raise Http404
    
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
                return HttpResponse("true")
            else:
                return HttpResponse("'Incorrect username or password.'")
    else:
        form = LoginForm()

    return render_to_response('modals/login.html', {'form': form})

def modals_content(request, slug):
    if not request.is_ajax():
        raise Http404
    
    return render_to_response('modals/login.html', {'form': form})

def modals_register(request):
    if not request.is_ajax():
        raise Http404
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # Get cleaned form values
            username = form.cleaned_data['username']
            email_address = form.cleaned_data['email_address']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_subscribe = form.cleaned_data['email_subscribe']
            sms_subscribe = form.cleaned_data['sms_subscribe']

            # Generate Random Password
            password = auth.models.UserManager().make_random_password(length=8)

            # Create user
            user = User.objects.create_user(
                username = username,
                password = password,
                email = email_address
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Create profile
            profile = user.profile
            profile.email_subscribe = email_subscribe
            profile.sms_subscribe = sms_subscribe
            profile.save()
        
            # Send confirmation mail
            message, subject = mailer_new_user(request, username, password)
            mail_user(subject, message, user, content_subtype="html", fail_silently=False)
            
            # Authenticate and login user
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
            
            return HttpResponse("true")
        else:
            return HttpResponse("false")
    else:
        form = RegistrationForm()
    
    context = RequestContext(request, {})
    context.update({
        'form': form,
    })
    return render_to_response('modals/register.html', context)

def modals_password_reset(request):
    if not request.is_ajax():
        raise Http404

    context = {}
    return render_to_response('modals/password_reset.html', context)

# News
def news(request, sorter='most-recent'):
    context = RequestContext(request, {})
    sorter = utils.Sorter(Post.permitted, 'news', 'by', request)
    pager = utils.paging(sorter.object_list, 'page', request, 10)

    context.update({
        'pager': pager,
        'sorter': sorter,
    })
    return render_to_response('content/news/news.html', context)

def news_content(request, slug):
    content = get_object_or_404(ContentBase, slug=slug, is_public=True)
    content = content.as_leaf_class()
    context = RequestContext(request, {})
    
    sorter = utils.Sorter([], 'news', 'by', request)
    context.update({
        'content': content,
        'sorter': sorter,
    })
    return render_to_response('content/news/content.html', context)

# Popups     
def listen_live(request):
    context = RequestContext(request, {})
    return render_to_response('popups/listen_live.html', context)

def studio_cam(request):
    context = RequestContext(request, {})
    settings = context['settings']
    urls = settings.studio_cam_urls
    if urls:
        urls = urls.replace('\r', '').split('\n')
    else:
        urls = []

    context.update({
        'urls': urls,
    })

    return render_to_response('popups/studio_cam.html', context)

# Shows
def shows_line_up(request, day='monday'):
    context = RequestContext(request, {})
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if day in days:
        offset = days.index(day)
    else:
        offset = 0
        day = 'monday'

    entries = Entry.objects.permitted().by_content_type(Show).day(offset).order_by('start')
    valid_entries = []
    for entry in entries:
        if entry.content.is_public:
            valid_entries.append(entry)
    
    today = str(calendar.day_name[datetime.now().weekday()]).lower()
  
    pager = utils.paging(valid_entries, 'page', request, 18)
    
    context.update({
        'pager': pager,
        'today': today,
        'day': day,
        'days': days,
    })

    return render_to_response('content/shows/line_up.html', context)

def shows_dj_blog(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    context = RequestContext(request, {})

    owner = castmember.owner
    instances = ContentBase.permitted.filter(owner=owner).exclude(classname__exact="castmember").order_by("-created") if owner else []
    pager = utils.paging(instances, 'page', request, 10)

    context.update({
        'castmember': castmember,
        'pager': pager,
    })
    return render_to_response('content/shows/dj_blog.html', context)

def shows_dj_profile(request, slug):
    castmember = get_object_or_404(CastMember, slug=slug, is_public=True)
    context = RequestContext(request, {})

    context.update({
        'castmember': castmember,
    })
    return render_to_response('content/shows/dj_profile.html', context)

def shows_dj_content(request, castmember_slug, content_slug):
    castmember = get_object_or_404(CastMember, slug=castmember_slug, is_public=True)
    content = get_object_or_404(ContentBase, slug=content_slug, is_public=True)
    content = content.as_leaf_class()
    context = RequestContext(request, {})

    context.update({
        'castmember': castmember,
        'content': content,
    })
    return render_to_response('content/shows/dj_content.html', context)

# Model Views
class CodeBannerViews(object):
    def render(self):
        return render_to_string('content/banners/code_banner.html', {"self": self})

class ImageBannerViews(object):
    def render(self):
        return render_to_string('content/banners/image_banner.html', {"self": self})

class ContentBaseViews(object):
    def render_home_updates(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('content/contentbase/home_updates.html', context)
    
    def render_updates_widget(self, context):
        labels = self.labels.visible()
        label = labels[0] if labels else None
        context = {
            'self': self,
            'label': label,
            'url': self.url(context),
        }
        return render_to_string('content/contentbase/updates_widget.html', context)
    
    def render_listing(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('content/contentbase/listing.html', context)

    def render_article(self, context):
        context = RequestContext(context['request'], {})
        context.update({
            'self': self,
        })
        return render_to_string('content/article.html', context)
        
    def url(self, context):
        def handle_home(self):
            return None

        def handle_shows(self):
            owner = self.owner
            if owner:
                castmembers = CastMember.permitted.filter(owner=owner)
                if castmembers:
                    return reverse('shows_dj_content', kwargs={'castmember_slug': castmembers[0].slug, 'content_slug': self.slug})
        
        def handle_galleries(self):
            if self.classname in ['Gallery',]:
                return reverse('galleries_content', kwargs={'slug': self.slug})
        
        def handle_competitions(self):
            if self.classname in ['Competition',]:
                return reverse('competitions_content', kwargs={'slug': self.slug})
        
        def handle_chart(self):
            if self.classname in ['Chart',]:
                return reverse('chart', kwargs={'slug': self.slug})
        
        def handle_events(self):
            if self.classname in ['Event',]:
                return reverse('events_content', kwargs={'slug': self.slug})
        
        def handle_news(self):
            return reverse('news_content', kwargs={'slug': self.slug})

        section_handlers = [
            ('home', handle_home),
            ('shows', handle_shows),
            ('galleries', handle_galleries),
            ('competitions', handle_competitions),
            ('events', handle_events),
            ('chart', handle_chart),
            ('news', handle_news),
        ]

        section = context['section']
        for section_handler in section_handlers:
            if section == section_handler[0]:
                url = section_handler[1](self)
        if url:
            return url
        else:
            for section_handler in section_handlers:
                url = section_handler[1](self)
                if url:
                    return url
            
        return '/404'

class ChartEntryViews(object):
    def render_chart(self):
        song = self.song
        now = datetime.now()
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        
        days_on = (week_start - self.created).days
        if days_on > 0:
            weeks_on = days_on / 7
        else:
            weeks_on = 0

        context = {
            'self': self, 
            'song': self.song,
            'artist': self.get_primary_artist(),
            'weeks_on': weeks_on,
        }
        return render_to_string('content/charts/entry.html', context)
    
    def get_primary_artist(self):
        artist = None
        credits = self.song.credits.all().order_by('role')
        for credit in credits:
            artist = credit.artist
            if artist.is_public:
                break

        return artist
        
class CompetitionViews(object):
    def render_listing(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('content/competitions/listing.html', context)
    
    def render_article_body(self):
        context = {
            'self': self,
        }
        return render_to_string('content/competitions/article_body.html', context)

class EntryViews(object):
    def render_block(self, context):
        content = self.content.as_leaf_class()
        credits = content.credits.order_by('role')
        castmember_url = credits[0].castmember.url() if credits else ''

        context = {
            'self': self,
            'content': content,
            'castmember_url': castmember_url,
        }
        return render_to_string('content/entry/block.html', context)
    
class EventViews(object):
    def render_article_body(self):
        context = {
            'self': self,
        }
        return render_to_string('content/events/article_body.html', context)
    
    def render_listing(self, context):
        locations = self.locations.permitted()
        location = locations[0] if locations else None
        
        context = {
            'self': self,
            'url': self.url(context),
            'location': location,
        }
        return render_to_string('content/events/listing.html', context)

class GalleryViews(object):
    def render_block(self, context):
        context = {
            'self': self,
            'url': self.url(context),
        }
        return render_to_string('content/galleries/block.html', context)
    
    def render_article_body(self):
        context = {
            'self': self,
        }
        return render_to_string('content/galleries/article_body.html', context)

class CastMemberViews(object):
    def url(self):
        return reverse('shows_dj_blog', kwargs={'slug': self.slug})

class PostViews(object):
    def render_article_body(self):
        context = {
            'self': self,
        }
        return render_to_string('content/posts/article_body.html', context)
       
class UserViews(object):
    def url(self):
        castmembers = self.contentbase_set.permitted().filter(classname__exact="castmember")
        return castmembers[0].as_leaf_class().url() if castmembers else ''
 
public.site.register(CastMember, CastMemberViews)
public.site.register(ChartEntry, ChartEntryViews)
public.site.register(CodeBanner, CodeBannerViews)
public.site.register(ContentBase, ContentBaseViews)
public.site.register(Competition, CompetitionViews)
public.site.register(Entry, EntryViews)
public.site.register(Event, EventViews)
public.site.register(Gallery, GalleryViews)
public.site.register(ImageBanner, ImageBannerViews)
public.site.register(Post, PostViews)
public.site.register(User, UserViews)
