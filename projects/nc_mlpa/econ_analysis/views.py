from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context
import os
from lingcod.common.utils import load_session
from nc_mlpa.mlpa.models import *
from econ_analysis.models import *
from Analysis import Analysis, AnalysisResult, EmptyAnalysisResult   
from Layers import *

def print_report(request, feature_id, user_group):
    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    layers = Layers()
    ports = layers.getPortsByGroup(user_group)
    all_results = []
    for single_port in ports:
        cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=user_group, port=single_port)
        results = list(cache)
        analysis_results = []
        for result in results:
            analysis_results.append(AnalysisResult(id=result.mpa_id, id_type='mpa', user_grp=user_group, port=single_port, species=result.species, mpaPercOverallArea=result.perc_area, mpaPercOverallValue=result.perc_value))
        analysis_results = flesh_out_results(user_group, single_port, analysis_results)
        
        #sort results alphabetically by species name
        analysis_results.sort(key=lambda obj: obj.species)
        
        #adjust recreational Fort Bragg display
        if user_group in ['Recreational Dive', 'Recreational Kayak', 'Recreational Private Vessel']:
            for result in analysis_results:
                if result.port == 'Fort Bragg':
                    result.port = 'Fort Bragg / Albion'
        
        all_results.append(analysis_results)
    return render_to_response('printable_report.html', RequestContext(request, {'mpa':mpa, 'user_group':user_group, 'all_results':all_results})) 

def impact_group_list(request, feature_id):
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    return render_to_response('groups_list.html', RequestContext(request, {'mpa_id':feature_id})) 
    
def impact_analysis(request, feature_id, group): 
    layers = Layers()
    if group not in layers.groups.keys():
        return render_to_response('impact_intro.html', RequestContext(request, {}))  
    group_name = layers.groups[group]  
    #the following port and species parameters are for testing on my local machine
    #return display_analysis(request, feature_id, group_name, port='Eureka', species='Salmon')
    #the following call is the more permanent/appropriate one for the server
    return display_analysis(request, feature_id, group_name, template='impact_analysis.html')
    
'''
Primarily used for testing...
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
def MpaEconAnalysis(request, feature_id):    
    if request.method != 'GET':
        return HttpResponseBadRequest('You must use GET')    
    #if not request.user.is_authenticated():
    #    return HttpResponse('You must be logged in', status=401)    

    group = request.GET.get("group")
    if not group:
        return HttpResponseBadRequest('Missing "group" parameter')
    else:
        group = group.replace('+',' ')
    
    #Optional port parameter
    port = request.GET.get("port")    
    if port:
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
    
    return display_analysis(request, feature_id, group, port, species, output)
  
def flesh_out_results(group, port, results):
    #fill out analysis results with species that are relevant for the given group, but not yet present in the results
    layers = Layers()
    group_species = layers.getSpeciesByGroup(group)
    result_species = [result.species for result in results]
    missing_species = [specs for specs in group_species if specs not in result_species]
    for spec in missing_species:
        results.append(EmptyAnalysisResult(group, port, spec))
    return results
    
def display_analysis(request, feature_id, group, port=None, species=None, output='json', template='impact_analysis.html'):
    
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)

    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    
    analysis = Analysis()

    #Get analysis results for given port or all ports
    layers = Layers()
    if not port:
        ports = layers.getPortsByGroup(group)
    else:
        ports = [port]
    
    all_results = []
    for single_port in ports:
        anal_results = []
        #See if we can retreive results from cache
        if species is None:
            cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=group, port=single_port)
        else:
            cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=group, port=single_port, species=species)
        cache_available = False
        if len(cache) > 0:
            cache_available = True
        for single_cache in cache:
            if single_cache.date_modified < mpa.date_modified:
                cache_available = False
                break
        
        if cache_available:
            results = list(cache)
            for result in results:
                anal_results.append(AnalysisResult(id=result.mpa_id, id_type='mpa', user_grp=group, port=single_port, species=result.species, mpaPercOverallArea=result.perc_area, mpaPercOverallValue=result.perc_value))
        #If not then run the analysis
        else:
            #since at least one cache was no current, remove all related entries as they will all be recreated and recached below
            for single_cache in cache:
                single_cache.delete()
            #Get all maps from the group (and possibly port and species) that we want to analyze
            maps = FishingImpactAnalysisMap.objects.getSubset(group, single_port, species)
            if maps is '':
                return HttpResponseBadRequest('User group, %s, does not exist' % group)
            
            #run the analysis
            anal_results = analysis.run(mpa, maps)
            if anal_results < 0:
                return HttpResponseBadRequest('Error running analysis')
            
            #Cache analysis results 
            for result in anal_results:
                cache = FishingImpactResults(mpa_id=mpa.id, group=group, port=result.port, species=result.species, perc_value=result.mpaPercOverallValue, perc_area=result.mpaPercOverallArea)
                cache.save()
            
        anal_results = flesh_out_results(group, single_port, anal_results)
        
        #sort results alphabetically by species name
        anal_results.sort(key=lambda obj: obj.species)
        
        #adjust recreational Fort Bragg display
        if group in ['Recreational Dive', 'Recreational Kayak', 'Recreational Private Vessel']:
            for result in anal_results:
                if result.port == 'Fort Bragg':
                    result.port = 'Fort Bragg / Albion'
        
        all_results.append(anal_results)
    
    
    """
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
    """
    '''
    if output == 'json':
        #is this import working?????
        import simplejson     
        anal_result_dicts = [x.__dict__ for x in anal_results]
        anal_results_json = simplejson.dumps(anal_result_dicts, sort_keys=True, indent=4)        
        return HttpResponse(anal_results_json, content_type='text/plain')
        #all_result_dicts = [x.__dict__ for x in all_results]
        #all_results_json = simplejson.dumps(all_result_dicts, sort_keys=True, indent=4)        
        #return HttpResponse(all_results_json, content_type='text/plain')
    else:
        printable = request.GET.get("printable")
        if printable == 'True':
            return render_to_response('impacts_page.html', RequestContext(request, {'mpa':mpa, 'results': anal_results, 'request':anal_results[0], 'valueChart': value_chart, 'areaChart': area_chart, 'printable':True}))
            #return render_to_response('impacts_page.html', RequestContext(request, {'mpa':mpa, 'all_results': all_results, 'printable':True}))
        else:
            #return render_to_response('fishery_impacts.html', RequestContext(request, {'mpa':mpa, 'results': anal_results, 'report':anal_results[0], 'valueChart': value_chart, 'areaChart': area_chart}))  
    '''    
    return render_to_response(template, RequestContext(request, {'mpa':mpa, 'all_results': all_results}))  

    
def MpaEconAnalysisTest(request):
    from Analysis import Analysis    
    analysis = Analysis()    
    #Optional return type parameter
    output = request.GET.get('output')
    if not output:
        output = 'html'
    else: 
        output = 'json'
        
    mpa = {'array_id': '', 'name': u'CI - Painted CaveHarris Point', 'id': 3002}
    all_results = [[{'port': u'Santa Barbara', 'array_id': None, 'srPercOverallValue': '93.67', 'mpaArea': '100.02', 'user_grp': u'Commercial', 'totalValue': '100000.00', 'totalArea': '343.46', 'mpa_id': 2949, 'mpaPercSrValue': '41.25', 'mpaPercSrArea': '31.15', 'srPercOverallArea': '93.49', 'mpaPercOverallValue': '38.63', 'mpaPercOverallArea': '29.12', 'mpaCells': 4145.0, 'mpaValue': '38634.29', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '93665.50', 'srArea': '321.12'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 30849, 'srPercOverallValue': '80.38', 'mpaArea': '229.83', 'user_grp': u'Commercial', 'srCells': 10844, 'totalValue': '100000.00', 'totalArea': '744.43', 'mpa_id': 2949, 'mpaPercSrValue': '91.33', 'mpaPercSrArea': '87.83', 'srPercOverallArea': '35.15', 'mpaPercOverallValue': '73.42', 'mpaPercOverallArea': '30.87', 'mpaCells': 9524.0, 'mpaValue': '73415.79', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '80381.20', 'srArea': '261.68'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 19943, 'srPercOverallValue': '97.13', 'mpaArea': '142.59', 'user_grp': u'Commercial', 'srCells': 17870, 'totalValue': '100000.00', 'totalArea': '481.25', 'mpa_id': 2949, 'mpaPercSrValue': '37.60', 'mpaPercSrArea': '33.07', 'srPercOverallArea': '89.61', 'mpaPercOverallValue': '36.52', 'mpaPercOverallArea': '29.63', 'mpaCells': 5909.0, 'mpaValue': '36520.49', 'species': u'Lobster', 'home_type': u'Port', 'srValue': '97134.02', 'srArea': '431.23'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 3991, 'srPercOverallValue': '99.69', 'mpaArea': '30.84', 'user_grp': u'Commercial', 'srCells': 3984, 'totalValue': '100000.00', 'totalArea': '96.31', 'mpa_id': 2949, 'mpaPercSrValue': '23.04', 'mpaPercSrArea': '32.08', 'srPercOverallArea': '99.82', 'mpaPercOverallValue': '22.97', 'mpaPercOverallArea': '32.02', 'mpaCells': 1278.0, 'mpaValue': '22966.37', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99689.65', 'srArea': '96.14'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12979, 'srPercOverallValue': '99.24', 'mpaArea': '44.59', 'user_grp': u'Commercial', 'srCells': 12915, 'totalValue': '100000.00', 'totalArea': '313.20', 'mpa_id': 2949, 'mpaPercSrValue': '6.07', 'mpaPercSrArea': '14.31', 'srPercOverallArea': '99.51', 'mpaPercOverallValue': '6.02', 'mpaPercOverallArea': '14.24', 'mpaCells': 1848.0, 'mpaValue': '6020.58', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99243.44', 'srArea': '311.66'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12978, 'srPercOverallValue': '95.91', 'mpaArea': '133.04', 'user_grp': u'Commercial', 'srCells': 12251, 'totalValue': '100000.00', 'totalArea': '313.18', 'mpa_id': 2949, 'mpaPercSrValue': '51.96', 'mpaPercSrArea': '45.00', 'srPercOverallArea': '94.40', 'mpaPercOverallValue': '49.83', 'mpaPercOverallArea': '42.48', 'mpaCells': 5513.0, 'mpaValue': '49830.35', 'species': u'Rock Crab', 'home_type': u'Port', 'srValue': '95905.80', 'srArea': '295.63'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 8177, 'srPercOverallValue': '99.30', 'mpaArea': '27.17', 'user_grp': u'Commercial', 'srCells': 8131, 'totalValue': '100013.82', 'totalArea': '197.32', 'mpa_id': 2949, 'mpaPercSrValue': '8.10', 'mpaPercSrArea': '13.85', 'srPercOverallArea': '99.44', 'mpaPercOverallValue': '8.04', 'mpaPercOverallArea': '13.77', 'mpaCells': 1126.0, 'mpaValue': '8040.01', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '99316.73', 'srArea': '196.21'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 29015, 'srPercOverallValue': '43.11', 'mpaArea': '200.07', 'user_grp': u'Commercial', 'srCells': 10223, 'totalValue': '100000.00', 'totalArea': '700.17', 'mpa_id': 2949, 'mpaPercSrValue': '90.93', 'mpaPercSrArea': '81.10', 'srPercOverallArea': '35.23', 'mpaPercOverallValue': '39.20', 'mpaPercOverallArea': '28.57', 'mpaCells': 8291.0, 'mpaValue': '39198.96', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '43110.29', 'srArea': '246.70'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 2620, 'srPercOverallValue': '31.84', 'mpaArea': '8.20', 'user_grp': u'Commercial', 'srCells': 673, 'totalValue': '100000.00', 'totalArea': '63.22', 'mpa_id': 2949, 'mpaPercSrValue': '68.40', 'mpaPercSrArea': '50.52', 'srPercOverallArea': '25.69', 'mpaPercOverallValue': '21.78', 'mpaPercOverallArea': '12.98', 'mpaCells': 340.0, 'mpaValue': '21782.13', 'species': u'Spot Prawn', 'home_type': u'Port', 'srValue': '31843.52', 'srArea': '16.24'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 11151, 'srPercOverallValue': '99.56', 'mpaArea': '87.26', 'user_grp': u'Commercial', 'srCells': 11109, 'totalValue': '100000.00', 'totalArea': '269.09', 'mpa_id': 2949, 'mpaPercSrValue': '5.07', 'mpaPercSrArea': '32.55', 'srPercOverallArea': '99.62', 'mpaPercOverallValue': '5.05', 'mpaPercOverallArea': '32.43', 'mpaCells': 3616.0, 'mpaValue': '5049.70', 'species': u'Urchin', 'home_type': u'Port', 'srValue': '99557.05', 'srArea': '268.08'}],[{'port': u'Santa Barbara', 'array_id': None, 'srPercOverallValue': '93.67', 'mpaArea': '100.02', 'user_grp': u'Commercial', 'totalValue': '100000.00', 'totalArea': '343.46', 'mpa_id': 2949, 'mpaPercSrValue': '41.25', 'mpaPercSrArea': '31.15', 'srPercOverallArea': '93.49', 'mpaPercOverallValue': '38.63', 'mpaPercOverallArea': '29.12', 'mpaCells': 4145.0, 'mpaValue': '38634.29', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '93665.50', 'srArea': '321.12'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 30849, 'srPercOverallValue': '80.38', 'mpaArea': '229.83', 'user_grp': u'Commercial', 'srCells': 10844, 'totalValue': '100000.00', 'totalArea': '744.43', 'mpa_id': 2949, 'mpaPercSrValue': '91.33', 'mpaPercSrArea': '87.83', 'srPercOverallArea': '35.15', 'mpaPercOverallValue': '73.42', 'mpaPercOverallArea': '30.87', 'mpaCells': 9524.0, 'mpaValue': '73415.79', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '80381.20', 'srArea': '261.68'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 19943, 'srPercOverallValue': '97.13', 'mpaArea': '142.59', 'user_grp': u'Commercial', 'srCells': 17870, 'totalValue': '100000.00', 'totalArea': '481.25', 'mpa_id': 2949, 'mpaPercSrValue': '37.60', 'mpaPercSrArea': '33.07', 'srPercOverallArea': '89.61', 'mpaPercOverallValue': '36.52', 'mpaPercOverallArea': '29.63', 'mpaCells': 5909.0, 'mpaValue': '36520.49', 'species': u'Lobster', 'home_type': u'Port', 'srValue': '97134.02', 'srArea': '431.23'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 3991, 'srPercOverallValue': '99.69', 'mpaArea': '30.84', 'user_grp': u'Commercial', 'srCells': 3984, 'totalValue': '100000.00', 'totalArea': '96.31', 'mpa_id': 2949, 'mpaPercSrValue': '23.04', 'mpaPercSrArea': '32.08', 'srPercOverallArea': '99.82', 'mpaPercOverallValue': '22.97', 'mpaPercOverallArea': '32.02', 'mpaCells': 1278.0, 'mpaValue': '22966.37', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99689.65', 'srArea': '96.14'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12979, 'srPercOverallValue': '99.24', 'mpaArea': '44.59', 'user_grp': u'Commercial', 'srCells': 12915, 'totalValue': '100000.00', 'totalArea': '313.20', 'mpa_id': 2949, 'mpaPercSrValue': '6.07', 'mpaPercSrArea': '14.31', 'srPercOverallArea': '99.51', 'mpaPercOverallValue': '6.02', 'mpaPercOverallArea': '14.24', 'mpaCells': 1848.0, 'mpaValue': '6020.58', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99243.44', 'srArea': '311.66'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12978, 'srPercOverallValue': '95.91', 'mpaArea': '133.04', 'user_grp': u'Commercial', 'srCells': 12251, 'totalValue': '100000.00', 'totalArea': '313.18', 'mpa_id': 2949, 'mpaPercSrValue': '51.96', 'mpaPercSrArea': '45.00', 'srPercOverallArea': '94.40', 'mpaPercOverallValue': '49.83', 'mpaPercOverallArea': '42.48', 'mpaCells': 5513.0, 'mpaValue': '49830.35', 'species': u'Rock Crab', 'home_type': u'Port', 'srValue': '95905.80', 'srArea': '295.63'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 8177, 'srPercOverallValue': '99.30', 'mpaArea': '27.17', 'user_grp': u'Commercial', 'srCells': 8131, 'totalValue': '100013.82', 'totalArea': '197.32', 'mpa_id': 2949, 'mpaPercSrValue': '8.10', 'mpaPercSrArea': '13.85', 'srPercOverallArea': '99.44', 'mpaPercOverallValue': '8.04', 'mpaPercOverallArea': '13.77', 'mpaCells': 1126.0, 'mpaValue': '8040.01', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '99316.73', 'srArea': '196.21'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 29015, 'srPercOverallValue': '43.11', 'mpaArea': '200.07', 'user_grp': u'Commercial', 'srCells': 10223, 'totalValue': '100000.00', 'totalArea': '700.17', 'mpa_id': 2949, 'mpaPercSrValue': '90.93', 'mpaPercSrArea': '81.10', 'srPercOverallArea': '35.23', 'mpaPercOverallValue': '39.20', 'mpaPercOverallArea': '28.57', 'mpaCells': 8291.0, 'mpaValue': '39198.96', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '43110.29', 'srArea': '246.70'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 2620, 'srPercOverallValue': '31.84', 'mpaArea': '8.20', 'user_grp': u'Commercial', 'srCells': 673, 'totalValue': '100000.00', 'totalArea': '63.22', 'mpa_id': 2949, 'mpaPercSrValue': '68.40', 'mpaPercSrArea': '50.52', 'srPercOverallArea': '25.69', 'mpaPercOverallValue': '21.78', 'mpaPercOverallArea': '12.98', 'mpaCells': 340.0, 'mpaValue': '21782.13', 'species': u'Spot Prawn', 'home_type': u'Port', 'srValue': '31843.52', 'srArea': '16.24'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 11151, 'srPercOverallValue': '99.56', 'mpaArea': '87.26', 'user_grp': u'Commercial', 'srCells': 11109, 'totalValue': '100000.00', 'totalArea': '269.09', 'mpa_id': 2949, 'mpaPercSrValue': '5.07', 'mpaPercSrArea': '32.55', 'srPercOverallArea': '99.62', 'mpaPercOverallValue': '5.05', 'mpaPercOverallArea': '32.43', 'mpaCells': 3616.0, 'mpaValue': '5049.70', 'species': u'Urchin', 'home_type': u'Port', 'srValue': '99557.05', 'srArea': '268.08'}]]
    '''
    if output == 'json':
        import simplejson
        anal_results_json = simplejson.dumps(anal_results, sort_keys=True, indent=4)        
        return HttpResponse(anal_results_json, content_type='text/plain')
    else:
    '''
    return render_to_response('fishery_impacts.html', RequestContext(request, {'mpa':mpa, 'all_results': all_results}))
