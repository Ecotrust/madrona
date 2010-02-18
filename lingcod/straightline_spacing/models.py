from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.gis.measure import A, D

class SpacingPoint(models.Model):
    name = models.CharField(max_length=200)
    geometry = models.PointField(srid=settings.GEOMETRY_DB_SRID)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return unicode(self.name)
        
def all_spacing_points_dict():
    """
    Returns a dictionary of the form: { point: 'name' } for all objects in SpacingPoint
    """
    return dict( [ (p.geometry,p.name) for p in SpacingPoint.objects.all() ] )
    
def add_all_spacing_points(in_dict):
    """
    Takes a dictionary of the form: { point: 'name' }, and adds all the objects in SpacingPoint
    """
    in_dict.update(all_spacing_points_dict())
    return in_dict

def distance_row_dict(from_dict, to_dict):
    """
    from_dict will be a dict with a point as the key and a label as the value.
    to_dict will be of the same format with multiple entries.
    will return a dictionary with points as keys and a dictionary as values.
    NOTE: This method assumes that the projection units are meters.
    """
    from_pnt = from_dict.keys()[0]
    for s_pnt in SpacingPoint.objects.all():
        to_dict.update({s_pnt.geometry:s_pnt.name})
    result = {}
    for point, pnt_label in to_dict.iteritems():
        result[point] = {
            'label': pnt_label,
            'distance': D(m=point.distance(from_pnt)).mi,
            'sort': point.y
        }
    return result
    
def distance_row_list(from_pnt, to_list):
    """
    NOTE: This method assumes that the projection units are meters.
    """
    result = []
    for point in to_list:
        result.append(D(m=point.distance(from_pnt)).mi)
    return result
    
def distance_matrix(point_list):
    result = []
    for point in point_list:
        result.append(distance_row_list(point,point_list))
    return result
    
def sorted_points_and_labels(in_dict):
    """
    in_dict will look like:
    { point: 'name' }
    sorted_points, sorted_labels (both lists) will be returned in a dictionary and they'll be 
    ordered from North to South.
    """
    sorted_points = []
    sorted_labels = []
    y_dict = {}
    for point, name in in_dict.iteritems():
        y_dict.update( { point.y: point } )
    y_list = y_dict.keys()
    y_list.sort()
    for y in reversed(y_list):
        sorted_points.append(y_dict[y])
        sorted_labels.append(in_dict[y_dict[y]])
    return { 'points': sorted_points, 'labels': sorted_labels }
    
def distance_matrix_and_labels(in_dict,add_spacing_points=True):
    """
    in_dict will look like:
    { point: 'name' }
    Will return a dictionary with the keys 'labels' and 'matrix'
    """
    if add_spacing_points:
        in_dict = add_all_spacing_points(in_dict)
    spl_dict = sorted_points_and_labels(in_dict)
    dist_mat = distance_matrix(spl_dict['points'])
    return { 'labels': spl_dict['labels'], 'matrix': dist_mat }