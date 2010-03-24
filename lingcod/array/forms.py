#from django.contrib.admin.widgets import AdminFileWidget
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django import forms
from lingcod.array.models import MpaArray
from lingcod.rest.forms import UserForm
from os.path import splitext,split

class AdminFileWidget(forms.FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = ['<p>']
        if value and hasattr(value, "name"):
            filename = split(value.name)[-1]
            output.append('%s %s</p> <p>%s ' % ('Currently:', filename, 'Change:'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        output.append("</p>")
        return mark_safe(u''.join(output))
 
# http://www.neverfriday.com/sweetfriday/2008/09/-a-long-time-ago.html
class FileValidationError(forms.ValidationError):
    def __init__(self):
        super(FileValidationError, self).__init__('Document types accepted: ' + ', '.join(ValidFileField.valid_file_extensions))

class ValidFileField(forms.FileField):
    """A validating document upload field"""
    valid_file_extensions = ['odt', 'pdf', 'doc', 'xls', 'txt', 'csv', 'kml', 'kmz', 'jpeg', 'jpg', 'png', 'gif', 'zip']

    def __init__(self, *args, **kwargs):
        super(ValidFileField, self).__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        f = super(ValidFileField, self).clean(data, initial)
        if f:
            ext = splitext(f.name)[1][1:].lower()
            if ext in ValidFileField.valid_file_extensions: 
                # check data['content-type'] ?
                return f
            raise FileValidationError()


class ArrayForm(UserForm):
    supportfile1 = ValidFileField(widget=AdminFileWidget,required=False,label="Support File", 
            help_text="e.g. Narrative Summary or other document associated with this array.")
    supportfile2 = ValidFileField(widget=AdminFileWidget,required=False,label="Additional Support File")

    class Meta:
        model = MpaArray
