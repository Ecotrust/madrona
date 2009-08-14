.. _study_region:

The Study Region
================

What is the Study Region?
*************************

The Study Region is a `multipolygon <http://geodjango.org/docs/geos.html#multipolygon>`_
that refers to all areas within which new Marine Protected Areas may be 
proposed. Often this is based on a combination of factors including the 
administrative jurisdiction of the agency implementing the MPAs, biogeography,
and the logistics of running a design process across a wide area. For example,
the `Marine Life Protection Act Initiative <http://www.dfg.ca.gov/mlpa/>`_ 
proceeded with establishing MPAs by breaking up the state into 5 study 
regions. Each study region was addressed in series, and the study region was 
limited to state waters because the process was backed by state legislation.

The Study Region is the fundamental unit by which MarineMap implementations 
are built. To support the `California MLPA Initiative <http://www.dfg.ca.gov/mlpa/>`_, 
5 instances of MarineMap would need to be built and run. MarineMap clips all 
Marine Protected Areas to the Study Region boundaries. It also uses the Study 
Region bounds to determine the default extent of the map.

Adding a Study Region
*********************

If you are building an implementation of MarineMap based on the ``simple`` 
example project, there should already be a Study Region in place that was 
added to the database from a fixture after the ``syncdb`` management command was
run. 

To customize the Study Region, new objects can be created using the admin 
interface. In nearly all circumstances, the existing Study Region(s) should
not be deleted or modified, instead ADD a new Study Region. MarineMap will 
reference the latest Study Region created by default.

Changing a Study Region on a Deployed App
*****************************************

Changing the Study Region boundaries on a deployed application presents many 
problems.

  * All Marine Protected Areas affected by the Study Region geometry changes will need to be re-clipped.
  * Any reports associated with those MPAs will need to be regenerated.
  * Some cached data structures such as the network graph used for calculating Array spacing will need to be regenerated.
  
When you change the active Study Region by adding a new one, the difference 
between it and the previous study region can be calculated to determine which
MPAs are affected. Reports cached for these MPAs will expire, so the next time
they are requested it may take longer to retrieve the results until they are
cached again.
