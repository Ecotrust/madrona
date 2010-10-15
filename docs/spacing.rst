.. _spacing:

The Spacing App
====================

Introduction
************
The spacing app's mission in life is to find the shortest distance between points without crossing given polygons. It's called the spacing app because it was created to address the "Spacing Guidelines" problem in the California Marine Life Protection Act where we needed to know the minimum distance a fish (or a larvae of some sort) would have to swim to get from one point in the ocean to another without crossing land.  Many of the naming conventions in the spacing app are geared toward this problem but, in reality, it could easily be used in any situation where you want to find the shortest distance between two points without crossing a polygon.  Please keep this in mind throughout the rest of this document because, in order to simplify the documentation, I'm going to call the polygons you don't want to cross as "land" and thing that's traveling the path will be the "fish".

Overview of How it Works 
************************
The heart of the spacing app is a bidirectional version of Dijkstra's algorithm as implemented in the NetworkX Python library (http://networkx.lanl.gov/). The spacing app builds a net graph from the "land" polygon that you give it. The vertices of the polygon become the nodes of the graph. The edges are a bit more complicated. For each node, we create a line to every other node. Each line is tested to see if it crosses the "land" polygon. If it does, we throw out that line and move on. If it does not, then we create an edge between those two nodes weighted with the distance of the line. So, when we're all done, we have a graph where each node represents a vertex and each edge represents a straight path between vertices that does not cross land. Generating this graph is the most time consuming part of the process so, once it's done, we pickle it and store it.

Once we've created the graph and stored it, we are ready to find the shortest distance between two points outside the "land" polygon that does not cross that polygon. In the code this distance is called "fish distance" because in the original use case it represents the shortest distance a fish could swim between two points. When you pass two points to the fish_distance method, the pickled graph is retrieved, the two points are added to the graph as nodes, non land crossing edges are added for those points, the dijkstra algorithm finds the shortest path between those points, and then returns both the actual GEOS line geometry of the path and the length of that path. Well actually before the fish_distance method goes through all that trouble, it checks to see if a straight line between the two points can be created without crossing "land". If it can, then that line and the length of that line are returned so that we don't have to go through the trouble (and processor time) of adding the nodes and calculating all the edges.

Overview of Extra Features
**************************
The section above explains the basic mechanics of how the app works but there's some extra stuff built on top of that. That's right, bonus features! There are a number of methods dedicated to building "spacing matrices". Basically, you can submit a list of points and get back a table that includes the "fish distance" between each point and every other point. The spacing app gives you a model in which to store "Spacing Points" which will be included in any spacing matrix outputs. Additionally, there are a number of methods and views that allow you to visualize your "land" polygon and your network graph as kml. Most of these features are well explained in comments within the code.

Using the Spacing App
*********************

1. Draw your "land" polygon using the Django admin for the Land model (you can also use Qgis to draw the feature and load it into you PostGIS db table for the Land model). The smaller the number of vertices, the faster the spacing calculations will run so you should simplify your polygon as much as you possibly can. If you have islands, each should be a separate polygon.  The land model does not accept multipolygons. If your working with a coast line, make sure your "land" polygon extends a long way inland.  You don't want any shortest distance paths to be found that go around the inland side of your "land" polygon.
2. Click on "Pickled Graph" in the Django admin tool for the spacing app.
3. Click the "Regenerate pickled graph" button on the top right side of the list view for the Pickled Graph model. Do this anytime changes are made to the Land features and you want those changes applied to the pickled graph.
4. Use the admin to add any points you want included in spacing matrices to the Spacing Point model.
5. Use the urls specified in spacing/urls.py to access spacing results and visualization methods.