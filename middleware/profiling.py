import sys
import tempfile
import hotshot
import hotshot.stats
from django.conf import settings
from cStringIO import StringIO

class ProfileMiddleware(object):
    """
    Source from http://www.djangosnippets.org/snippets/186/

    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode,
    but you really shouldn't add this middleware to any production configuration.
    * Only tested on Linux
    """
    def process_request(self, request):
        if settings.DEBUG and request.GET.has_key('prof'):
            self.tmpfile = tempfile.NamedTemporaryFile()
            self.prof = hotshot.Profile(self.tmpfile.name)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and request.GET.has_key('prof'):
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and request.GET.has_key('prof'):
            self.prof.close()

            out = StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile.name)
            #stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:

                stats_str_lines = stats_str.split('\n')
                header_lines = stats_str_lines[:5]
                body_lines = stats_str_lines[5:]
                body_lines = self.filter_lines(request, body_lines)
                body_lines = self.emphasize_lines(request, body_lines)

                lines = header_lines + body_lines

                response.content = "<pre>" + '\n'.join(lines) + "</pre>"

        return response

    def filter_lines(self, request, lines):
        filtered_lines = []
        if request.GET.has_key('filter'):
            filter = request.GET['filter']
        
            for line in lines:
                if filter in line:
                    filtered_lines.append(line)
            return filtered_lines
            
        else:
            return lines
    
    def emphasize_lines(self, request, lines):
        formatted_lines = []
        if request.GET.has_key('em'):
            filter = request.GET['em']
        
            for line in lines:
                if filter in line:
                    line = "<strong>%s</strong>" % line
                formatted_lines.append(line)
            return formatted_lines
            
        else:
            return lines
