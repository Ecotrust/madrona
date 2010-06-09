from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.core.files import File
from django.db import connection
from django.conf import settings
from exceptions import AttributeError
import os
import tempfile
import pickle
import networkx as nx


### Display Methods ###
# These methods are used by the spacing views
def kml_doc_from_geometry_list(geom_list, template='general.kml'):
    out_dict = {}
    placemarks = []
    for geom in geom_list:
        placemarks.append( kml_placemark_from_geom(geom) )
    out_dict['placemarks'] = placemarks
    from django.template import Context, Template
    from django.template.loader import get_template
    t = get_template(template)
    response = t.render(Context({ 'kml': out_dict }))
    return response
    
def kml_doc_from_queryset(qs, template='general.kml'):
    dict = {}
    placemarks = []
    for item in qs:
        placemarks.append( kml_placemark(item) )
    dict['placemarks'] = placemarks
    from django.template import Context, Template
    from django.template.loader import get_template
    t = get_template(template)
    response = t.render(Context({ 'kml': dict }))
    return response

def kml_placemark_from_geom(geom, styleUrl='#default'):
    geom.transform(settings.GEOMETRY_CLIENT_SRID)
    style = '<styleUrl>%s</styleUrl>' % styleUrl
    return_kml = '<Placemark>%s%s</Placemark>' % (style,geom.kml)
    return return_kml

def kml_placemark(qs_item, styleUrl='#default', geo_field='geometry'):
    geom = qs_item.__getattribute__(geo_field)
    geom.transform(4326)
    try:
        name = qs_item.name
    except AttributeError:
        name = qs_item.model.__name__
    name = '<Name>%s</Name>' % name
    
    style = '<styleUrl>%s</styleUrl>' % styleUrl
    return_kml = '<Placemark>%s%s%s</Placemark>' % (name,style,geom.kml)
    return return_kml
### End Display Methods ###
    
class PickledGraph(models.Model):
    """
    This model gives us someplace to put our pickle.  No, really that's 
    what it does.  There should only be one record in this model at any
    given time.  This model just stores THE graph.
    """
    pickled_graph = models.FileField(upload_to='spacing/pickled_graphs')
    
    @property
    def graph(self):
        f = open(self.pickled_graph.path,'r')
        graph = pickle.load(f)
        return graph

def create_pickled_graph(verbose=False):
    # get rid of existing
    PickledGraph.objects.all().delete()
    tf = tempfile.NamedTemporaryFile()
    graph = nx.Graph()
    graph = add_land_to_graph(graph,verbose=verbose)
    # add spacing points to graph
    points = [ sp.geometry for sp in SpacingPoint.objects.all() ]
    graph = add_points_to_graph(points,graph)
    pickle.dump(graph, tf)
    pg = PickledGraph()
    pg.pickled_graph = File(tf)
    pg.save()
    tf.close()
    return graph
    
class Land(models.Model):
    """
    This is where a simplified polygon representation of land gets stored.  The greater the number of verticies, the slower the distance analysis
    so don't get too fancy.  Land can be made up of multiple polygons but each polygon gets it's own single polygon record.
    """ 
    name = models.CharField(max_length=200, null=True, blank=True)
    geometry = models.PolygonField(srid=3310,null=True, blank=True)
    objects = models.GeoManager()
    
    def add_hull_nodes_to_graph(self, graph):
        """
        This is for only adding the nodes of the convex hull to the graph.  I don't think this will be used in most cases but,
        in some cases, it could be effective at reducing the number of nodes in the graph and speeding things up.
        """
        poly = self.geometry#.buffer(5).simplify(1)
        
        graph.add_nodes_from([geos.Point(p) for p in poly.convex_hull.shell])
        return graph
    
    def add_nodes_to_graph(self, graph):
        poly = self.geometry
        
        graph.add_nodes_from([geos.Point(p) for p in poly.shell])
        return graph
    
    def create_hull(self): 
        """
        probably don't need this method in the long run because we won't really need to keep the hull
        """
        hull, created = Hull.objects.get_or_create(land=self)
        hull.geometry = self.geometry.convex_hull
        hull.save()
        
    def geometry_kml(self):
        geom = self.geometry
        geom.transform(4326)
        return geom.kml
        
    def kml(self):
        from django.template import Context, Template
        from django.template.loader import get_template
        t = get_template('land.kml')
        response = t.render(Context({ 'land': self }))
        return response
    
    def simplify(self, tolerance=500):
        self.geometry = self.geometry.simplify(tolerance=tolerance, preserve_topology=True)
        self.geometry = geos.Polygon(self.geometry.exterior_ring)
        self.save()

### Spacing matrix models and methods ###
# This stuff is related to building a spacing matrix for a set of points
class SpacingPoint(models.Model):
    """
    This model is used when generating a spacing matrix.  Points contained here will be added to the array
    of points that you are creating a spacing matrix for.  In the MLPA process this is used to add the 
    points at the northern and southern extreme of the study region.
    """
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
    
def distance_row_list(from_pnt, to_list, straight_line=False, with_geom=False):
    """
    NOTE: This method assumes that the projection units are meters.
    """
    result = []
    for point in to_list:
        point_pair_dict = {}
        if straight_line:
            point_pair_dict.update( {'distance': D(m=point.distance(from_pnt)).mi } )
            if with_geom:
                line = geos.LineString(point,from_pnt)
        else:
            distance, line = fish_distance_from_edges(from_pnt,point)
            point_pair_dict.update( {'distance': distance} )
        if with_geom:
            point_pair_dict.update( {'geometry': line} )
        result.append(point_pair_dict)
    return result
    
def distance_matrix(point_list, straight_line=False, with_geom=False):
    result = []
    for point in point_list:
        result.append(distance_row_list(point,point_list,straight_line=straight_line,with_geom=with_geom))
    return result
    
def sorted_points_and_labels(in_dict):
    """
    in_dict will look like:
    { point: 'name' }
    sorted_points, sorted_labels (both lists) will be returned in a dictionary and they'll be 
    ordered from North to South.
    
    I added in an if statement that makes this method work with other geometry types aside from
    points.  I should change the name of the method to make for sense but I'm going to put that
    off until later.
    """
    sorted_points = []
    sorted_labels = []
    y_dict = {}
    for point, name in in_dict.iteritems():
        # adapt this to work with other geometry types:
        if point.__class__.__name__.lower() == 'point':
            y_dict.update( { point.y: point } )
        else:
            y_dict.update( { point.centroid.y: point })
    y_list = y_dict.keys()
    y_list.sort()
    for y in reversed(y_list):
        sorted_points.append(y_dict[y])
        sorted_labels.append(in_dict[y_dict[y]])
    return { 'points': sorted_points, 'labels': sorted_labels }
    
def distance_matrix_and_labels(in_dict,add_spacing_points=True,straight_line=False,with_geom=False):
    """
    in_dict will look like:
    { point: 'name' }
    Will return a dictionary with the keys 'labels' and 'matrix'
    """
    if add_spacing_points:
        in_dict = add_all_spacing_points(in_dict)
    spl_dict = sorted_points_and_labels(in_dict)
    dist_mat = distance_matrix(spl_dict['points'], straight_line=straight_line, with_geom=with_geom)
    return { 'labels': spl_dict['labels'], 'matrix': dist_mat }
    
### End of spacing matrix methods ###

def add_points_to_graph(points,graph):
    """
    points is a list of points.  graph is a NetworkX graph.
    """
    graph.add_nodes_from(points)
    for pnt in points:
        graph = add_ocean_edges_for_node(graph,get_node_from_point(graph, pnt))
    return graph
    
def fish_distance(point1,point2):
    """
    Returns the shortest distance around land (see the Land model) between the two points.  Returns the distance in miles and
    the geos linestring that represents the path.
    
    NOTE: I'm assuming that the native units of the points and line is meters.  This is true for the MLPA project but may
    not be true for other processes.
    """
    # This is the straight line between the two points
    line = geos.LineString(point1,point2)
    
    # See if the straight line crosses land
    if line_crosses_land(line): 
        # The straight line cut across land so we have to do it the hard way.
        G = PickledGraph.objects.all()[0].graph
        G = add_points_to_graph([point1,point2],G)
        # G.add_nodes_from([point1,point2])
        # G = add_ocean_edges_for_node(G,get_node_from_point(G,point1))
        # G = add_ocean_edges_for_node(G,get_node_from_point(G,point2))
        # Replace the straight line with the shortest path around land
        line = geos.LineString( nx.dijkstra_path(G,get_node_from_point(G,point1),get_node_from_point(G,point2)) )
        line.srid = settings.GEOMETRY_DB_SRID
    
    # Figure out the distance of the line (straight or otherwise) in miles
    distance = D(m=line.length).mi
    return distance, line
    
def fish_distance_from_edges(geom1,geom2):
    """
    
    """
    # Straight line between geoms
    line = shortest_line(geom1,geom2)
    
    # See if the line crosses land
    if line_crosses_land(line):
        # Get shortest centroid to centroid fish_distance line
        c_distance, c_line = fish_distance(geom1.centroid,geom2.centroid)
        # Replace the first point in the fish path with the point on geom1
        # that lies closest to the second point on the path.
        #print c_line[1]
        c_line[0] = closest_point(geom1, geos.Point( c_line.coords[1] ) ).coords
        # Do the same for the last point in the path
        c_line[c_line.num_points - 1] = closest_point(geom2, geos.Point( c_line.coords[c_line.num_points - 2] ) ).coords
        line = c_line
    # Adjust the distance
    distance = D(m=line.length).mi
    return distance, line

def get_node_from_point(graph, point):
    for node in graph.nodes_iter():
        if node == point:
            return node

def position_dictionary(graph):
    """
    can be used by nx.draw to position nodes with matplotlib.  This is not used in the general functioning of 
    the spacing app but is useful for visual testing.  If you have a networkx graph G, then you can use it like:
    nx.draw(G,pos=position_dictionary(G)) To see the result, use matplotlib.pyplot.show()
    """
    pos = {}
    for n in graph.nodes_iter():
        pos[n] = (n.x, n.y)
    return pos
    
def add_land_to_graph(graph, hull_only=False, verbose=False):
    if verbose:
        print 'Adding land nodes to graph'
    for l in Land.objects.iterator():
        if hull_only:
            graph = l.add_hull_nodes_to_graph(graph)
        else:
            graph = l.add_nodes_to_graph(graph)
    
    graph = add_ocean_edges_complete(graph,verbose=verbose)
    return graph    

def points_from_graph(graph):
    """
    Return a list of points from a graph.
    """
    g_nodes = graph.nodes()
    for point in g_nodes:
        if point.srid == None:
            point.srid = settings.GEOMETRY_DB_SRID
    return g_nodes
    
def lines_from_graph(graph):
    """
    Return a list of lines made from the edges of a graph.
    """
    lines = []
    for g_edge in graph.edges():
        line = geos.LineString(g_edge[0],g_edge[1])
        line.srid = settings.GEOMETRY_DB_SRID
        lines.append(line)
    return lines        
    
def line_crosses_land(line):
    land = Land.objects.all()
    crosses = False
    for l in land:
        if line.intersects(l.geometry.buffer(-1)):
            crosses = True
    return crosses

def add_ocean_edges_for_node(graph, node):
    for n in graph:
        line = geos.LineString(node,n)
        if not line_crosses_land(line):
            graph.add_edge(node,n,{'weight': D(m=node.distance(n)).mi})
    return graph

def add_ocean_edges_complete(graph, verbose=False):
    if verbose:
        cnt = 1
        import time
        t0 = time.time()
        print "Starting at %s to add edges for %i nodes." % (time.asctime(time.localtime(t0)), graph.number_of_nodes() )
        edge_possibilities = graph.number_of_nodes() * (graph.number_of_nodes() -1)
        print "We'll have to look at somewhere around %i edge possibilities." % ( edge_possibilities )
        print "Node: ",
    for node in graph.nodes_iter():
        if verbose:
            print str(cnt) + ' ',
            cnt += 1
        for n in graph.nodes_iter():
            if node <> n:
                line = geos.LineString(node,n)
                if not line_crosses_land(line):
                    graph.add_edge(node,n,{'weight': D(m=node.distance(n)).mi})
    if verbose:
        print "It took %i minutes to load %i edges." % ((time.time() - t0)/60, graph.number_of_edges() )
    return graph
    
def shortest_line(geom1,geom2):
    """
    Use the PostGIS function st_shortestline() to find the shortest line between two geometries.  This requires
    PostGIS 1.5 or newer.  This will return a line geometry that represents the shortest line between the two 
    given geometries.  Seems to work with any geometry type including geometry collections.
    """
    cursor = connection.cursor()
    query = "select st_astext( st_shortestline('%s'::geometry, '%s'::geometry) ) as sline;" % (geom1.wkt, geom2.wkt)
    cursor.execute(query)
    return geos.fromstr(cursor.fetchone()[0])
    
def closest_point(geom1,geom2):
    """
    Use the PostGIS function ST_ClosestPoint() to return the 2-dimensional point on geom1 that is closest to geom2.  This requires
    PostGIS 1.5 or newer.  
    """
    cursor = connection.cursor()
    query = "select st_astext( ST_ClosestPoint('%s'::geometry, '%s'::geometry) ) as sline;" % (geom1.wkt, geom2.wkt)
    cursor.execute(query)
    return geos.fromstr(cursor.fetchone()[0])

def clean_geometry(qs_item):
    cursor = connection.cursor()
    query = "update %s set geometry = cleangeometry(geometry) where %s = %i" % (qs_item._meta.db_table, qs_item._meta.pk.attname, qs_item.pk)
    cursor.execute(query)
    connection._commit()

def clean_query_set_geometries(qs):
    for qs_item in qs:
        if not qs_item.geometry.valid:
            clean_geometry(qs_item)