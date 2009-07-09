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


from django.db import models
from django import forms
from widgets import RichTextWidget


class RichTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        return RichTextFormField()
        

class RichTextFormField(forms.fields.Field):
    def __init__(self, *args, **kwargs):
        self.widget = RichTextWidget()
        super(RichTextFormField, self).__init__(*args, **kwargs)