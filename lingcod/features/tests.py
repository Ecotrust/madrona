from django.test import TestCase
from lingcod.features import FeatureConfigurationError, FeatureConfig
from lingcod.features.models import Feature
from lingcod.features.forms import FeatureForm

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
            class Rest:
                pass

        with self.assertRaisesRegexp(FeatureConfigurationError,'form'):
            TestFeatureNoForm.get_config()
    
    def test_must_specify_form_as_string(self):

        class TestFeature(Feature):
            class Rest:
                form = FeatureForm

        with self.assertRaisesRegexp(FeatureConfigurationError,'string'):
            TestFeature.get_config()

    def test_slug(self):
        pass
    
    def test_default_verbose_name(self):
        pass
    
    def test_custom_verbose_name(self):
        pass
        
    def test_default_show_template(self):
        pass
    
    def test_custom_show_template(self):
        pass
    
    def test_missing_show__template(self):
        pass
    
    def test_get_form(self):
        pass
    
    def test_get_form_not_subclass(self):
        pass