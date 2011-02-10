from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.http import HttpResponse
from lingcod.features.managers import ShareableGeoManager
from lingcod.features.forms import FeatureForm
from lingcod.features import get_model_options
from lingcod.common.utils import asKml, clean_geometry, ensure_clean
from lingcod.common.utils import get_logger, get_class, enable_sharing
from lingcod.manipulators.manipulators import manipulatorsDict, NullManipulator
import re

logger = get_logger()

class Feature(models.Model):
    """Model used for representing user-generated features

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Creator

        ``name``                Name of the object
                                
        ``date_created``        When it was created

        ``date_modified``       When it was last updated.
                                        
        ======================  ==============================================
    """   
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related")
    name = models.CharField(verbose_name="Name", max_length="255")
    date_created = models.DateTimeField(auto_now_add=True, 
            verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, 
            verbose_name="Date Modified")
    sharing_groups = models.ManyToManyField(Group,editable=False,blank=True,
            null=True,verbose_name="Share with the following groups", 
            related_name="%(app_label)s_%(class)s_related")
    content_type = models.ForeignKey(ContentType, blank=True, null=True, 
            related_name="%(app_label)s_%(class)s_related")
    object_id = models.PositiveIntegerField(blank=True,null=True)
    collection = generic.GenericForeignKey('content_type', 'object_id')

    objects = ShareableGeoManager()

    def __unicode__(self):
        return u"%s_%s" % (self.model_uid(), self.pk)

    def __repr__(self):
        return u"%s_%s" % (self.model_uid(), self.pk)

    class Meta:
        abstract=True

    @models.permalink
    def get_absolute_url(self):
        return ('%s_resource' % (self.get_options().slug, ), (), {
            'pk': self.pk
        })
    
    @classmethod
    def get_options(klass):
        return get_model_options(klass.__name__)
    
    @classmethod
    def model_uid(klass):
        ct = ContentType.objects.get_for_model(klass)
        return "%s_%s" % (ct.app_label, ct.model)
        
    @property
    def uid(self):
        if not self.pk:
            raise Exception(
                'Trying to get uid for feature class that is not yet saved!')
        return "%s_%s" % (self.model_uid(), self.pk, )
    
    def add_to_collection(self, collection):
        assert issubclass(collection.__class__, FeatureCollection)
        assert self.__class__ in collection.get_options().get_valid_children()
        assert self.user == collection.user
        self.collection = collection
        self.save()

    def remove_from_collection(self):
        collection = self.collection
        self.collection = None
        self.save()
        if collection:
            collection.save()

    def share_with(self, groups, append=False):
        """
        Share this feature with the specified group/groups.
        Owner must be a member of the group/groups.
        Group must have 'can_share' permissions else an Exception is raised
        """
        if not append:
            # Don't append to existing groups; Wipe the slate clean
            # Note that this is the default behavior
            self.sharing_groups.clear()

        if groups is None or groups == []:
            # Nothing to do here
            return True
            
        if isinstance(groups,Group):
             # Only a single group was provided, make a 1-item list
             groups = [groups]

        for group in groups:
            assert isinstance(group, Group)
            # Check that the group to be shared with has appropos permissions
            assert group in self.user.groups.all()
            try:
                gp = group.permissions.get(codename='can_share_features')
            except:
                raise Exception("The group you are trying to share with "  
                        "does not have can_share permission")

            self.sharing_groups.add(group)

        self.save()
        return True

    def is_viewable(self, user):
        """ 
        Is this feauture viewable by the specified user? 
        Either needs to own it or have it shared with them.
        returns : Viewable(boolean), HttpResponse
        """
        # First, is the user logged in?
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Does the user own it?
        if self.user == user:
            return True, HttpResponse("Object owned by user",status=202)
        
        # Next see if its shared with the user
        try: 
            # Instead having the sharing logic here, use the shared_with_user
            # We need it to return querysets so no sense repeating that logic
            obj = self.__class__.objects.shared_with_user(user).get(pk=self.pk)
            return True, HttpResponse("Object shared with user", status=202)
        except self.__class__.DoesNotExist:
            return False, HttpResponse("Access denied", status=403)

        return False, HttpResponse("Server Error in feature.is_viewable()", status=500) 

    def copy(self, user=None):
        """
        Returns a copy of this feature, setting the user to the specified 
        owner. Copies many-to-many relations
        """
        # Took this code almost verbatim from the mpa model code.
        # TODO: Test if this method is robust, and evaluate alternatives like
        # that described in django ticket 4027
        # http://code.djangoproject.com/ticket/4027
        the_feature = self

        # Make an inventory of all many-to-many fields in the original feature
        m2m = {}
        for f in the_feature._meta.many_to_many:
            m2m[f.name] = the_feature.__getattribute__(f.name).all()

        # The black magic voodoo way, 
        # makes a copy but relies on this strange implementation detail of 
        # setting the pk & id to null 
        # An alternate, more explicit way, can be seen at:
        # http://blog.elsdoerfer.name/2008/09/09/making-a-copy-of-a-model-instance
        the_feature.pk = None
        the_feature.id = None
        the_feature.save()

        the_feature.name = the_feature.name + " (copy)"

        # Restore the many-to-many fields
        for fname in m2m.keys():
            for obj in m2m[fname]:
                the_feature.__getattribute__(fname).add(obj)
    
        # Reassign User
        the_feature.user = user
        
        # Clear everything else 
        the_feature.sharing_groups.clear()
        the_feature.remove_from_collection()

        the_feature.save()
        return the_feature

class SpatialFeature(Feature):
    """
    Abstract Model used for representing user-generated geometry features. 
    Inherits from Feature and adds geometry-related methods/properties
    common to all geometry types.
    """   
    manipulators = models.TextField(verbose_name="Manipulator List", null=True,
            blank=True, help_text='csv list of manipulators to be applied')

    class Meta(Feature.Meta):
        abstract=True

    def save(self, *args, **kwargs):
        self.apply_manipulators()
        if self.geometry_final:
            self.geometry_final = clean_geometry(self.geometry_final)
        super(SpatialFeature, self).save(*args, **kwargs) # Call the "real" save() method
    
    @property
    def geom_kml(self):
        return asKml(self.geometry_final.transform(settings.GEOMETRY_CLIENT_SRID, clone=True))
    
    @property
    def kml(self):
        """
        The Feature's kml property MUST 
          - return a string containing a valid KML placemark element
          - the placemark must have id= [the feature's uid]
          - if it references any style URLs, the corresponding Style element(s)
            must be provided by the feature's .kml_style property
        """
        return """
        <Placemark id="%s">
            <name>%s</name>
            <styleUrl>#%s-default</styleUrl>
            <ExtendedData>
                <Data name="name"><value>%s</value></Data>
                <Data name="user"><value>%s</value></Data>
                <Data name="modified"><value>%s</value></Data>
            </ExtendedData>
            %s 
        </Placemark>
        """ % (self.uid, self.name, self.model_uid(), 
               self.name, self.user, self.date_modified, 
               self.geom_kml)

    @property
    def kml_style(self):
        """
        Must return a string with one or more KML Style elements
        whose id's may be referenced by relative URL
        from within the feature's .kml string
        In any given KML document, each *unique* kml_style string will get included 
        so don't worry if you have 10 million features with "blah-default" style...
        only one will appear in the final document and all the placemarks can refer
        to it.
        """
        return """
        <Style id="%s-default">
            <IconStyle>
                <color>ffffffff</color>
                <colorMode>normal</colorMode>
                <scale>0.9</scale> 
                <Icon> <href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href> </Icon>
            </IconStyle>
            <BalloonStyle>
                <bgColor>ffeeeeee</bgColor>
                <text> <![CDATA[
                    <font color="#1A3752"><strong>$[name]</strong></font><br />
                    <font size=1>Created by $[user] on $[modified]</font>
                ]]> </text>
            </BalloonStyle>
            <LabelStyle>
                <color>ffffffff</color>
                <scale>0.8</scale>
            </LabelStyle>
            <PolyStyle>
                <color>778B1A55</color>
            </PolyStyle>
            <LineStyle>
                <color>ffffffff</color>
            </LineStyle>
        </Style>
        """ % (self.model_uid(),)

    @property
    def active_manipulators(self):
        """
        This method contains all the logic to determine which manipulators get applied to a feature

        If self.manipulators doesnt exist or is null or blank, 
           apply the required manipulators (or the NullManipulator if none are required)

        If there is a self.manipulators string and there are optional manipulators contained in it,
           apply the required manipulators PLUS the specified optional manipulators
        """
        active = []
        try:
            manipulator_list = self.manipulators.split(',')
            if len(manipulator_list) == 1 and manipulator_list[0] == '':
                # list is blank
                manipulator_list = []
        except AttributeError:
            manipulator_list = [] 

        required = [get_class(m) for m in self.__class__.Options.manipulators]
        try:
            optional = [get_class(m) for m in self.__class__.Options.optional_manipulators]
        except AttributeError:
            optional = []

        # Always include the required manipulators in the active list
        active.extend(required)

        if len(manipulator_list) < 1:
            if not required or len(required) < 1:
                manipulator_list = ['NullManipulator']
            else:
                return active 

        # include all valid manipulators from the self.manipulators list
        for manipulator in manipulator_list:
            manipClass = manipulatorsDict.get(manipulator)
            if manipClass and (manipClass in optional or manipClass == NullManipulator):
                active.append(manipClass)

        return active

    def apply_manipulators(self, force=False):
        if force or (self.geometry_orig and not self.geometry_final):
            logger.debug("applying manipulators to %r" % self)
            target_shape = self.geometry_orig.transform(settings.GEOMETRY_CLIENT_SRID, clone=True).wkt
            logger.debug("active manipulators: %r" % self.active_manipulators)
            result = False
            for manipulator in self.active_manipulators:
                m = manipulator(target_shape)
                result = m.manipulate()
                target_shape = result['clipped_shape'].wkt
            if not result:
                raise Exception("No result returned - maybe manipulators did not run?")
            geo = result['clipped_shape']
            geo.transform(settings.GEOMETRY_DB_SRID)
            ensure_clean(geo, settings.GEOMETRY_DB_SRID)
            if geo:
                self.geometry_final = geo
            else:
                raise Exception('Could not pre-process geometry')

class PolygonFeature(SpatialFeature):
    """
    Model used for representing user-generated polygon features. 
    """   
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Original Polygon Geometry")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final Polygon Geometry")
    
    @property
    def centroid_kml(self):
        geom = self.geometry_final.point_on_surface.transform(settings.GEOMETRY_CLIENT_SRID, clone=True)
        return geom.kml
 
    #TODO make default geom_kml a multi? 

    class Meta(Feature.Meta):
        abstract=True

class LineFeature(SpatialFeature):
    """
    Model used for representing user-generated linestring features. 
    """   
    geometry_orig = models.LineStringField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Original LineString Geometry")
    geometry_final = models.LineStringField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final LineString Geometry")

    class Meta(Feature.Meta):
        abstract=True

class PointFeature(SpatialFeature):
    """
    Model used for representing user-generated point features. 
    """   
    geometry_orig = models.PointField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Original Point Geometry")
    geometry_final = models.PointField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final Point Geometry")
    
    class Meta(Feature.Meta):
        abstract=True

class FeatureCollection(Feature):
    """
    A Folder/Collection of Features
    """
    class Meta:
        abstract = True
    
    def add(self, f):
        """Adds a specified Feature to the Collection"""
        f.add_to_collection(self)
    
    def remove(self, f):
        """Removes a specified Feature from the Collection"""
        if f.collection == self:
            f.remove_from_collection()
            self.save() # This updates the date_modified field of the collection
        else:
            raise Exception('Feature `%s` is not in Collection `%s`' % (f.name, self.name))

    @property
    def kml(self):
        features = self.feature_set()
        kmls = [x.kml for x in features]
        return """
        <Folder id="%s">
          <name>%s</name>
          <visibility>1</visibility>
          <open>0</open>
          %s
        </Folder>
        """ %  (self.uid, self.name, ''.join(kmls))

    @property
    def kml_style(self):
        return ""

    def feature_set(self, recurse=False, feature_classes=None):
        """
        Returns a list of Features belonging to the Collection
        Optionally recurse into all child containers
        or limit/filter for a list of feature classes
        """
        feature_set = []

        # If a single Feature is provided, make it into 1-item list
        if issubclass(feature_classes.__class__, Feature):
            feature_classes = [feature_classes]

        for model_class in self.get_options().get_valid_children():
            if recurse and issubclass(model_class, FeatureCollection):
                collections = model_class.objects.filter(
                    content_type=ContentType.objects.get_for_model(self),
                    object_id=self.pk
                )
                for collection in collections:
                    feature_list = collection.feature_set(recurse, feature_classes)
                    if len(feature_list) > 0:
                        feature_set.extend(feature_list)

            if feature_classes and model_class not in feature_classes:
                continue

            feature_list = list( 
                model_class.objects.filter(
                    content_type=ContentType.objects.get_for_model(self),
                    object_id=self.pk
                )
            )

            if len(feature_list) > 0:
                feature_set.extend(feature_list)

        return feature_set

    def copy(self, user=None):
        """
        Returns a copy of this feature collection, setting the user to the specified 
        owner. Recursively copies all children.
        """
        original_feature_set = self.feature_set(recurse=False)

        the_collection = self

        # Make an inventory of all many-to-many fields in the original feature
        m2m = {}
        for f in the_collection._meta.many_to_many:
            m2m[f.name] = the_collection.__getattribute__(f.name).all()

        # makes a copy but relies on this strange implementation detail of 
        # setting the pk & id to null 
        the_collection.pk = None
        the_collection.id = None
        the_collection.save()

        the_collection.name = the_collection.name + " (copy)"

        # Restore the many-to-many fields
        for fname in m2m.keys():
            for obj in m2m[fname]:
                the_collection.__getattribute__(fname).add(obj)
    
        # Reassign User
        the_collection.user = user
        
        # Clear everything else 
        the_collection.sharing_groups.clear()
        the_collection.remove_from_collection()
        the_collection.save()

        for child in original_feature_set:
            new_child = child.copy(user)
            new_child.add_to_collection(the_collection)

        the_collection.save()
        return the_collection
