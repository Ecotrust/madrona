from django.test import TestCase
from madrona.features.tests import TestMpa, TestFolder
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from madrona.common.utils import enable_sharing

class HeatmapTest(TestCase):
    fixtures = ['example_data']

    def setUp(self):
        enable_sharing()

        self.user1 = User.objects.create_user(
            'user1', 'featuretest@madrona.org', password='pword')
        self.user2 = User.objects.create_user(
            'user2', 'othertest@madrona.org', password='pword')

        self.mpa1 = TestMpa(user=self.user1, name="My Mpa")
        self.mpa1.save()
        self.folder1 = TestFolder(user=self.user1, name="My Folder")
        self.folder1.save()
        self.mpa1.add_to_collection(self.folder1)

        self.tif_url = reverse("heatmap-collection-geotiff", kwargs={'collection_uids': self.folder1.uid})
        self.kmz_url = reverse("heatmap-collection-kmz", kwargs={'collection_uids': self.folder1.uid})

    def test_noauth(self):
        response = self.client.get(self.tif_url)
        self.assertEqual(response.status_code, 401)

        self.client.login(username=self.user2.username, password='pword')
        response = self.client.get(self.tif_url)
        self.assertEqual(response.status_code, 403)

    def test_urls(self):
        self.client.login(username=self.user1.username, password='pword')
        response = self.client.get(self.tif_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.kmz_url)
        self.assertEqual(response.status_code, 200)
