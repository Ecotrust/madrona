from django.shortcuts import render
from django.template import RequestContext
from madrona.shapes.forms import UploadForm


# TODO convert this to using ModelForm with a custom Django FileField
# For now we just stick an uploaded shapefile into a project directory

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.handle(request.FILES['file_obj'])
            #form.save() # if a modelform
            #form.cleaned_data['user'] = request.user
            return render(request, 'uploaded.html', {})
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})
