from forms import SimpleSaveForm, SimpleLoadForm
from django.shortcuts import redirect
from simple_app.models import *
from lingcod.mpa.views import *

def simpleLoadForm(request):
    '''
        Handler for load form request
    '''
    return mpaLoadForm(request, SimpleLoadForm())

def simpleLoad(request):
    '''
        Handler for load form submission
    '''
    loadform = SimpleLoadForm(request.GET)
    mpas = None
    if loadform.is_valid():
        user = loadform.cleaned_data['user']
        name = loadform.cleaned_data['name']
        mpas = Mpa.objects.filter(user=user, name=name)
    return mpaLoad(request, mpas, loadform)

def simpleCommit(request):
    '''
        Handler for save form request and submission
    '''
    saveform = SimpleSaveForm()
    if request.method == 'POST':
        saveform = SimpleSaveForm(request.POST)
    return mpaCommit(request, saveform)

def manipulatorList(request):
    return redirect('/manipulators/list/simple_app/mpa/')