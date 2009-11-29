from django.contrib.contenttypes.models import ContentType

def rest_uid(model_class_or_instance):
    c = ContentType.objects.get_for_model(model_class_or_instance)
    return "%s_%s" % (c.app_label, c.model)