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
        js_snip = 'this.value = this.value.substring(0, %d);' % self.limit
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
        return mark_safe(u''.join(output))
