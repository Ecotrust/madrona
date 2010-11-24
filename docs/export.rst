.. _export:

Export Options
==============
In order to provide the user the opportunity to export their shapes into formats 
that are viewable (among other things) outside of MarineMap, 
MarineMap provides an Export option allowing the user to export individual 
shapes as well as arrays in a variety of formats.

Exporting as kmz and exporting as image are both built in to Lingcod and will 
appear by default in the Export drop-down menu.  

Exporting as shapefile requires the enabling of a urlpattern as explained below.

Atom links for each of these Export options can be found in ``lingcod/kmlapp/templates/placemarks.kml``.

as kmz (Google Earth)
---------------------

as image (PNG)
--------------

as shapefile
------------
The `Export as shapefile` option can be enabled by adding a urlpattern named ``mpa_shapefile``.

.. code-block:: python

    urlpatterns = patterns('',
        url(r'shapefile/mpa/(?P<mpa_id_list_str>(\d+,?)+)/$', mpa_shapefile, name='mpa_shapefile'),
    )

This urlpattern refers to a view, which we have called ``mpa_shapefile``.  This view will utilize the built-in ``ShpResponder`` 
class to generate a shapefile from the ``export_query_set`` property of your model (we are using ``MPA`` as 
the model in this example).  

.. code-block:: python

    from lingcod.common import utils
    from lingcod.sharing.utils import get_viewable_object_or_respond
    from lingcod.shapes.views import ShpResponder
    from django.template.defaultfilters import slugify

    def mpa_shapefile(request, mpa_id_list_str):
        mpa_class = utils.get_mpa_class()
        mpa_id_list = mpa_id_list_str.split(',')
        mpa_id = mpa_id_list[0] # only expecting one 
        mpa = get_viewable_object_or_respond(mpa_class, mpa_id, request.user)
        shp_response = ShpResponder(mpa.export_query_set)
        shp_response.file_name = slugify(mpa.name[0:8])
        return shp_response()

In order for this view to function, your model (``MPA`` in this case) needs to have an ``export_query_set`` property defined.

.. code-block:: python

    @property
    def export_query_set(self):
        return MpaShapefile.objects.filter(pk=self.export_version.pk)
    
This ``export_query_set`` property requires an additional model (which we will call ``MpaShapefile``),
and an additional property in your original model, ``export_version``, which will be responsible for
generating an instance of this new model ``MpaShapefile``.
This additional model, ``MpaShapefile``, will provide the fields you wish to have present in the attribute table of 
the exported shapefile.  

.. code-block:: python

    class MpaShapefile(models.Model):
        """
        This model will provide the correct fields for the export of shapefiles.
        """
        name = models.CharField(max_length=255)
        mpa_id_num = models.IntegerField(blank=True, null=True)
        geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,blank=True,null=True)
        mpa = models.OneToOneField(MPA, related_name="mpa")
        mpa_modification_date = models.DateTimeField(blank=True, null=True)
        date_modified = models.DateTimeField(blank=True, null=True, auto_now_add=True)
        objects = models.GeoManager()

And the ``export_version`` property of your original model (``MPA`` in our case), will generate an entry in 
the ``MpaShapefile`` table if one is not already present (and current).  

.. code-block:: python

    @property
    def export_version(self):
        """
        Port the MPAs attributes over to the MpaShapefile model so we can export the shapefile.
        """
        msf, created = MpaShapefile.objects.get_or_create(mpa=self)
        if created or msf.date_modified < self.date_modified:
            msf.name = self.name
            msf.mpa_id_num = self.pk
            msf.geometry = self.geometry_final
            msf.mpa_modification_date = self.date_modified
            msf.save()
        return msf

Implementing all of the above should provide a working `Export as shapefile` feature for your individual model.

Once you have this in place for an individual model, implementing the `Export as shapefile` feature for an array,
or group of models is simple:

Add an additional urlpattern:

.. code-block:: python

    url(r'shapefile/array/(?P<array_id_list_str>(\d+,?)+)/$', array_shapefile,name='array_shapefile')
    
An additional view:    
    
.. code-block:: python

    def array_shapefile(request, array_id_list_str):
        array_class = utils.get_array_class()
        array_id_list = array_id_list_str.split(',')
        array_id = array_id_list[0] # for now we're only expecting to get one
        array = get_viewable_object_or_respond(array_class,array_id,request.user)
        file_name = array.name[0:8]
        shp_response = ShpResponder(array.export_query_set)
        shp_response.file_name = slugify(file_name)
        return shp_response()

And an ``export_query_set`` property to your Array model (``MpaArray`` in our case):

.. code-block:: python

    @property
    def export_query_set(self):
        for mpa in self.mpa_set.all():
            mpa.export_version # update these records
        qs = MpaShapefile.objects.filter(group=self)
        return qs

This property will simply loop through the individual shapes in your array, utilizing the ``export_version property`` 
of your base model (``MPA``), to generate a shapefile with all of the shapes contained within that array.
