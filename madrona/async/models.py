from django.db import models
from djcelery.models import TaskMeta

'''
NOTES:
    url entries should be unique -- a single url maps to a single task_id in a one-to-one fashion
'''
class URLtoTaskID(models.Model):
    url = models.TextField(verbose_name='Polling Url')
    task_id = models.TextField(verbose_name='task_id from celery_taskmeta')

