from django.conf.urls.defaults import *

registered_models = []

def register(*args):
    for model in args:
        print "registering " + str(model)
        registered_models.append(model)
