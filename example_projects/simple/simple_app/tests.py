from django.test import TestCase
from simple_app.models import Mpa
from simple_app.models import MpaArray
from django.conf import settings

from lingcod.common.utils import get_mpa_class, get_array_class

class MpaTest(TestCase):
            
    def test_get_mpa_class(self):
        """
        Tests function that retrieves the mpa class using the MPA_CLASS
        setting.
        """
        self.assertEquals(Mpa, get_mpa_class())
    
class ArrayTest(TestCase):
    
    def test_get_array_class(self):
        self.assertEqual(MpaArray, get_array_class())
    
    def test_array_mpa_relations(self):
        MpaArray = get_array_class()
        mpa = get_mpa_class().objects.all()[0]
        array = MpaArray(name='Test Array', user=mpa.user)
        array.add_mpa(mpa)
        self.assertTrue(mpa in array.mpa_set)
        mpa.remove_from_array()
        self.assertFalse(mpa in array.mpa_set)