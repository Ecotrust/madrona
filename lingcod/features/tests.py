from django.test import TestCase
from lingcod.features import validate_feature_config
from lingcod.features import FeatureConfigurationError
from lingcod.features.forms import FeatureForm

class FeatureConfigTest(TestCase):
    
    def test_check_for_inner_class(self):
        
        class TestFeatureFails(object):
            pass
            
        with self.assertRaisesRegexp(FeatureConfigurationError,'not defined'):
            validate_feature_config(TestFeatureFails)
            
    def test_check_for_form_class(self):

        class TestFeatureFails(object):
            class Rest:
                pass
                
        class TestFeature(object):
            class Rest:
                form = FeatureForm

        with self.assertRaisesRegexp(FeatureConfigurationError,'form'):
            validate_feature_config(TestFeatureFails)
        
        self.assertEqual(validate_feature_config(TestFeature), True)