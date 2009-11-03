# Copyright (c) 2009, Jurie-Jan Botha
#
# This file is part of the 'richtext' Django application.
#
# 'richtext' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 'richtext' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


from django import forms
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class RichTextWidget(forms.TextInput):
    class Media:
        js = (
            '/media/richtext/js/nicEdit.js',
        )

    def __init__(self, attrs=None):
        super(RichTextWidget, self).__init__(attrs=attrs)
        self.media_url = reverse('media', urlconf='broadcastcms.richtext.urls', args=[''])

    def render(self, name, value, attrs={}):
        attrs['id'] = 'id_%s' % name
        attrs['value'] = value
        attrs['name'] = name
        attrs['media_url'] = self.media_url
        if not attrs.has_key('class'): attrs['class'] = ''

        return mark_safe(u'''
            <div style="padding-left:106px;">
            <textarea id="%(id)s" class="%(class)s" name="%(name)s" cols="100">%(value)s</textarea>
            <script type="text/javascript">
                %(id)s = new nicEditor({
                    iconsPath:'%(media_url)s/img/nicEditorIcons.gif',
                    buttonList: [
                        'bold', 'italic', 'undeline', 'left', 'center', 'right',
                        'justify', 'ol', 'ul', 'strikethrough', 'removeformat',
                        'indent', 'outdent', 'hr', 'forecolor', 'link', 'unlink',
                        'xhtml'
                    ]
                }).panelInstance('%(id)s');
            </script>
            </div>
        ''' % attrs)
