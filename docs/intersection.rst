.. _intersection:

The Intersection App
====================

Introduction
************

The basis of habitat reporting in MarineMap is knowing how much habitat is captured within each MPA. Habitats can be represented as points, lines, or polygons. These habitat features generally come to us as shapefiles with wildly varying schemas. The intersection app assists in the process of resolving these various schemas into single feature shapefiles.

Once the habitat features are in simple single feature shapefiles, the intersection app lets you import them in into the database as intersection features. The features are then available to do intersections with. However, the more common use case will be to define an organization scheme first. Organization schemes let you define the order in which feature results are reported and let you combine existing features of the same type (two or more polygon features, for instance) into a single result.

Once the feature data is loaded into the intersection application and the organization scheme is defined, intersection results may be obtained either by directly calling a method of the OrganizationScheme object in the intersection app with a polygon or geometry collection as an argument or through an http request that includes a polygon in the URL.

Using the Intersection App
**************************

Getting Intersection Features into the Intersection App
-------------------------------------------------------

In order to find out how much of a particular feature intersects with a given polygon, we first have to get the intersection feature into the database. Having each intersection feature represent a single habitat (as opposed to representing different habitats specified by an attribute) provides the greatest flexibility and constancy. The primary format for habitat data (in our experience so far) are shapefiles. The schemes of these shapefile data sources vary considerably.

The Difference Between Multi Feature and Single Feature Shapefiles
------------------------------------------------------------------
Sometimes, as is the case with the MLPA linear kelp data sets, the presence of geometry indicates the presence of the habitat. We'll refer to this type of shapefile as a Single Feature Shapefile.

In other cases, a shapefile may contain geometries that represent any number of different habitats according to how each individual geometry is attributed. An example of one of these Multi Feature Shapefiles is available `here <http://code.google.com/p/marinemap/source/browse/trunk/lingcod/intersection/test_data/test_substrate.zip>`_. That example is a portion of the substrate data set used in the South Coast MLPA process. The shapefile consists of polygons with a sub_depth attribute (among others). Some values of this attribute are 'Hard 0 - 30m', 'Soft 30 - 50m', etc. If we want to know, for instance, how much hard substrate with a depth of 0 - 30 meters is within a given polygon, we want to intersect that polygon with a set of geometries that represent just that habitat type. In other words, we want to intersect with a single feature rather than a multi feature.

Turning a Multi Feature Shapefile into Single Feature Shapefiles
----------------------------------------------------------------
The intersection app admin can take a zipped multi feature shapefile that has been uploaded and split it into the necessary number of zipped single feature shapefiles. Once the intersection app is installed and running, you may want to follow these steps in order to acquaint yourself with the app:

1. Download the sample substrate shapefile to your computer.
2. Log in to the django admin tool for the intersection app.
3. Click on 'Multi feature shapefiles' in the intersection admin.
4. Click the 'Add multi feature shapefile' button on the top right.
5. Type 'Substrate' into the name field.
6. Click 'Choose File' and select the sample shapefile (make sure you chose the zipped file) that you downloaded in step 1.
7. Click the Save button on the bottom right. You will be taken back to the 'Multi feature shapefiles' list.
8. Click on the multi feature shapefile you just created (it should be called 'Substrate').
9. Click on the 'Split to Single Feature Shapefiles' button on the top right.
10.  Chose the shapefile field you want to use to split the multi feature shapefile into single feature shapefiles.

When you click the submit button, you will be taken to the list of single feature shapefiles and you will see that one single feature shapefile has been created for each distinct value in the field that you split on.

Importing Features from Single Feature Shapefiles
-------------------------------------------------

Once we have a single feature shapefile, whether it was started life as a single feature shapefile and was imported as such or it started as a multi feature shapefile and was split by the admin tool, we can add it to the Intersection Features model and make it available for intersections. The following assumes that you've followed the steps above:

1. Click on "Single feature shapefiles" in the intersection admin.
2. Select all the substrate shapefiles that were created when you split the multi feature shapefile.
3. Select "Load the selected shapefiles to intersection features" from the "Action" drop down near the top of the page and click "Go".

This will take you to the list of Intersection Features and you'll see that each of those single feature shapefiles have been imported into the database.

Running Test Intersections Within the Intersection App
------------------------------------------------------

You may want to play around with the intersection app independently of the other apps in your project. You can do that in a couple of different ways. You can draw polygons and get results for the intersection features you have loaded into the application. You can also create test polygons in the admin tool, save them, and get intersection results on them repeatedly. This helps in evaluating how results are cached.

Drawing a Polygon and Getting Intersection Results
--------------------------------------------------

Go to http://YOUR-HOST/intersection/intersect/testdrawing/
Draw a polygon over some portion of the intersection features you've loaded (if you've been following along, that'll be a small portion of the coast just off shore of Point Conception).
Choose the organization scheme and format for your results.
Click the "Submit" button.