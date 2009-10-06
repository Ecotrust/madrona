from spacing.models import *
import matplotlib.pyplot as plt
import mapnik

p1 = TestPoint.objects.get(name='p1')
p2 = TestPoint.objects.get(name='p2')
p3 = TestPoint.objects.get(name='p3')
ocean_line = geos.LineString(p1.geometry, p2.geometry)
land_line = geos.LineString(p1.geometry, p3.geometry)
G = nx.Graph()