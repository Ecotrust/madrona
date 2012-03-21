from django.contrib import admin
from madrona.simplefaq.models import Faq, FaqGroup

class FaqAdmin(admin.ModelAdmin):
    search_fields = ('question', 'answer')
    list_display = ('question','importance','faq_group')   

admin.site.register(Faq,FaqAdmin)
admin.site.register(FaqGroup)
