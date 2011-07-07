.. _export:

Export Options
==============
In order to provide the user the opportunity to make use of their shapes outside of the MarineMap environment, 
MarineMap provides an `Export` option which allows the user to export individual 
shapes and arrays of shapes in a variety of formats.

Exporting as kmz and exporting as image are both built in to Lingcod and will 
appear by default in the `Export` drop-down menu.  

Exporting as shapefile requires the enabling of a urlpattern as explained below.

Atom links for each of these Export options can be found in ``lingcod/kmlapp/templates/placemarks.kml``.

as kmz (Google Earth)
---------------------

as image (PNG)
--------------

as shapefile
------------
The `Export as shapefile` option can be enabled by adding a view, a model, and a couple tweaks
to the exportable model.  

The following example will walk you through the steps of enabling the export as shapefile option using
a sample model ``MyBioregion``.

The following view (``bio_shapefile`` in this example) will utilize the built-in ``ShpResponder`` class 
to generate a shapefile from our exportable model (``MyBioregion``).  

.. note::
    This view is actually equipped to handle multiple instances of MyBioregion that may have been selected by the user
    for exporting.  

.. code-block:: python

    from lingcod.common import utils
    from lingcod.sharing.utils import get_viewable_object_or_respond
    from lingcod.shapes.views import ShpResponder
    from django.template.defaultfilters import slugify
    
    def bio_shapefile(request, instances):
        from mybioregions.models import MyBioregion, BioregionShapefile
        bios = []
        for inst in instances:
            viewable, response = inst.is_viewable(request.user)
            if not viewable:
                return response

            if isinstance(inst, MyBioregion):
                inst.convert_to_shp()
                bios.append(inst)
            else:
                pass # ignore anything else

        filename = '_'.join([slugify(inst.name) for inst in instances])
        pks = [bio.pk for bio in bios]
        qs = BioregionShapefile.objects.filter(bio_id_num__in=pks)
        if len(qs) == 0:
            return HttpResponse(
                "Nothing in the query set; you don't want an empty shapefile", 
                status=404
            )
        shp_response = ShpResponder(qs)
        shp_response.file_name = slugify(filename[0:8])
        return shp_response()

In order for this view to function, the exportable model (``MyBioregion``) will need a ``convert_to_shp`` function.

.. code-block:: python

    def convert_to_shp(self):
        '''
        Port the Bioregion attributes over to the BioregionShapefile model so we can export the shapefile.
        '''
        bsf, created = BioregionShapefile.objects.get_or_create(bioregion=self)
        if created or bsf.date_modified < self.date_modified:
            bsf.name = self.name
            bsf.bio_id_num = self.pk
            bsf.geometry = self.output_geom
            #short_name = self.name
            if self.collection:
                bsf.group = self.collection
                bsf.group_name = self.collection.name
            #units based on the settings variable DISPLAY_AREA_UNITS (currently sq miles)
            bsf.area_sq_mi = area_in_display_units(self.output_geom)
            bsf.author = self.user.username
            bsf.aoi_modification_date = self.date_modified
            bsf.save()
        return bsf
    
And the following ``link`` entry should be added to the model's (``MyBioregion``) ``Options`` class. 

.. code-block:: python
    
    links = (
        alternate('Shapefile',
            'mybioregions.views.bio_shapefile',
            select='multiple single',
            type='application/zip',
        ),
    )
    
    
This ``convert_to_shp`` function requires an additional model (``BioregionShapefile`` in our example).
This additional model will provide the fields you wish to have present in the attribute table of 
the exported shapefile.  

.. code-block:: python

    class BioregionShapefile(models.Model):
        """
        This model will provide the correct fields for the export of shapefiles using the django-shapes app.
        """
        geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,blank=True,null=True)
        name = models.CharField(max_length=255)
        bio_id_num = models.IntegerField(blank=True, null=True)
        group = models.ForeignKey(Folder, null=True, blank=True)
        group_name = models.CharField(blank=True, max_length=255, null=True)
        area_sq_mi = models.FloatField(blank=True,null=True)
        author = models.CharField(blank=True, max_length=255,null=True)
        bioregion = models.OneToOneField(MyBioregion, related_name="bioregion")
        bio_modification_date = models.DateTimeField(blank=True, null=True)
        date_modified = models.DateTimeField(blank=True, null=True, auto_now_add=True)
        objects = models.GeoManager()   

Implementing all of the above should provide a working `Export as shapefile` feature for your individual model.

Once you have this in place for an individual model, implementing the `Export as shapefile` feature for an array,
or group of models is simple:

Augment your view to reflect the minor changes seen below (including the possibility of a ``Folder`` instance):    
    
.. code-block:: python

    def bio_shapefile(request, instances):
        from mybioregions.models import MyBioregion, Folder, BioregionShapefile
        bios = []
        for inst in instances:
            viewable, response = inst.is_viewable(request.user)
            if not viewable:
                return response

            if isinstance(inst, MyBioregion):
                inst.convert_to_shp()
                bios.append(inst)
            elif isinstance(inst, Folder):
                for bio in inst.feature_set(recurse=True,feature_classes=[MyBioregion]):
                    bio.convert_to_shp()
                    bios.append(bio)
            else:
                pass # ignore anything else

        filename = '_'.join([slugify(inst.name) for inst in instances])
        pks = [bio.pk for bio in bios]
        qs = BioregionShapefile.objects.filter(bio_id_num__in=pks)
        if len(qs) == 0:
            return HttpResponse(
                "Nothing in the query set; you don't want an empty shapefile", 
                status=404
            )
        shp_response = ShpResponder(qs)
        shp_response.file_name = slugify(filename[0:8])
        return shp_response()

This change will simply loop through the individual shapes in any ``Folder`` instance, generating 
a shapefile record from each of the shapes contained within that array.

And finally, add the following ``link`` entry to the ``Options`` class in your array model (``Folder`` in this example):

.. code-block:: python

    links = (
        alternate('Shapefile',
            'mybioregions.views.bio_shapefile',
            select='multiple single',
            type='application/zip',
        ),
    )

And you should now have the ability to export shapes and folders of shapes as shapefiles.
