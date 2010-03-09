from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from lingcod.user_profile.models import UserProfile

class UserProfileTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("user1", "user1@marinemap.org",password="pword")
        self.user2 = User.objects.create_user("user2", "user2@marinemap.org",password="pword")
        
    def test_login_required(self):
        url = reverse('user_profile-form',args=['nomatter'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_401_profile(self):
        self.client.login(username=self.user2.username, password='pword')
        url = reverse('user_profile-form',args=[self.user1.username])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_get_profile(self):
        self.client.login(username=self.user1.username, password='pword')
        url = reverse('user_profile-form',args=[self.user1.username])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_post_profile(self):
        self.client.login(username=self.user1.username, password='pword')
        url = reverse('user_profile-form',args=[self.user1.username])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        data = { 'first_name': 'Joe', 'last_name': 'Rando', 'email': 'joe@marinemap.org', 'about': 'Joe Rando is a man of few words' }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 302, response)

        joe = User.objects.get(pk=self.user1.pk)
        self.assertEquals(joe.last_name, 'Rando')
        joepro = UserProfile.objects.get(user=joe)
        self.assertEquals(joepro.about, 'Joe Rando is a man of few words')
