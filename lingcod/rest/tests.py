from django.test import TestCase
from django.conf import settings
from lingcod.rest.views import *
# TODO: Take care of all UserForm references
# Temporary measure 
from lingcod.features.forms import FeatureForm as UserForm
from django.test.client import Client
from django.contrib.gis.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import *

class RestTestModel(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)

    @models.permalink
    def get_absolute_url(self):
        return ('rest_test_resource', (), {
            'pk': self.pk
        })

class RestTestForm(UserForm):
    class Meta:
        model = RestTestModel

def get_view(request):
    return HttpRequest('Test view')

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
        
class FormResourcesTest(TestCase):
    
    urls = 'lingcod.rest.test_urls'
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('resttest', 'resttest@marinemap.org', password='pword')
        self.test_instance = RestTestModel(user=self.user, name="My Name")
        self.test_instance.save()
    
    def test_create_form(self):
        response = self.client.get('/rest_test_models/form/')
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/rest_test_models/form/')
        self.assertContains(response, 'form', status_code=200)
        # Title automatically assigned if not given
        self.assertContains(response, 'New Resttestmodel', status_code=200)
    
    def test_create_submit(self):
        response = self.client.post('/rest_test_models/form/', {
            'name': "My Test", 'user': 1
        })
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        old_count = RestTestModel.objects.count()
        response = self.client.post('/rest_test_models/form/', {
            'name': "My Test", 'user': 1
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(old_count < RestTestModel.objects.count())
    
    def test_update_form(self):
        response = self.client.get('/rest_test_models/%d/form/' % (self.test_instance.pk, ))
        self.assertEqual(response.status_code, 401)
        self.client.login(username='resttest', password='pword')
        response = self.client.get('/rest_test_models/%d/form/' % (self.test_instance.pk, ))
        self.assertContains(response, 'form', status_code=200)
        self.assertContains(response, "Edit &#39;My Name&#39;", status_code=200)

class UtilsTest(TestCase):

    def test_rest_uid(self):
        from lingcod.rest.utils import rest_uid
        self.assertEqual(rest_uid(RestTestModel), 'rest_resttestmodel')

from elementtree.ElementTree import fromstring

def assertImplementsRestInterface(testcase, user, password, url, rest_uid, valid_form_data):
    testcase.client.login(username=user.username, password=password)
    response = testcase.client.get(url)
    testcase.assertContains(response, 'kml', status_code=200)
    root = fromstring(response.content)
    found = False
    
    # look for create form link
    for link in root.findall("*//{http://www.w3.org/2005/Atom}link"):
        if link.attrib['rel'] == 'marinemap.create_form':
            if link.attrib["{http://marinemap.org}model"] == rest_uid:
                found = link
    testcase.assertTrue(found != False, 'Could not find link with rel=marinemap.create_form within %s' % (url, ))
    
    # Now follow the link to get the form
    testcase.client.logout()
    response = testcase.client.get(found.attrib['href'])
    testcase.assertEqual(response.status_code, 401, "Must be authenticated")
    testcase.client.login(username=user.username, password=password)
    response = testcase.client.get(found.attrib['href'])
    testcase.assertContains(response, 'form', status_code=200)
    
    # get form action
    from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
    soup = BeautifulSoup(response.content)
    action = soup.find('form')['action']
    testcase.assertTrue(action != None)
    
    # check for validation errors
    import copy
    invalid_form_data = copy.deepcopy(valid_form_data)
    invalid_form_data['name'] = ''
    response = testcase.client.post(action, invalid_form_data)
    testcase.assertContains(response, 'form', status_code=400)

    # make sure submission works
    response = testcase.client.post(action, valid_form_data)
    testcase.assertEqual(response.status_code, 201, 'New resource created with valid form data')
    location = response['Location']
    
    # Get Attributes
    response = testcase.client.get(location)
    testcase.assertContains(response, valid_form_data['name'], status_code=200)
	
    # Use link to look for element in refreshed list
    response = testcase.client.get(url)
    testcase.assertContains(response, 'kml', status_code=200)
    root = BeautifulStoneSoup(response.content, selfClosingTags=['atom:link'])
    found = False
    for link in root.findAll('atom:link', attrs={'rel': 'self'}):
        if location.find(link['href']) != -1:
            found = link
    testcase.assertNotEqual(False, found, 'Could not find link with rel=self for resources')
    resource_url = found['href']
    testcase.assertTrue(found != False, 'Should be able to find self link with url %s that matches the location header of our newly created object.' % (url, ))
    element = found.parent
    name = element.find('name').contents[0]
    testcase.assertEqual(name, unicode(valid_form_data['name']))
    
    # look for update form
    text = str(element)
    form_link = element.find('atom:link', attrs={'rel': 'marinemap.update_form'})
    testcase.assertTrue(form_link != None, 'Should find link with marinemap.update_form rel')
    href = form_link['href']
    
    # grab it
    response = testcase.client.get(href)
    testcase.assertContains(response, 'myname', status_code=200)
    # action should match resource location
    soup = BeautifulSoup(response.content)
    action = soup.find('form')['action']
    testcase.assertEqual(resource_url, action)
    
    # try posting invalid form data
    response = testcase.client.post(action, invalid_form_data)
    testcase.assertContains(response, 'form', status_code=400)
    
    # try changing the name and posting valid form data
    valid_form_data['name'] = valid_form_data['name'] + ' Edited'
    response = testcase.client.post(action, valid_form_data)
    new_name = valid_form_data['name']
    testcase.assertEqual(response.status_code, 200)
    
    # should find changes in list resources
    response = testcase.client.get(url)
    testcase.assertContains(response, 'kml', status_code=200)
    root = BeautifulStoneSoup(response.content, selfClosingTags=['atom:link'])
    found = False
    for link in root.findAll('atom:link', attrs={'rel': 'self'}):
        if location.find(link['href']) != -1:
            found = link

    resource_url = found['href']
    testcase.assertTrue(found != False, 'Need to find our object again')
    element = found.parent
    name = element.find('name').contents[0]
    testcase.assertEqual(name, unicode(new_name))
    
    # Now delete
    response = testcase.client.delete(resource_url)
    testcase.assertEqual(response.status_code, 200)
    # make sure it can't be found now
    response = testcase.client.get(url)
    testcase.assertContains(response, 'kml', status_code=200)
    root = BeautifulStoneSoup(response.content)
    found = False
    for link in root.findAll('atom:link', attrs={'rel': 'self'}):
        if location.find(link['href']) != -1:
            found = link
    testcase.assertTrue(found == False, 'Shouldnt be able to find deleted object now')
    
# TODO: Add tests for optional arguments like template, extra_context, title
        