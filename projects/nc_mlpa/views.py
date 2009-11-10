from forms import MLPASaveForm, MLPALoadForm
from mlpa.models import *
from lingcod.mpa.views import *

def mlpaMpaLoadForm(request):
    '''
        Handler for load form request
    '''
    return mpaLoadForm(request, MLPALoadForm())

def mlpaMpaLoad(request):
    '''
        Handler for load form submission
    '''
    loadform = MLPALoadForm(request.GET)
    mpas = None
    if loadform.is_valid():
        user = loadform.cleaned_data['user']
        name = loadform.cleaned_data['name']
        mpas = MlpaMpa.objects.filter(user=user, name=name)
    return mpaLoad(request, loadform, mpas)

def mlpaMpaCommit(request):
    '''
        Handler for save form request and submission
    '''
    mpaform = MLPASaveForm()
    if request.method == 'POST':
        mpaform = MLPASaveForm(request.POST)
    return mpaCommit(request, mpaform)
