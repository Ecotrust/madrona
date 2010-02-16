from django import template
from django.template import resolve_variable
register = template.Library()
from django.template import Variable
from lingcod.geographic_report.models import GeographicReport
from django.contrib.gis.measure import Area
from django.utils import simplejson
import random

@register.tag(name="geographic_report")
def do_geographic_report(parser, token):
    """Returns a string that is a unique identifier for a given model for
    the REST Framework.
    """
    tokens = token.split_contents()
    persist = ''
    if len(tokens) == 5:
        name = tokens[1]
        area = tokens[2]
        persist = tokens[3]
        tab_id = tokens[4]
    else:
        raise template.TemplateSyntaxError, "%r tag accepts a report name and an area value (in square meters)." % token.contents.split()[0]
    return GeographicReportNode(name, area, persist, tab_id)

class GeographicReportNode(template.Node):
    def __init__(self, name, area, persist, tab_id):
        self.name = name
        self.area = area
        self.persist = persist
        self.tab_id = tab_id
    
    def render(self, context):
        report = GeographicReport.objects.get(name=self.name)
        area = Area(sq_m=Variable(self.area).resolve(context))
        random_id = "%s-%s" % (report.name, random.randint(1, 10000))
        json = {
            'maxScale': report.max_scale, 
            'annotations': [],
            'element': '#%s' % (random_id, )
        }
        for annotation in report.annotation_set.all():
            json['annotations'].append({
                'label': annotation.label,
                'min': annotation.min,
                'max': annotation.max,
                'color': '#%s' % (annotation.color, ) })
                
        json = simplejson.dumps(json)
        return """
            <div id="%s" class="geographic_report"></div>
            <script type="text/javascript" charset="utf-8">
                lingcod.onTabShow('%s', function(ui){
                    var persist_id = '%s';
                    var report = lingcod.persistentReports[persist_id];
                    if(report){
                        $('#%s').append(report.paper.canvas);
                    }else{
                        report = lingcod.geographicReport(%s);
                        lingcod.persistentReports[persist_id] = report;
                    }
                    report.updateValue(%s, true);
                });
            </script>
        """ % (random_id, self.tab_id, self.persist, random_id, json, area.sq_mi)