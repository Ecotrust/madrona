from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.db import connection
from exceptions import AttributeError
import os
import pickle
import networkx as nx

FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'pickled_graph'))
# Create your models here.

def kml_doc_from_queryset(qs):
    dict = {}
    placemarks = []
    for item in qs:
        placemarks.append( kml_placemark(item) )
    dict['placemarks'] = placemarks
    from django.template import Context, Template
    from django.template.loader import get_template
    t = get_template('general.kml')
    response = t.render(Context({ 'kml': dict }))
    return response

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
    
class Land(models.Model): #may want to simplify geometry before storing in this table
    name = models.TextField(null=True, blank=True)
    geometry = models.PolygonField(srid=3310,null=True, blank=True)
    objects = models.GeoManager()
    
    def add_hull_nodes_to_graph(self, graph):
        #buffer to put points offshore
        poly = self.geometry#.buffer(5).simplify(1)
        
        graph.add_nodes_from([geos.Point(p) for p in poly.convex_hull.shell])
        return graph
    
    def add_nodes_to_graph(self, graph):
        #buffer to put points offshore
        poly = self.geometry
        
        graph.add_nodes_from([geos.Point(p) for p in poly.shell])
        return graph
    
    def create_hull(self): #probably don't need this method in the long run because we won't really need to keep the hull
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
        

class OceanPath(models.Model):
    points = models.ManyToManyField('TestPoint', null=True, blank=True)
    geometry = models.LineStringField(srid=3310)
    objects = models.GeoManager()
    
## We probably won't need this model in the long run but I want to be able to see the convex hull in Q-gis
class Hull(models.Model):
    land = models.OneToOneField(Land, primary_key=True)
    geometry = models.PolygonField(srid=3310,null=True, blank=True)
    objects = models.GeoManager()
    
class TestPoint(models.Model):
    name = models.TextField()
    geometry = models.PointField(srid=3310)
    objects = models.GeoManager()
    
    def fish_distance_to(self, point):
        #first check if a straight line can connect the two points without crossing land
        line = geos.LineString(self.geometry, point.geometry)
        
        if not line_crosses_land(line):
            distance = D(m=line.length).mi
            return distance, line
        else:
            G = get_pickled_graph()
            G.add_node(self.geometry)
            G = add_ocean_edges_for_node(G,get_node_from_point(G,self.geometry))
            G.add_node(point.geometry)
            G = add_ocean_edges_for_node(G,get_node_from_point(G,point.geometry))
            line = geos.LineString( nx.dijkstra_path(G,get_node_from_point(G,self.geometry),get_node_from_point(G,point.geometry)) )
            distance = D(m=line.length).mi
            return distance, line

def fish_distance(point1,point2):
    tp1 = TestPoint(name='tp1', geometry=point1)
    tp2 = TestPoint(name='tp2', geometry=point2)
    distance, line = tp1.fish_distance_to(tp2)
    return distance, line

def add_test_points(points):
    cnt = 0
    for p in points:
        cnt += 1
        name = 'point_' + str(cnt)
        tp, created = TestPoint.objects.get_or_create(name=name,geometry=geos.Point(p))
        tp.save()

def get_node_from_point(graph, point):
    for node in graph.nodes_iter():
        if node == point:
            return node

def position_dictionary(graph):
    #can be used by nx.draw to position nodes
    pos = {}
    for n in graph.nodes_iter():
        pos[n] = (n.x, n.y)
    return pos

def setup_tests():
    p1 = TestPoint.objects.get(name='p1')
    p2 = TestPoint.objects.get(name='p2')
    p3 = TestPoint.objects.get(name='p3')
    ocean_line = geos.LineString(p1.geometry, p2.geometry)
    land_line = geos.LineString(p1.geometry, p3.geometry)
    G = nx.Graph()
    
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

def create_pickled_graph(file=FILE_PATH,verbose=False):
    # create a pickled graph with all nodes from Land and all edges that do not cross Land
    f = open(file, 'w')
    graph = nx.Graph()
    graph = add_land_to_graph(graph,verbose=verbose)
    pickle.dump(graph, f)
    f.close()
    return graph

def get_pickled_graph(file=FILE_PATH):
    f = open(file, 'r')
    graph = pickle.load(f)
    return graph

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
            graph.add_edge(node,n,D(m=node.distance(n)).mi)
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
                    graph.add_edge(node,n,D(m=node.distance(n)).mi)
    if verbose:
        print "It took %i minutes to load %i edges." % ((time.time() - t0)/60, graph.number_of_edges() )
    return graph

def clean_geometry(qs_item):
    cursor = connection.cursor()
    query = "update %s set geometry = cleangeometry(geometry) where %s = %i" % (qs_item._meta.db_table, qs_item._meta.pk.attname, qs_item.pk)
    cursor.execute(query)
    connection._commit()

def clean_query_set_geometries(qs):
    for qs_item in qs:
        if not qs_item.geometry.valid:
            clean_geometry(qs_item)