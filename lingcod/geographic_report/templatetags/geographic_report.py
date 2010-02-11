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
    if len(tokens) >= 3:
        name = tokens[1]
        area = tokens[2]
        if len(tokens) == 4:
            persist = tokens[3]
    else:
        raise template.TemplateSyntaxError, "%r tag accepts a report name and an area value (in square meters)." % token.contents.split()[0]
    return GeographicReportNode(name, area, persist)

class GeographicReportNode(template.Node):
    def __init__(self, name, area, persist):
        self.name = name[1:(len(name)-1)]
        self.area = area
        self.persist = persist
    
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
            <div id="%s" class="geographic_report" />
            <script type="text/javascript" charset="utf-8">
                lingcod.panelEvents({
                    show: function(el){
                    var persist_id = '%s';
                        if(persist_id){
                            var report = lingcod.persistentReports[persist_id];
                            if(report){
                                $('#%s').append(report.paper.canvas);
                            }else{
                                report = lingcod.geographicReport(%s);
                                lingcod.persistentReports[persist_id] = report;
                            }
                            report.updateValue(%s, true);
                        }
                    },
                    close: function(el){
                        
                    }
                });
            </script>
        """ % (random_id, self.persist, random_id, json, area.sq_mi)