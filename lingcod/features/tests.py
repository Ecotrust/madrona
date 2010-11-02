from django.test import TestCase
from lingcod.features import FeatureConfigurationError, FeatureConfig
from lingcod.features.models import Feature
from lingcod.features.forms import FeatureForm
import os
import shutil
from django.test.client import Client
from django.contrib.auth.models import *

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
        
class TestGetFormClassFeature(Feature):
    class Config:
        form = 'lingcod.features.tests.TestFeatureForm'

class TestFeatureForm(FeatureForm):
    class Meta:
        model = TestGetFormClassFeature

class TestGetFormClassFailFeature(Feature):
    class Config:
        form = 'lingcod.features.tests.TestForm'

class TestForm:
    class Meta:
        model = TestGetFormClassFeature


class FeatureConfigTest(TestCase):
    
    def test_check_for_subclass(self):
        class NotAFeature:
            pass
        
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            FeatureConfig(NotAFeature)
    
    def test_check_for_inner_class(self):
        class TestFeatureFails(Feature):
            pass
            
        with self.assertRaisesRegexp(FeatureConfigurationError,'not defined'):
            TestFeatureFails.get_config()
            
    def test_must_have_form_class(self):
        class TestFeatureNoForm(Feature):
            class Config:
                pass

        with self.assertRaisesRegexp(FeatureConfigurationError,'form'):
            TestFeatureNoForm.get_config()
    
    def test_must_specify_form_as_string(self):
        class TestFeature(Feature):
            class Config:
                form = FeatureForm

        with self.assertRaisesRegexp(FeatureConfigurationError,'string'):
            TestFeature.get_config()

    def test_slug(self):
        class TestSlugFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
                
        self.assertEqual(TestSlugFeature.get_config().slug, 'testslugfeature')
    
    def test_default_verbose_name(self):
        class TestDefaultVerboseNameFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
        
        self.assertEqual(
            TestDefaultVerboseNameFeature.get_config().verbose_name, 
            'TestDefaultVerboseNameFeature')
    
    def test_custom_verbose_name(self):
        class TestCustomVerboseNameFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
                verbose_name = 'vb-name'
        
        self.assertEqual(
            TestCustomVerboseNameFeature.get_config().verbose_name, 
            'vb-name')
        
    def test_default_show_template(self):
        class TestDefaultShowTemplateFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
        
        config = TestDefaultShowTemplateFeature.get_config()
        path = config.slug + '/show.html'
        delete_template(path)
        create_template(path)
        self.assertEqual(
            config.get_show_template().name, 
            path)
        delete_template(path)
    
    def test_custom_show_template(self):
        class TestCustomShowTemplateFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
                show_template = 'location/show.html'
        
        config = TestCustomShowTemplateFeature.get_config()
        path = TestCustomShowTemplateFeature.Config.show_template
        delete_template(path)
        create_template(path)
        self.assertEqual(
            config.get_show_template().name, 
            path)
        delete_template(path)
        
    
    def test_missing_default_show_template(self):
        class TestMissingDefaultShowTemplateFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
        
        config = TestMissingDefaultShowTemplateFeature.get_config()
        path = config.slug + '/show.html'
        self.assertEqual(
            config.get_show_template().name, 
            'rest/show.html')

    def test_missing_custom_show_template(self):
        class TestMissingCustomShowTemplateFeature(Feature):
            class Config:
                form = 'lingcod.features.form.FeatureForm'
                show_template = 'location/show.html'

        config = TestMissingCustomShowTemplateFeature.get_config()
        self.assertEqual(
            config.get_show_template().name, 
            'rest/show.html')

    
    def test_get_form_class(self):
        self.assertEqual(
            TestGetFormClassFeature.get_config().get_form_class(),
            TestFeatureForm)
    
    def test_get_form_not_subclass(self):
        with self.assertRaisesRegexp(FeatureConfigurationError, 'subclass'):
            TestGetFormClassFailFeature.get_config().get_form_class()

    def test_json(self):
        pass

# Generic view tests
        
class DeleteTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = RestTestModel(user=self.user, name="My Name")
        self.test_instance.save()

    def test_delete_not_logged_in(self):
        """
        If user not logged in they can't delete anything
        401 status_code response
        """
        response = self.client.delete('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 401)

    def test_delete_not_owner(self):
        """
        Don't allow just any old user to delete objects.
        Return 403 Forbidden status code
        """
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username=other_user.username, password='pword')
        response = self.client.delete('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 403)

    def test_delete_not_owner_but_staff(self):
        """
        Staff users can delete anyone's stuff
        """
        staff_user = User.objects.create_user('staff', 'staff@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        pk = self.test_instance.pk
        self.assertEqual(RestTestModel.objects.filter(pk=pk).count(), 1)
        self.client.login(username='staff', password='pword')
        response = self.client.delete('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RestTestModel.objects.filter(pk=pk).count(), 0)

    def test_delete_authorized(self):
        """
        Users can delete objects that belong to them
        """
        pk = self.test_instance.pk
        self.assertEqual(RestTestModel.objects.filter(pk=pk).count(), 1)
        self.client.login(username='resttest', password='pword')
        response = self.client.delete('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RestTestModel.objects.filter(pk=pk).count(), 0)

    def test_delete_invalid_method(self):
        """
        http DELETE method must be used, not get or post
        """
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 405)
        response = self.client.post('/delete/%d/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 405)


class CreateFormTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')

    def test_user_not_logged_in(self):
        """
        Can't create stuff without being logged in.
        """
        response = self.client.get('/create/form/')
        self.assertEqual(response.status_code, 401)

    def test_get_form(self):
        """
        Returns a form that can be displayed on the client.
        """
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/create/form/')
        self.assertEqual(response.status_code, 200)

class CreateTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')

    def test_submit_not_authenticated(self):
        response = self.client.post('/create/', {'name': "My Test", 'user': 1})
        self.assertEqual(response.status_code, 401)

    def test_submit_invalid_form(self):
        old_count = RestTestModel.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/create/', {'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(old_count == RestTestModel.objects.count())
        self.assertNotEqual(response.content.find('This field is required.'), -1)

    def test_submit_valid_form(self):
        old_count = RestTestModel.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/create/', {'name': "My Test"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < RestTestModel.objects.count())
        inst = RestTestModel.objects.get(name='My Test')
        self.assertTrue(response['Location'].count(inst.get_absolute_url()) == 1)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        old_count = RestTestModel.objects.count()
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/create/', {'name': "My Test Hack Test", 'user': other_user.pk})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < RestTestModel.objects.count())
        new_instance = RestTestModel.objects.get(name='My Test Hack Test')
        self.assertNotEqual(new_instance.user, other_user)

class UpdateFormTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = RestTestModel(user=self.user, name="My Name")
        self.test_instance.save()

    def test_get_form(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/update/%s/form/' % (self.test_instance.pk))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content.find('My Name'), -1)

    def test_not_logged_in(self):
        response = self.client.get('/update/%s/form/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 401)

    def test_not_owner(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.get('/update/%s/form/' % (self.test_instance.pk))
        self.assertEqual(response.status_code, 403)

    def test_not_owner_but_staff(self):
        staff_user = User.objects.create_user('staff', 'other@marinemap.org', password='pword')
        staff_user.is_staff = True
        staff_user.save()
        self.client.login(username='staff', password='pword')
        response = self.client.get('/update/%s/form/' % (self.test_instance.pk))
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/update/300/form/')
        self.assertEqual(response.status_code, 404)

class UpdateTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = RestTestModel(user=self.user, name="My Name")
        self.test_instance.save()

    def test_post(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_post_validation_error(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': '',
        })
        self.assertEqual(response.status_code, 400)

    def test_post_not_logged_in(self):
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 401)

    def test_post_not_owner(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='other', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 403)

    def test_post_not_owner_but_staff(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        other_user.is_staff = True
        other_user.save()
        self.client.login(username='other', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_not_found(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk + 1000), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 404)

    def test_cannot_hack_user_field(self):
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/update/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
            'user': other_user.pk,
        })
        self.assertEqual(response.status_code, 200)
        edited_instance = RestTestModel.objects.get(pk=self.test_instance.pk)
        self.assertNotEqual(edited_instance.user, other_user)

class ResourceTest(TestCase):

    urls = 'lingcod.rest.test_urls'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = RestTestModel(user=self.user, name="My Name")
        self.test_instance.save()

    def test_delete(self):
        old_count = RestTestModel.objects.count()
        response = self.client.delete('/rest_test_models/%s/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        response = self.client.delete('/rest_test_models/%s/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(old_count > RestTestModel.objects.count())

    def test_update(self):
        response = self.client.post('/rest_test_models/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        response = self.client.post('/rest_test_models/%s/' % (self.test_instance.pk), {
            'name': 'My New Name',
        })
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/rest_test_models/%s/' % (self.test_instance.pk, ))
        self.assertContains(response, self.test_instance.name, status_code=200)