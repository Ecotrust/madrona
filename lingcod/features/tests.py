from django.test import TestCase
from lingcod.features import *
from lingcod.features.models import Feature, PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.features.forms import FeatureForm
from lingcod.common.utils import kml_errors, enable_sharing
import os
import shutil
from django.test.client import Client
from django.contrib.auth.models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.gis.geos import GEOSGeometry 
from django.conf import settings


# used by some of the tests to temporarily create a template file
def create_template(path):
    d = os.path.dirname(__file__)
    dpath = os.path.dirname(os.path.join(d, 'templates', path))
    os.mkdir(dpath)
    path = os.path.join(dpath, 'show.html')
    f = open(path, 'w')
    f.write('h1 />')
    f.close()

def delete_template(path):
    d = os.path.dirname(__file__)
    dpath = os.path.join(d, 'templates')
    path = os.path.join(dpath, path)
    path = os.path.dirname(path)
    if os.path.exists(path):
        shutil.rmtree(path)

@register        
class TestGetFormClassFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.TestFeatureForm'

class TestFeatureForm(FeatureForm):
    class Meta:
        model = TestGetFormClassFeature

@register
class TestGetFormClassFailFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.TestForm'

class TestForm:
    class Meta:
        model = TestGetFormClassFeature

@register
class TestSlugFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
                
@register
class TestDefaultVerboseNameFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
@register 
class TestCustomVerboseNameFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        verbose_name = 'vb-name'
        
@register
class TestDefaultShowTemplateFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
@register
class TestCustomShowTemplateFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        show_template = 'location/show.html'
        
@register
class TestMissingDefaultShowFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
@register
class TestMissingCustomShowFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        show_template = 'location/show.html'

class FeatureOptionsTest(TestCase):
    
    def test_check_for_subclass(self):
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            @register
            class NotAFeature:
                pass
            NotAFeature.get_options()
    
    def test_check_for_inner_class(self):
        with self.assertRaisesRegexp(FeatureConfigurationError,'not defined'):
            @register
            class TestFeatureFails(Feature):
                pass
            TestFeatureFails.get_options()

    def test_must_have_form_class(self):
        with self.assertRaisesRegexp(FeatureConfigurationError,'form'):
            @register
            class TestFeatureNoForm(Feature):
                class Options:
                    pass
            TestFeatureNoForm.get_options()

    def test_must_specify_form_as_string(self):
        with self.assertRaisesRegexp(FeatureConfigurationError,'string'):
            @register
            class TestFeature(Feature):
                class Options:
                    form = FeatureForm
            TestFeature.get_options()

    def test_slug(self):
        self.assertEqual(TestSlugFeature.get_options().slug, 'testslugfeature')
    
    def test_default_verbose_name(self):
        self.assertEqual(
            TestDefaultVerboseNameFeature.get_options().verbose_name, 
            'TestDefaultVerboseNameFeature')
    
    def test_custom_verbose_name(self):
        self.assertEqual(
            TestCustomVerboseNameFeature.get_options().verbose_name, 
            'vb-name')
        
    def test_default_show_template(self):
        options = TestDefaultShowTemplateFeature.get_options()
        path = options.slug + '/show.html'
        delete_template(path)
        create_template(path)
        self.assertEqual(
            options.get_show_template().name, 
            path)
        delete_template(path)
    
    def test_custom_show_template(self):
        options = TestCustomShowTemplateFeature.get_options()
        path = TestCustomShowTemplateFeature.Options.show_template
        delete_template(path)
        create_template(path)
        self.assertEqual(
            options.get_show_template().name, 
            path)
        delete_template(path)
    
    def test_missing_default_show_template(self):
        options = TestMissingDefaultShowFeature.get_options()
        path = options.slug + '/show.html'
        self.assertEqual(
            options.get_show_template().name, 
            'features/show.html')

    def test_missing_custom_show_template(self):

        options = TestMissingCustomShowFeature.get_options()
        self.assertEqual(
            options.get_show_template().name, 
            'features/show.html')
    
    def test_get_form_class(self):
        self.assertEqual(
            TestGetFormClassFeature.get_options().get_form_class(),
            TestFeatureForm)
    
    def test_get_form_not_subclass(self):
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            TestGetFormClassFailFeature.get_options().get_form_class()
    
# Generic view tests

@register
class TestDeleteFeature(Feature):
    class Options:
        form = 'lingcod.features.form.FeatureForm'
        
class DeleteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.options = TestDeleteFeature.get_options()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.test_instance = TestDeleteFeature(user=self.user, name="My Name")
        self.test_instance.save()

    def test_delete_not_logged_in(self):
        """
        If user not logged in they can't delete anything
        401 status_code response
        """
        url = self.test_instance.get_absolute_url()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_not_owner(self):
        """
        Don't allow just any old user to delete objects.
        Return 403 Forbidden status code
        """
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.client.login(username=other_user.username, password='pword')
        url = self.test_instance.get_absolute_url()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_not_owner_but_staff(self):
        """
        Staff users can delete anyone's stuff
        """
        staff_user = User.objects.create_user(
            'staff', 'staff@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        pk = self.test_instance.pk
        url = self.test_instance.get_absolute_url()
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 1)
        self.client.login(username='staff', password='pword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 0)

    def test_delete_authorized(self):
        """
        Users can delete objects that belong to them
        """
        pk = self.test_instance.pk
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 1)
        url = self.test_instance.get_absolute_url()
        self.client.login(username='featuretest', password='pword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestDeleteFeature.objects.filter(pk=pk).count(), 0)
        

@register
class CreateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateFormTestForm'

class CreateFormTestForm(FeatureForm):
    class Meta:
        model = CreateFormTestFeature

class CreateFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.options = CreateFormTestFeature.get_options()

    def test_user_not_logged_in(self):
        """
        Can't create stuff without being logged in.
        """
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 401)

    def test_get_form(self):
        """
        Returns a form that can be displayed on the client.
        """
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 200)

@register
class CreateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.CreateTestForm'

class CreateTestForm(FeatureForm):
    class Meta:
        model = CreateTestFeature


class CreateTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.options = CreateTestFeature.get_options()
        self.create_url = self.options.get_create_form()

    def test_submit_not_authenticated(self):
        response = self.client.post(self.create_url, 
            {'name': "My Test", 'user': 1})
        self.assertEqual(response.status_code, 401)

    def test_submit_invalid_form(self):
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.create_url, {'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(old_count == CreateTestFeature.objects.count())
        self.assertNotEqual(
            response.content.find('This field is required.'), -1)

    def test_submit_valid_form(self):
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.create_url, {'name': "My Test"})
        self.assertEqual(response.status_code, 201,response.content)
        self.assertTrue(old_count < CreateTestFeature.objects.count())
        inst = CreateTestFeature.objects.get(name='My Test')
        self.assertTrue(
            response['Location'].count(inst.get_absolute_url()) == 1)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        old_count = CreateTestFeature.objects.count()
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.create_url, 
            {'name': "My Test Hack Test", 'user': other_user.pk})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < CreateTestFeature.objects.count())
        new_instance = CreateTestFeature.objects.get(name='My Test Hack Test')
        self.assertNotEqual(new_instance.user, other_user)

@register
class UpdateFormTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateFormTestForm'

class UpdateFormTestForm(FeatureForm):
    class Meta:
        model = UpdateFormTestFeature

class UpdateFormTest(TestCase):

    def setUp(self):
        self.options = UpdateFormTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.test_instance = UpdateFormTestFeature(
            user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)

    def test_get_form(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content.find('My Name'), -1)

    def test_not_logged_in(self):
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 401)

    def test_not_owner(self):
        other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 403)

    def test_not_owner_but_staff(self):
        staff_user = User.objects.create_user(
            'staff', 'other@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        self.client.login(username='staff', password='pword')
        response = self.client.get(self.update_form_url)
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(self.options.get_update_form(30000000000))
        self.assertEqual(response.status_code, 404)

@register
class UpdateTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.UpdateTestForm'

class UpdateTestForm(FeatureForm):
    class Meta:
        model = UpdateTestFeature

class UpdateTest(TestCase):

    def setUp(self):
        self.options = UpdateTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.test_instance = UpdateTestFeature(user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)
        self.instance_url = self.test_instance.get_absolute_url()

    def test_post(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_post_validation_error(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': '',
        })
        self.assertEqual(response.status_code, 400)

    def test_post_not_logged_in(self):
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 401)

    def test_post_not_owner(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 403)

    def test_post_not_owner_but_staff(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        other_user.is_staff = True
        other_user.save()
        self.client.login(username='other', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.options.get_resource(10000000), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 404)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='featuretest', password='pword')
        response = self.client.post(self.instance_url, {
            'name': 'My New Name',
            'user': other_user.pk,
        })
        self.assertEqual(response.status_code, 200)
        edited_instance = UpdateTestFeature.objects.get(pk=self.test_instance.pk)
        self.assertNotEqual(edited_instance.user, other_user)

def valid_single_select_view(request, instance):
    return HttpResponse(instance.name)

def invalid_single_select_view(request, pk):
    pass

def invalid_multiple_select_view(request, fail):
    pass

def valid_multiple_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))

class LinkViewValidationTest(TestCase):
    
    def test_single_select_view_requires_instance_argument(self):
        # Must accept at least a second argument for the instance
        with self.assertRaises(FeatureConfigurationError):
            link = alternate(
                'test title',
                'lingcod.features.tests.invalid_single_select_view')
                
        # Accepts the instance argument
        link = alternate('test title',
            'lingcod.features.tests.valid_single_select_view')
        self.assertIsInstance(link, Link)
    
    def test_multiple_select_view_requires_instance_argument(self):
        # Must accept at least a second argument for the instances
        with self.assertRaises(FeatureConfigurationError):
            link = alternate('test title',
                'lingcod.features.tests.invalid_multiple_select_view', 
                select='multiple')

        # Accepts the instance argument
        link = alternate('test title',
            'lingcod.features.tests.valid_multiple_select_view', 
            select='multiple')
        self.assertIsInstance(link, Link)
        
    def test_check_extra_kwargs_allowed(self):
        pass
        # TODO: Test that Link validates extra_kwargs option is compatible 
        # with the view

@register
class LinkTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.LinkTestFeatureForm'
        links = (
            alternate('Single Select View',
                'lingcod.features.tests.valid_single_select_view',  
                type="application/shapefile"),
                
            alternate('Spreadsheet of all Features',
                'lingcod.features.tests.valid_multiple_select_view',
                type="application/xls", 
                select='multiple single'),
            
            edit('Edit single feature',
                'lingcod.features.tests.valid_single_select_view'
            ),
            
            edit_form('Edit multiple features',
                'lingcod.features.tests.valid_multiple_select_view',
                select='multiple single'
            ),
        )

class LinkTestFeatureForm(FeatureForm):
    class Meta:
        model = LinkTestFeature


class LinkTest(TestCase):
    
    def setUp(self):
        self.options = LinkTestFeature.get_options()
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.other_user = User.objects.create_user(
            'other', 'other@marinemap.org', password='pword')
        self.test_instance = LinkTestFeature(user=self.user, name="My Name")
        self.test_instance.save()
        self.update_form_url = self.options.get_update_form(
            self.test_instance.pk)
        self.instance_url = self.test_instance.get_absolute_url()
        self.i2 = LinkTestFeature(user=self.user, name="I2")
        self.i2.save()
        
    
    def test_get_links(self):
        links = LinkTestFeature.get_options().links
        link = links[2]
        link2 = links[3]
        self.assertIsInstance(link, Link)
        self.assertEqual('Single Select View', link.title)
        self.assertEqual('single', link.select)
        self.assertEqual('multiple single', link2.select)
    
    def test_links_registered(self):
        options = LinkTestFeature.get_options()
        links = options.links
        link = links[2]
        link2 = links[3]
        # Check to see that the Feature Class was registered at all
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(self.options.get_create_form())
        self.assertEqual(response.status_code, 200)
        # Check that both links have urls
        path = link.reverse(self.test_instance)
        response = self.client.get(path)
        self.assertRegexpMatches(response.content, r'My Name')
        path = link2.reverse([self.test_instance, self.i2])
        response = self.client.get(path)
        self.assertRegexpMatches(response.content, r'My Name, I2')
        
    def test_401_response(self):
        """Should not be able to perform editing actions without login.
        """
        links = self.options.links
        response = self.client.post(links[4].reverse(self.test_instance))
        self.assertEqual(response.status_code, 401,response.content)
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 401)
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 200)        
    
    def test_cant_GET_edit_links(self):
        """For links of rel=edit, a post request should be required.
        """
        links = self.options.links
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(links[4].reverse(self.test_instance))
        self.assertEqual(response.status_code, 405,response.content)
        self.assertEqual(response['Allow'], 'POST')
        
    def test_403_response(self):
        """Should not be able to edit shapes a user doesn't own.
        """
        links = self.options.links
        self.client.login(username='other', password='pword')
        response = self.client.get(links[5].reverse(self.test_instance))
        self.assertEqual(response.status_code, 403)        
        
    
    def test_403_response_multiple_instances(self):
        """Should not be able to edit shapes a user doesn't own. Test to make
        sure every feature in a request is checked.
        """
        links = self.options.links
        self.client.login(username='other', password='pword')
        inst = LinkTestFeature(user=self.other_user, 
            name="Other User's feature")
        inst.save()
        response = self.client.get(
            links[5].reverse([inst, self.test_instance]))
        self.assertEqual(response.status_code, 403, response.content)
        
    def test_404_response(self):
        links = self.options.links
        self.client.login(username='featuretest', password='pword')
        inst = LinkTestFeature(user=self.user, 
            name="feature")
        inst.save()
        path = links[5].reverse([inst, self.test_instance])
        inst.delete()
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

def multi_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))

@register
class GenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.GenericLinksTestForm'
        links = (
            alternate('Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
            alternate('Non-Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
        )

class GenericLinksTestForm(FeatureForm):
    class Meta:
        model = GenericLinksTestFeature


@register
class OtherGenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.OtherGenericLinksTestForm'
        links = (
            alternate('Generic Link',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),
        )


class OtherGenericLinksTestForm(FeatureForm):
    class Meta:
        model = OtherGenericLinksTestFeature

@register
class LastGenericLinksTestFeature(Feature):
    class Options:
        form = 'lingcod.features.tests.GenericLinksTestForm'
        links = (
            alternate('Different Name',
                'lingcod.features.tests.multi_select_view',  
                type="application/shapefile",
                select='multiple single'),

        )

class GenericLinksTest(TestCase):
    
    # Note that links[2] will be the first generic link in the list
    # ... the first two links are KML and Copy which are automatically created
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.generic_instance = GenericLinksTestFeature(user=self.user, 
            name="Generic")
        self.other_instance = OtherGenericLinksTestFeature(user=self.user, 
            name="Other")
        self.last_instance = LastGenericLinksTestFeature(user=self.user, 
            name="Last")
        self.generic_instance.save()
        self.other_instance.save()
        self.last_instance.save()
    
    def test_generic_links_reused_by_create_link(self):
        """Test that the calls to lingcod.features.create_link return 
        references to generic links when appropriate."""
        self.assertEqual(GenericLinksTestFeature.get_options().links[2], 
            OtherGenericLinksTestFeature.get_options().links[2])
        self.assertNotEqual(
            OtherGenericLinksTestFeature.get_options().links[2],
            LastGenericLinksTestFeature.get_options().links[2])
            
    def test_generic_links_work(self):
        """Test that a generic view can recieve a request related to more than
        one feature class."""
        link = GenericLinksTestFeature.get_options().links[2]
        path = link.reverse([self.generic_instance, self.other_instance])
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'Generic')
        self.assertRegexpMatches(response.content, r'Other')
        
    def test_generic_links_deny_unconfigured_models(self):
        """Generic links shouldn't work for any model, only those that have 
        the link configured in their Options class."""
        link = GenericLinksTestFeature.get_options().links[2]
        path = link.reverse([self.generic_instance, self.last_instance])
        self.client.login(username='featuretest', password='pword')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 400,response.content)
        self.assertRegexpMatches(response.content, r'GenericLinksTestFeature')
        self.assertRegexpMatches(response.content, 
            r'OtherGenericLinksTestFeature')



def delete_w_contents(request, instances):
    return HttpResponse('Deleted')

def habitat_spreadsheet(request, instance):
    return HttpReponse('Report Contents')

def viewshed_map(request, instance):
    return HttpResponse('image')

def kml(request, instances):
    return HttpResponse('<kml />')
    
# Lets use the following as a canonical example of how to use all the features
# of this framework (will be kept up to date as api changes):
        
DESIGNATION_CHOICES = (
    ('R', 'Reserve'), 
    ('P', 'Park'),
    ('C', 'Conservation Area')
)

@register
class TestMpa(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)
    class Options:
        verbose_name = 'Marine Protected Area'
        form = 'lingcod.features.tests.MpaForm'
        manipulators = [ 'lingcod.manipulators.tests.TestManipulator' ]
        optional_manipulators = [ 'lingcod.manipulators.manipulators.ClipToGraticuleManipulator' ]
        links = (
            related('Habitat Spreadsheet',
                'lingcod.features.tests.habitat_spreadsheet',
                select='single',
                type='application/xls'
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )
        
class MpaForm(FeatureForm):
    class Meta:
        model = TestMpa

@register
class TestArray(FeatureCollection):
    class Options:
        form = 'lingcod.features.tests.TestArrayForm'
        valid_children = (
            'lingcod.features.tests.TestMpa', 
            'lingcod.features.tests.Pipeline', 
            'lingcod.features.tests.RenewableEnergySite')

class TestArrayForm(FeatureForm):
    class Meta:
        model = TestArray

@register
class TestFolder(FeatureCollection):
    
    def copy(self, user):
        copy = super(TestFolder, self).copy(user)
        copy.name = copy.name.replace(' (copy)', '-Copy')
        copy.save()
        return copy
    
    class Options:
        form = 'lingcod.features.tests.TestFolderForm'
        valid_children = (
            'lingcod.features.tests.TestMpa', 
            'lingcod.features.tests.TestArray', 
            'lingcod.features.tests.TestFolder', 
            'lingcod.features.tests.RenewableEnergySite')
        links = (
            edit('Delete folder and contents',
                'lingcod.features.tests.delete_w_contents',
                select='single multiple',
                confirm="""
                Are you sure you want to delete this folder and it's contents? 
                This action cannot be undone.
                """
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )

class TestFolderForm(FeatureForm):
    class Meta:
        model = TestFolder


TYPE_CHOICES = (
    ('W', 'Wind'),
    ('H', 'Hydrokinetic'),
)

@register
class RenewableEnergySite(PolygonFeature):
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    class Options:
        verbose_name = 'Renewable Energy Site'
        form = 'lingcod.features.tests.RenewableEnergySiteForm'
        links = (
            related('Viewshed Map',
                'lingcod.features.tests.viewshed_map',
                select='single',
                type='image/png'
            ),
            alternate('Export KML',
                'lingcod.features.tests.kml',
                select='multiple single'
            )
        )

class RenewableEnergySiteForm(FeatureForm):
    class Meta:
        model = RenewableEnergySite
        
@register
class Pipeline(LineFeature):
    type = models.CharField(max_length=30,default='')
    diameter = models.FloatField(null=True)
    class Options:
        verbose_name = 'Pipeline'
        form = 'lingcod.features.tests.PipelineForm'

class PipelineForm(FeatureForm):
    class Meta:
        model = Pipeline

@register
class Shipwreck(PointFeature):
    incident = models.CharField(max_length=100,default='')
    class Options:
        verbose_name = 'Shipwreck'
        form = 'lingcod.features.tests.ShipwreckForm'

class ShipwreckForm(FeatureForm):
    class Meta:
        model = Shipwreck


class JsonSerializationTest(TestCase):
    
    def setUp(self):
        self.json = workspace_json()
        self.dict = json.loads(self.json)

    def test_normal_features(self):
        fcdict = [x for x in self.dict['feature-classes'] if x['title'] == 'Shipwreck'][0]
        for lr in ['self','create','edit']:
            self.assertTrue(fcdict['link-relations'][lr])
        with self.assertRaises(KeyError):
            fcdict['link-relations']['alternate']
        with self.assertRaises(KeyError):
            fcdict['link-relations']['related']
         
    def test_generic(self):
        linkdict = [x for x in self.dict['generic-links'] if x['title'] == 'Generic Link'][0]
        for f in ["features_genericlinkstestfeature", "features_othergenericlinkstestfeature"]:
            self.assertTrue(f in linkdict['models'])
        self.assertFalse("features_shipwreck" in linkdict['models'])

    def test_custom_features(self):
        fcdict = [x for x in self.dict['feature-classes'] if x['id'] == 'features_testmpa'][0]
        for lr in ['self','create','edit', 'related']:
            self.assertTrue(fcdict['link-relations'][lr])
        with self.assertRaises(KeyError):
            fcdict['link-relations']['alternate']

        fcdict = [x for x in self.dict['feature-classes'] if x['title'] == 'LinkTestFeature'][0]
        for lr in ['self','create','edit', 'alternate']:
            self.assertTrue(fcdict['link-relations'][lr])
        with self.assertRaises(KeyError):
            fcdict['link-relations']['related']

    def test_collections(self):
        fcdict = [x for x in self.dict['feature-classes'] if x['title'] == 'TestArray'][0]
        self.assertTrue(fcdict['collection'])
        self.assertEquals(len(fcdict['collection']['classes']), 3)

    def test_url(self):
        url = '/features/workspace.json'
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.json)
        
        
class CopyTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.other_user = User.objects.create_user(
            'othertest', 'othertest@marinemap.org', password='pword')
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        self.user.groups.add(self.group1)
        self.other_user.groups.add(self.group1)
        enable_sharing(self.group1)

        self.mpa = TestMpa(user=self.user, name="My Mpa")
        self.folder = TestFolder(user=self.user, name="My Folder")
        self.folder.save()
        self.mpa.save()
    
    def test_login_required(self):
        self.client.logout()
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        self.assertEqual(response.status_code, 401, response)
            
    def test_copy(self):
        self.client.login(username='featuretest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d+')
    
    def test_copy_multiple_and_custom_copy_method(self):
        self.client.login(username='featuretest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        path = link.reverse([self.mpa, self.folder])
        response = self.client.post(path)
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response.content, r'Folder-Copy')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d+ features_testfolder_\d+')
    
    def test_other_users_can_copy_if_shared(self):
        self.mpa.share_with(self.group1) 
        self.client.login(username='othertest', password='pword')
        for link in self.mpa.get_options().links:
            if link.title == 'Copy':
                copy_link = link
                break
        self.assertEqual(Link, getattr(link, '__class__', None))
        response = self.client.post(link.reverse([self.mpa]))
        self.assertRegexpMatches(response.content, r'(copy)')
        self.assertRegexpMatches(response['X-MarineMap-Select'], 
            r'features_testmpa_\d')


class SpatialTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.client.login(username='featuretest', password='pword')
        
        g3 = GEOSGeometry('SRID=4326;POINT(-120.45 34.32)')
        g3.transform(settings.GEOMETRY_DB_SRID)
        self.wreck = Shipwreck(user=self.user, name="Nearby Wreck", geometry_final=g3)
        self.wreck.save()

        g2 = GEOSGeometry('SRID=4326;LINESTRING(-120.42 34.37, -121.42 33.37)')
        g2.transform(settings.GEOMETRY_DB_SRID)
        self.pipeline = Pipeline(user=self.user, name="My Pipeline", geometry_final=g2)
        self.pipeline.save()

        g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)
        self.mpa = TestMpa(user=self.user, name="My Mpa", geometry_orig=g1) 
        # geometry_final will be set with manipulator
        self.mpa.save()

    def test_feature_types(self):
        self.assertTrue(isinstance(self.wreck, PointFeature))
        self.assertEqual(self.wreck.geometry_final.geom_type,'Point')

        self.assertTrue(isinstance(self.pipeline, LineFeature))
        self.assertEqual(self.pipeline.geometry_final.geom_type,'LineString')

        self.assertTrue(isinstance(self.mpa, PolygonFeature))
        self.assertEqual(self.mpa.geometry_final.geom_type,'Polygon')

    def test_point_defaultkml_url(self):
        url = [link.reverse(self.wreck) for link in self.wreck.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))
        
    def test_line_defaultkml_url(self):
        url = [link.reverse(self.pipeline) for link in self.pipeline.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_polygon_defaultkml_url(self):
        url = [link.reverse(self.mpa) for link in self.mpa.get_options().links if link.title == "KML"][0]
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))


class CollectionTest(TestCase):
    
    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(
            'user1', 'featuretest@marinemap.org', password='pword')
        self.user2 = User.objects.create_user(
            'user2', 'othertest@marinemap.org', password='pword')

        self.mpa1 = TestMpa(user=self.user1, name="My Mpa")
        self.mpa1.save()
        self.mpa2 = TestMpa(user=self.user1, name="My Mpa 2")
        self.mpa2.save()
        self.folder1 = TestFolder(user=self.user1, name="My Folder")
        self.folder1.save()
        self.folder2 = TestFolder(user=self.user1, name="My Folder2")
        self.folder2.save()
        self.pipeline = Pipeline(user=self.user1, name="My Pipeline")
        self.pipeline.save()
        self.mpa3 = TestMpa(user=self.user2, name="User2s MPA")
        self.mpa3.save()

    def test_add_remove_at_feature_level(self):
        self.mpa1.add_to_collection(self.folder1)
        self.assertEqual(self.mpa1.collection, self.folder1)
        self.assertTrue(self.mpa1 in self.folder1.feature_set())

        self.mpa1.remove_from_collection()
        self.assertEqual(self.mpa1.collection, None)
        self.assertTrue(self.mpa1 not in self.folder1.feature_set())
        
        self.assertRaises(AssertionError, self.mpa3.add_to_collection, self.folder1)

    def test_add_remove_at_collection_level(self):
        self.folder1.add(self.mpa1)
        self.assertEqual(self.mpa1.collection, self.folder1)
        self.assertTrue(self.mpa1 in self.folder1.feature_set())

        self.folder1.remove(self.mpa1)
        self.assertEqual(self.mpa1.collection, None)
        self.assertTrue(self.mpa1 not in self.folder1.feature_set())

        self.assertRaises(AssertionError, self.folder1.add, self.mpa3)

    def test_feature_set(self):
        """
        When checking which mpas belong to folder1 we can:
        * look only at immediate children
        * look for children of a given feature class
        * look recursively through all containers

         folder1
          |- mpa1
          |- folder2
              | - mpa2
        """
        self.folder1.add(self.mpa1)
        self.folder2.add(self.mpa2)
        self.folder1.add(self.folder2)

        direct_children = self.folder1.feature_set(recurse=False)
        self.assertEqual(len(direct_children), 2)
        self.assertTrue(self.mpa1 in direct_children)
        self.assertTrue(self.folder2 in direct_children)
        self.assertTrue(self.mpa2 not in direct_children)

        direct_mpa_children = self.folder1.feature_set(recurse=False,feature_classes=[TestMpa])
        self.assertEqual(len(direct_mpa_children), 1)
        self.assertTrue(self.mpa1 in direct_mpa_children)
        self.assertTrue(self.folder2 not in direct_mpa_children)
        self.assertTrue(self.mpa2 not in direct_mpa_children)

        recursive_mpa_children = self.folder1.feature_set(recurse=True,feature_classes=[TestMpa])
        self.assertEqual(len(recursive_mpa_children), 2)
        self.assertTrue(self.mpa1 in recursive_mpa_children)
        self.assertTrue(self.folder2 not in recursive_mpa_children)
        self.assertTrue(self.mpa2 in recursive_mpa_children)

    def test_deep_recursion(self):
        """
         folder1
          |- mpa1
          |- folder2
              | - mpa2
              | - folder3
                   |- mpa3
                   |- folder4
                       |- mpa4
                       |- mpa5
        """
        mpa3 = TestMpa(user=self.user1, name="My Mpa")
        mpa3.save()
        mpa4 = TestMpa(user=self.user1, name="My Mpa 2")
        mpa4.save()
        mpa5 = TestMpa(user=self.user1, name="My Mpa 2")
        mpa5.save()
        folder3 = TestFolder(user=self.user1, name="My Folder")
        folder3.save()
        folder4 = TestFolder(user=self.user1, name="My Folder2")
        folder4.save()

        self.folder1.add(self.mpa1)
        self.folder2.add(self.mpa2)
        self.folder1.add(self.folder2)
        self.folder2.add(folder3)
        folder3.add(folder4)
        folder3.add(mpa3)
        folder4.add(mpa4)
        folder4.add(mpa5)

        recursive_mpa_children = self.folder1.feature_set(recurse=True,feature_classes=[TestMpa])
        self.assertEqual(len(recursive_mpa_children), 5)
        self.assertTrue(self.mpa1 in recursive_mpa_children)
        self.assertTrue(mpa5 in recursive_mpa_children)
        self.assertTrue(folder4 not in recursive_mpa_children)

        recursive_children = self.folder1.feature_set(recurse=True)
        self.assertEqual(len(recursive_children), 8)
        self.assertTrue(self.mpa1 in recursive_children)
        self.assertTrue(mpa5 in recursive_children)
        self.assertTrue(folder4 in recursive_children)

    def test_potential_parents(self):
        """
            Folder (of which TestArray is a valid child but Pipeline is NOT)
            TestArray (of which Pipeline is a valid child)
            Therefore, Folder is also a potential parent of Pipeline
            
            folder1
             |-my_array
               |-self.pipeline
               |-self.mpa1
        """
        pipeline_parents = Pipeline.get_options().get_potential_parents()
        self.assertTrue(TestArray in pipeline_parents) 
        self.assertTrue(self.folder1.__class__ in pipeline_parents)

        my_array = TestArray(user=self.user1, name="My TestArray")
        my_array.save()
        my_array.add(self.pipeline)
        my_array.add(self.mpa1)
        self.assertTrue(self.pipeline in my_array.feature_set())

        self.folder1.add(my_array)
        self.assertTrue(my_array in self.folder1.feature_set())
        self.assertTrue(self.pipeline in self.folder1.feature_set(recurse=True))

    def test_no_potential_parents(self):
        shipwreck_parents = Shipwreck.get_options().get_potential_parents()
        self.assertFalse(TestArray in shipwreck_parents) 
        self.assertFalse(TestFolder in shipwreck_parents) 
        self.assertEqual(len(shipwreck_parents), 0)

    def test_add_invalid_child_feature(self):
        """
        Try to add a Pipeline to Folder; feature.add has a runtime assertion so 
        this should raise an AssertionError
        """
        self.assertRaises(AssertionError, self.folder1.add, self.pipeline)

    def test_copy_feature_collection(self):
        """ 
        folder1 copied to folder1-copy
        make sure it contains mpa1-copy, mpa2-copy and folder2-copy
        """
        self.folder1.add(self.mpa1)
        self.folder2.add(self.mpa2)
        self.folder1.add(self.folder2)
        folder1_copy = self.folder1.copy(self.user1)
        folder1_copy.save()
        children = folder1_copy.feature_set(recurse=True)
        self.assertEqual(len(children),3, 
           "Folder1_copy should contain copies folder2, mpa1, mpa2 but doesn't")
        

class SharingTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        # Create 3 users
        self.password = 'iluvsharing'
        self.user1 = User.objects.create_user('user1', 'test@marinemap.org', password=self.password)
        self.user2 = User.objects.create_user('user2', 'test@marinemap.org', password=self.password)
        self.user3 = User.objects.create_user('user3', 'test@marinemap.org', password=self.password)

        # Create some groups
        # Group 1 has user1 and user2 and can share
        # Group 2 has user2 and user3 and has no sharing permissions
        # Group 3 has user1 only and no sharing permissions
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group1)

        self.group2 = Group.objects.create(name="Test Group 2")
        self.group2.save()
        self.user2.groups.add(self.group2)
        self.user3.groups.add(self.group2)

        self.group3 = Group.objects.create(name="Test Group 3")
        self.group3.save()
        self.user1.groups.add(self.group3)

        enable_sharing(self.group1)
        
        # Create some necessary objects
        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)

        # Create three Mpas by different users
        self.mpa1 = TestMpa.objects.create( name='Test_MPA_1', designation='R', user=self.user1, geometry_final=g1)
        self.mpa1.save()

        self.mpa2 = TestMpa.objects.create( name='Test_MPA_2', designation='R', user=self.user2, geometry_final=g1)
        self.mpa2.save()

        self.mpa3 = TestMpa.objects.create( name='Test_MPA_3', designation='R', user=self.user3, geometry_final=g1)
        self.mpa3.save()

        # Create a pipeline
        self.pipeline1 = Pipeline(user=self.user1, name="My Pipeline")
        self.pipeline1.save()

        #    folder1
        #     |-array1
        #       |-pipeline1
        #       |-mpa1

        self.array1 = TestArray.objects.create( name='Test_Array_1', user=self.user1)
        self.array1.save()
        self.array1.add(self.mpa1)
        self.array1.add(self.pipeline1)

        self.folder1 = TestFolder.objects.create(user=self.user1, name="My Folder")
        self.folder1.save()
        self.folder1.add(self.array1)

        self.folder1_share_url = self.folder1.get_options().get_share_form(self.folder1.pk)
        self.folder1_resource_url = self.folder1.get_options().get_resource(self.folder1.pk)

    def test_nested_folder_sharing(self):
        # Not shared yet
        viewable, response = self.pipeline1.is_viewable(self.user2)
        self.assertEquals( viewable, False)
        viewable, response = self.pipeline1.is_viewable(self.user3)
        self.assertEquals( viewable, False )

        # Share folder1 with group1; now group1 should be able to see array1
        self.folder1.share_with(self.group1)
        viewable, response = self.array1.is_viewable(self.user2)
        self.assertEquals( viewable, True, str(response.status_code) + str(response) )
        viewable, response = self.array1.is_viewable(self.user3)
        self.assertEquals( viewable, False )
        # ... and group1 should be able to see pipeline
        viewable, response = self.pipeline1.is_viewable(self.user2)
        self.assertEquals( viewable, True, str(response.status_code) + str(response) )
        viewable, response = self.pipeline1.is_viewable(self.user3)
        self.assertEquals( viewable, False )

    def test_user_sharing_groups(self):
        sgs = user_sharing_groups(self.user1)
        self.assertEquals(len(sgs),1)

        sgs = user_sharing_groups(self.user2)
        self.assertEquals(len(sgs),1)

        sgs = user_sharing_groups(self.user3)
        self.assertEquals(len(sgs),0)
        
    def test_nothing_shared(self):
        """
        Make sure nothing is shared yet
        """
        shared_mpas = TestMpa.objects.shared_with_user(self.user1)
        self.assertEquals(len(shared_mpas),0)

    def test_share_mpa_manager(self):
        """
        Make sure the basic sharing of mpas works 
        via the object manager (for returning querysets)
        """
        # User2 shares their MPA2 with Group1
        self.mpa2.share_with(self.group1)
        # User1 should see it (since they're part of Group1)
        shared_mpas = TestMpa.objects.shared_with_user(self.user1)
        self.assertEquals(len(shared_mpas),1)
        # User3 should not see it since they're not part of Group1
        shared_mpas = TestMpa.objects.shared_with_user(self.user3)
        self.assertEquals(len(shared_mpas),0)

    def test_share_mpa_method(self):
        """
        Make sure the basic sharing of mpas works 
        via the feature method (check viewability of particular instance)
        """
        # User2 shares their MPA2 with Group1
        self.mpa2.share_with(self.group1)
        # User 2 should be able to view it since they own it
        viewable, response = self.mpa2.is_viewable(self.user2)
        self.assertEquals( viewable, True )
        # User1 should see it (since they're part of Group1)
        viewable, response = self.mpa2.is_viewable(self.user1)
        self.assertEquals( viewable, True )
        # User3 should not see it since they're not part of Group1
        viewable, response = self.mpa2.is_viewable(self.user3)
        self.assertEquals(response.status_code, 403)
        self.assertEquals(viewable, False )

    def test_share_with_bad_group(self):
        """
        Make sure we can't share with a group which does not have permissions
        """
        # Would use assertRaises here but can't figure how to pass args to callable
        # see http://www.mail-archive.com/django-users@googlegroups.com/msg46609.html
        error_occured = False
        try:
            self.mpa2.share_with(self.group2) 
        except:
            error_occured = True
        self.assertTrue(error_occured)

    def test_share_by_bad_user(self):
        """
        Make sure user not belonging to the group can't share their objects
        """
        # User3 trys to share their MPA3 with Group1
        error_occured = False
        try:
            self.mpa3.share_with(self.group1) 
        except:
            error_occured = True
        self.assertTrue(error_occured)

    def test_share_collection_manager(self):
        """
        Arrays are containers of MPAs so their child objects should also appear to be shared
        Uses the class object manager
        """
        # User1 shares their array1 (which contains MPA1) with Group1
        self.array1.share_with(self.group1) 
        # User2 should see the mpa contained in array1 (since they're part of Group1)
        shared_mpas = TestMpa.objects.shared_with_user(self.user2)
        self.assertEquals(len(shared_mpas),1)
        # User3 should not see it (since they're not part of Group1)
        shared_mpas = TestMpa.objects.shared_with_user(self.user3)
        self.assertEquals(len(shared_mpas),0)

    def test_share_collection_method(self):
        """
        Arrays are containers of MPAs so their child objects should also appear to be shared
        Uses the feature's is_viewable() method
        """
        # User1 shares their array1 (which contains MPA1) with Group1
        self.array1.share_with(self.group1) 
        # User 1 should see it since they own it
        viewable, response = self.mpa1.is_viewable(self.user1)
        self.assertEquals( viewable, True )
        # User2 should see the mpa contained in array1 (since they're part of Group1)
        viewable, response = self.mpa1.is_viewable(self.user2)
        self.assertEquals( viewable, True )
        # User3 should not see it (since they're not part of Group1)
        viewable, response = self.mpa1.is_viewable(self.user3)
        self.assertEquals( viewable, False )


    def test_groups_users_sharing_with(self):
        """
        Test if we can get a list of groups and users who are sharing with a given user
        """
        # User1 shares their Mpa1 with Group1
        self.mpa1.share_with(self.group1) 
        # User1 should NOT see himself 
        sw = groups_users_sharing_with(self.user1)
        self.assertEquals(sw,None)
        # User2 should see group1:user1 as a sharer
        sw = groups_users_sharing_with(self.user2)
        self.assertNotEquals(sw,None)
        usernames = [x.username for x in sw['Test Group 1']['users']]
        self.assertEquals(usernames, ['user1'])
        # User3 should see nothing
        sw = groups_users_sharing_with(self.user3)
        self.assertEquals(sw, None)

    def test_get_share_form_401(self):
        # Need to log in
        response = self.client.get(self.folder1_share_url)
        self.assertEqual(response.status_code, 401)

    def test_get_share_form_403(self):
        # Need to own the feature in order to share it
        self.client.login(username=self.user3.username, password=self.password)
        response = self.client.get(self.folder1_share_url)
        self.assertEqual(response.status_code, 403)

    def test_get_share_form(self):
        self.client.login(username=self.user1.username, password=self.password)

        # user1 should be able to share with Group 1 only
        response = self.client.get(self.folder1_share_url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'Test Group 1')
        self.assertNotRegexpMatches(response.content, r'Test Group 2')
        self.assertNotRegexpMatches(response.content, r'Test Group 3')

        enable_sharing(self.group3)
        # Now user1 should be able to share with Group 1 & 3
        response = self.client.get(self.folder1_share_url)
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'Test Group 1')
        self.assertNotRegexpMatches(response.content, r'Test Group 2')
        self.assertRegexpMatches(response.content, r'Test Group 3')

    def test_post_share_form(self):
        # user 2 tries to get resource for folder1, not shared yet
        self.client.login(username=self.user2.username, password=self.password)
        response = self.client.get(self.folder1_resource_url)
        self.assertEqual(response.status_code, 403)
 
        # user 1 shares it
        self.client.logout()
        self.client.login(username=self.user1.username, password=self.password)
        response = self.client.post(self.folder1_share_url, {'sharing_groups': [self.group1.pk]})
        self.assertEqual(response.status_code, 200, response.content)

        # user2 tries again
        self.client.logout()
        self.client.login(username=self.user2.username, password=self.password)
        response = self.client.get(self.folder1_resource_url)
        self.assertEqual(response.status_code, 200)


