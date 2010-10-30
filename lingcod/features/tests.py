from django.test import TestCase
from lingcod.features import FeatureConfigurationError, FeatureConfig
from lingcod.features.models import Feature
from lingcod.features.forms import FeatureForm
import os
import shutil

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
    class Rest:
        form = 'lingcod.features.tests.TestFeatureForm'

class TestFeatureForm(FeatureForm):
    class Meta:
        model = TestGetFormClassFeature

class TestGetFormClassFailFeature(Feature):
    class Rest:
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
        class TestSlugFeature(Feature):
            class Rest:
                form = 'lingcod.features.form.FeatureForm'
                
        self.assertEqual(TestSlugFeature.get_config().slug, 'testslugfeature')
    
    def test_default_verbose_name(self):
        class TestDefaultVerboseNameFeature(Feature):
            class Rest:
                form = 'lingcod.features.form.FeatureForm'
        
        self.assertEqual(
            TestDefaultVerboseNameFeature.get_config().verbose_name, 
            'TestDefaultVerboseNameFeature')
    
    def test_custom_verbose_name(self):
        class TestCustomVerboseNameFeature(Feature):
            class Rest:
                form = 'lingcod.features.form.FeatureForm'
                verbose_name = 'vb-name'
        
        self.assertEqual(
            TestCustomVerboseNameFeature.get_config().verbose_name, 
            'vb-name')
        
    def test_default_show_template(self):
        class TestDefaultShowTemplateFeature(Feature):
            class Rest:
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
            class Rest:
                form = 'lingcod.features.form.FeatureForm'
                show_template = 'location/show.html'
        
        config = TestCustomShowTemplateFeature.get_config()
        path = TestCustomShowTemplateFeature.Rest.show_template
        delete_template(path)
        create_template(path)
        self.assertEqual(
            config.get_show_template().name, 
            path)
        delete_template(path)
        
    
    def test_missing_default_show_template(self):
        class TestMissingDefaultShowTemplateFeature(Feature):
            class Rest:
                form = 'lingcod.features.form.FeatureForm'
        
        config = TestMissingDefaultShowTemplateFeature.get_config()
        path = config.slug + '/show.html'
        self.assertEqual(
            config.get_show_template().name, 
            'rest/show.html')

    def test_missing_custom_show_template(self):
        class TestMissingCustomShowTemplateFeature(Feature):
            class Rest:
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