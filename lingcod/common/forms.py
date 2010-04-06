from django.forms import Textarea
from django.utils.safestring import mark_safe

class ShortTextarea(Textarea):
    """
    Provides a textarea widget which uses a simple js statement to limit the 
    number of chars. 

    example usage: widget=ShortTextarea(limit=45, rows=3, cols=15)
    """
    def __init__(self, attrs={}, limit=1024, rows=10, cols=50):
        super(ShortTextarea, self).__init__(attrs)
        self.limit = int(limit)
        self.rows = int(rows)
        self.cols = int(cols)

    def render(self, name, value, attrs=None):
        output = ['<p>']
        chars_used = 0
        if value:
            chars_used = len(value)

        if chars_used > self.limit:
            alert_truncate = "true"
        else:
            alert_truncate = "false"

        js_snip = 'limit_to(this, %d, "%s_chars_used", %s);' % (self.limit, name, alert_truncate)
        attrs = { 
            'rows': '%d' % self.rows,
            'cols': '%d' % self.cols,
            'id': 'id_%s' % name,
            'onKeyUp': js_snip, 
            'onKeyDown': js_snip,
            'onChange': js_snip,
        }
        output.append(super(ShortTextarea, self).render(name, value, attrs))
        output.append("</p>")
        if chars_used > self.limit:
            output.append("<p style='color:red;font-weight:bold;'>Editing this field will truncate text to %d characters</p>" % self.limit)
        output.append("<p><span id='%s_chars_used'>%d</span> characters of %d limit entered.</p>" % (name, chars_used, self.limit))

        return mark_safe(u''.join(output))

    class Media:
        js = ('common/js/layout/shortTextArea.js',)
