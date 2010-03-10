from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context
import os
from nc_mlpa.mlpa.models import *
from econ_analysis.models import *


'''
Given a user group 'group' and port/county 'port', runs fishing impact analysis on each 
of the species fished out of the port/county for the given user group.  Accepts an optional
species parameter in which case it only analyzes the single species
    status codes:
        200: success, returning JSON result
        401: not logged in
        403: user doesn't own
        404: pk not specified or mpa with pk doesn't exist or missing parameters
        500: must use get
'''
def MpaEconAnalysis(request, feature_id, format='json'):    
    if request.method != 'GET':
        return HttpResponseBadRequest('You must use GET')    
    #if not request.user.is_authenticated():
    #    return HttpResponse('You must be logged in', status=401)    

    #SHOULD BE ABLE TO REMOVE THESE FROM THE ACTUAL URL (AFTER TESTING)
    group = request.GET.get("group")
    if not group:
        return HttpResponseBadRequest('Missing "group" parameter')
    else:
        group = group.replace('+',' ')
    
    port = request.GET.get("port")    
    if not port:
        return HttpResponseBadRequest('Missing "port" parameter')
    else:
        port = port.replace('+',' ')    
        
    #Optional species parameter
    species = request.GET.get('species')
    if species:
        species = species.replace('+',' ')
    
    #Optional return type parameter
    output = request.GET.get('output')
    if not output:
        output = 'json'
    else: 
        output = 'html'
    
    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    #if request.user != mpa.user:
    #    return HttpResponseForbidden('You cannot analyze MPA\'s you don\'t own')    
    
    from Analysis import Analysis    
    analysis = Analysis()

    #Get only the maps we want to analyze
    maps = FishingImpactAnalysisMap.objects.getSubset(group, port, species)
    if maps is '':
        return HttpResponseBadRequest('User group or port does not exist')
    
    anal_results = analysis.run(mpa, maps)
    if anal_results < 0:
        return HttpResponseBadRequest('Error running analysis')

    x_perc_value_mpa = []
    x_perc_value_sr = []    
    x_perc_area_mpa = []
    x_perc_area_sr = []
    y_labels = []
       
    for result in anal_results:          
        perc_value_mpa = float(result.mpaPercOverallValue)
        x_perc_value_mpa.append(perc_value_mpa)
        perc_value_sr = float(result.srPercOverallValue)
        x_perc_value_sr.append(perc_value_sr - perc_value_mpa)
        perc_area_mpa = float(result.mpaPercOverallArea)
        x_perc_area_mpa.append(perc_area_mpa)
        perc_area_sr = float(result.srPercOverallArea)
        x_perc_area_sr.append(perc_area_sr - perc_area_mpa)  
        y_labels.insert(0, result.species)           
    
    xLabels = ['0','-','10','-','20','-','30','-','40','-','50','-','60','-','70','-','80','-','90','-','100']
    lowColor = 'E8492D'
    highColor = 'FF9648'
    legendLabels = ('A. % Area of total fishing grounds affected by your proposed MPA', 'C. % Area of total fishing grounds within the study area')    
    area_chart = analysis.createStackChart(x_perc_area_mpa,
                                           x_perc_area_sr, 
                                           lowColor, 
                                           highColor, 
                                           xLabels, 
                                           y_labels, 
                                           legendLabels)     
    xLabels = ['0','-','10','-','20','-','30','-','40','-','50','-','60','-','70','-','80','-','90','-','100']
    lowColor = '4A58E8'
    highColor = '8BBBFF'
    legendLabels = ('A. % Value of total fishing grounds affected by your proposed MPA', 'C. % Value of total fishing grounds within the study area')
    value_chart = analysis.createStackChart(x_perc_value_mpa,
                                            x_perc_value_sr, 
                                            lowColor, 
                                            highColor, 
                                            xLabels, 
                                            y_labels, 
                                            legendLabels)   
    
    if output == 'json':
        import simplejson     
        anal_result_dicts = [x.__dict__ for x in anal_results]
        anal_results_json = simplejson.dumps(anal_result_dicts, sort_keys=True, indent=4)        
        return HttpResponse(anal_results_json, content_type='text/plain')
    else:
        printable = request.GET.get("printable")
        if printable == 'True':
            return render_to_response('impacts_page.html', RequestContext(request, {'mpa':mpa, 'results': anal_results, 'request':anal_results[0], 'valueChart': value_chart, 'areaChart': area_chart, 'printable':True}))
        else:
            return render_to_response('fishery_impacts.html', RequestContext(request, {'mpa':mpa, 'results': anal_results, 'report':anal_results[0], 'valueChart': value_chart, 'areaChart': area_chart}))  
