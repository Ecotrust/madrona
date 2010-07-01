from django.db import models

'''
NOTES:
    url entries should be unique -- a single url maps to a single task_id in a one-to-one fashion
    we'll want to make sure task is present in celery table, maybe verify on save?
'''
class URLtoTaskID(models.Model):
    url = models.TextField(verbose_name='Polling Url')
    task_id = models.TextField(verbose_name='task_id from celery_taskmeta')
