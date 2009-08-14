.. _django_test_database_and_postgis:

PostGIS and the Django test database
====================================

When django runs tests it creates a new database from scratch. This isolates 
test data from your production or development environment. Without proper
configuration, this database will lack the PostGIS functions needed to run
those tests and reproduce MarineMap's data model.

There are two different approaches to getting PostGIS working within these 
newly created databases.

Configuring django to spatially-enable the new databases
--------------------------------------------------------

If altering the properties of every newly created database is undesirable, 
GeoDjango has made the process of spatially-enabling just the test databases 
easier. See `Testing GeoDjango Apps <http://geodjango.org/docs/testing.html?highlight=testing#testing-geodjango-apps>`_.

Adding PostGIS to the default template
--------------------------------------

Another option is to spatially-enable all databases created on your system.
By default new databases are created from a template called ``template1``. 
Any functions or data added to this template will appear in the new databases,
whether they are created by the django test framework, another tool, or the
postgres shell itself.

The PostGIS documentation has a section on `spatially-enabling a database <http://postgis.refractions.net/documentation/manual-1.4/ch02.html#id2532099>`_.
Simply follow those instructions, installing spatial functions and the 
reference system into ``template1``.