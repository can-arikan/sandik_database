from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpResponseRedirect
from .models import TutanakResimVeri, Veri, TutanakImage

class TutanakImageAdmin(ModelAdmin):
    fields = ('barcode', 'tutanak_veri', 'need_to_be_checked')
    
    change_form_template = "entities/open_image.html"
    
    def response_change(self, request, obj):
        if "_open-image" in request.POST:
            return HttpResponseRedirect("http://localhost:8000/get_image?image_id={}".format(obj.pk))
        return super().response_change(request, obj)

# Register your models here.
admin.site.register(TutanakResimVeri)
admin.site.register(TutanakImage, TutanakImageAdmin)
admin.site.register(Veri)