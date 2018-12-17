"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from madrona.simplefaq.models import *
from django.conf import settings
from django.conf.urls import patterns, url, include

class SimpleFaqTest(TestCase):
    fixtures = ['example_data']

    def testFaqItemsPresent(self):
        """
        Check presence of initial FaqGroup and Faq
        """
        self.assertTrue(FaqGroup.objects.count() > 0)
        self.assertTrue(Faq.objects.count() > 0)

    def testFaqView(self):
        """
        test views.faq
        """
        response = self.client.get('/faq/', {})
        self.assertEquals(response.status_code, 200)
