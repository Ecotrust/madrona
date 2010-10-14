.. _spacing:

The Spacing App
====================

Introduction
************
The spacing app's mission in life is to find the shortest distance between points without crossing given polygons. It's called the spacing app because it was created to address the "Spacing Guidelines" problem in the California Marine Life Protection Act where we needed to know the minimum distance a fish (or a larvae of some sort) would have to swim to get from one point in the ocean to another without crossing land.  Many of the naming conventions in the spacing app are geared toward this problem but, in reality, it could easily be used in any situation where you want to find the shortest distance between two points without crossing a polygon.  Please keep this in mind throughout the rest of this document because, in order to simplify the documentation, I'm going to call the polygons you don't want to cross as "land" and thing that's traveling the path will be the "fish".

How it Works
************
The heart of the spacing app is a bidirectional version of Dijkstra's algorithm as implemented in the NetworkX Python library (http://networkx.lanl.gov/). The spacing app builds a net graph from the "land" polygon that you give it. The vertices of the polygon become the nodes of the graph. The edges are a bit more complicated. For each node, we create a line to every other node. Each line is tested to see if it crosses the "land" polygon. If it does, we throw out that line and move on. If it does not, then we create an edge between those two nodes weighted with the distance of the line. So, when we're all done, we have a graph where each node represents a vertex and each edge represents a straight path between vertices that does not cross land.