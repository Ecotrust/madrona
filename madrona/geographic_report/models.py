from django.db import models

class GeographicReport(models.Model):
    name = models.CharField(max_length=50, help_text="Will be used to identify a specific report when including chart via the geographic_report templatetag.")
    max_scale = models.IntegerField(help_text="In square miles. If no annotations are specified, this will be the scale.")

    def __unicode__(self):
        return self.name

class Annotation(models.Model):
    report = models.ForeignKey(GeographicReport)
    label = models.CharField(max_length=30, help_text="Label that will be shown to the user.")
    min = models.FloatField(blank=True, help_text="In square miles. If the annotation is to be a range, include this. If not, just specify a max value alone.")
    max = models.FloatField(blank=False, help_text="In square miles")
    color = models.CharField(max_length=6, default='000000', help_text='Color of the label as a hex value.')

    def __unicode__(self):
        return self.label
