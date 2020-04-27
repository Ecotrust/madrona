from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import datetime

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(editable=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

class Entry(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(editable=False)
    summary = models.CharField(max_length=200,blank=True,null=True,help_text="One sentence. If not supplied, whole body text will show up in archive view.")
    body = models.TextField(help_text="Use HTML.")
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    is_draft = models.BooleanField("Draft", default=False, help_text="Check if this is a draft.")
    published_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True,editable=False)

    class Meta:
        verbose_name_plural = 'Entries'
        ordering = ('-published_on',)
        get_latest_by = 'published_on'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Entry, self).save(*args, **kwargs)
