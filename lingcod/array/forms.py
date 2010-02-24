#from django.contrib.admin.widgets import AdminFileWidget
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django import forms
from lingcod.array.models import MpaArray
from lingcod.rest.forms import UserForm

class AdminFileWidget(forms.FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('<p>%s <a target="_blank" href="%s">%s</a></p><p>%s ' % \
                ('Currently:', value.url, value, 'Change:'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        output.append("</p>")
        return mark_safe(u''.join(output))


class ArrayForm(UserForm):
    supportfile1 = forms.FileField(widget=AdminFileWidget,required=False,label="Support File", 
            help_text="e.g. Narrative Summary or other document associated with this array")
    supportfile2 = forms.FileField(widget=AdminFileWidget,required=False,label="Additional Support File")

    class Meta:
        model = MpaArray
