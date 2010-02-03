from django.contrib.gis import admin
from models import Entry, Tag

class TagAdmin(admin.ModelAdmin):
    pass

class EntriesAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_on'
    list_display = ('title', 'author', 'is_draft', 'published_on')
    search_fields = ['title', 'summary', 'body']

admin.site.register(Entry, EntriesAdmin)
admin.site.register(Tag, TagAdmin)
