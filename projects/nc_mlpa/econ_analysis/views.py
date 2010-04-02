from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context
import os
from lingcod.common.utils import load_session
from nc_mlpa.mlpa.models import *
from econ_analysis.models import *
from Layers import *
from Analysis import *


'''
Accessed via named url when user selects a group (Commercial, Recreational Dive, etc) to run analysis on 
'''
def impact_analysis(request, feature_id, group, feature='mpa'): 
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    if not user.has_perm('layers.view_ecotrustlayerlist'):
        return HttpResponse('You must have permission to view this information.', status=401)  
    
    group_name = Layers.GROUPS[group]
    if feature == 'mpa':
        #the following port and species parameters are for testing on my local machine
        #return display_mpa_analysis(request, feature_id, group_name, port='Eureka', species='Salmon')
        #the following call is the more permanent/appropriate one for the server
        return display_mpa_analysis(request, feature_id, group_name)
    else:
        #the following port and species parameters are for testing on my local machine
        #return display_array_analysis(request, feature_id, group_name, port='Eureka', species='Salmon')
        return display_array_analysis(request, feature_id, group_name)

#remember to remove unused templates from repository (and my own directory)
def display_array_analysis(request, feature_id, group, port=None, species=None, template='array_impact_analysis.html'):
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    if not user.has_perm('layers.view_ecotrustlayerlist'):
        return HttpResponse('You must have permission to view this information.', status=401)
    
    array = get_object_or_404(MpaArray, pk=feature_id)
    
    #Get a list of mpas associated with this array
    mpas = array.mpa_set
       
    array_results = []
    #Sum results for each species, in each port, for each mpa in the array
    #What to do if mpa_analysis_results returns a Response object instead of a result?
    for mpa in mpas:
        if mpa.designation_id is not None:
            mpa_results = mpa_analysis_results(mpa, group, port, species)
            array_results.append(mpa_results)
    
    aggregated_results = aggregate_array_results(array_results, group)
    
    analysis_results = []
    #ports = GetPortsByGroup(group)
    #for port in ports:
        #port_results = []
    for species, results in aggregated_results.iteritems():
        analysis_results.append(AnalysisResult(id=array.id, id_type='array', user_grp=group, port=port, species=species, mpaPercOverallArea=results['Area'], mpaPercOverallValue=results['Value']))
    #analysis_results.append(port_results)
        
    return render_to_response(template, RequestContext(request, {'array':array, 'array_results': analysis_results}))  

    
def aggregate_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    for mpa_results in array_results:
        #why does this have to be index 0?  
        #is there an unneeded list here?
        for result in mpa_results[0]:
            if result.mpaPercOverallValue == '---':
                pass
            elif aggregated_array_results[result.species]['Value'] == '---':
                aggregated_array_results[result.species]['Value'] = float(result.mpaPercOverallValue)
                aggregated_array_results[result.species]['Area'] = float(result.mpaPercOverallArea)
            else:
                #thinking back to displaying results with 1 significant digit after decimal...
                #perhaps that reduction should happen at display time and not before 
                #that way we won't be losing precision here in the aggregation
                aggregated_array_results[result.species]['Value'] += result.mpaPercOverallValue
                aggregated_array_results[result.species]['Area'] += result.mpaPercOverallArea
    return aggregated_array_results       

    
def get_empty_array_results_dictionary(group):
    group_species = GetSpeciesByGroup(group)
    initialValue = '---'
    initialArea = '---'
    if group == 'Commercial':
        species_results = dict( (Layers.COMMERCIAL_SPECIES_DISPLAY[species], {'Value':initialValue, 'Area':initialArea}) for species in group_species)
    else:
        species_results = dict( (species, {'Value':initialValue, 'Area':initialArea}) for species in group_species)
    #results = dict( (port, species_results) for port in Layers.PORTS.values())
    #change this name to results once we know this works
    return species_results
  
'''
Called from impact_analysis and MpaEconAnalysis
Renders template with embedded analysis results
'''
def display_mpa_analysis(request, feature_id, group, port=None, species=None, template='impact_analysis.html'):
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    if not user.has_perm('layers.view_ecotrustlayerlist'):
        return HttpResponse('You must have permission to view this information.', status=401)

    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    
    mpa_results = mpa_analysis_results(mpa, group, port, species)
    
    try:
        #if mpa_analysis_results threw an error it will return a response object of some sort
        if mpa_results.status_code:
            response_object = mpa_results
            return response_object
    except:
        #otherwise it worked 
        return render_to_response(template, RequestContext(request, {'mpa':mpa, 'all_results': mpa_results}))  

#would be nice to produce some helper methods from within here...
def mpa_analysis_results(mpa, group, port, species):
    mpa_results = []
    
    #Get analysis results for given port or all ports 
    if not port:
        ports = GetPortsByGroup(group)
    else:
        ports = [port]
        
    #Get results for each port
    for single_port in ports:
        analysis_results = []
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
        
        #get results from cache
        #if they don't exist or are out of date, then run the analysis
        if cache_available:
            results = list(cache)
            for result in results:
                analysis_results.append(AnalysisResult(id=result.mpa_id, id_type='mpa', user_grp=group, port=single_port, species=result.species, mpaPercOverallArea=result.perc_area, mpaPercOverallValue=result.perc_value))
        else: 
            #since at least one cache was not current, remove all related entries as they will all be recreated and recached below
            for single_cache in cache:
                single_cache.delete()
            #Get all maps from the group and port (and possibly species) that we want to analyze
            maps = FishingImpactAnalysisMap.objects.getSubset(group, single_port, species)
            if maps is '':
                return HttpResponseBadRequest('A Fishing Map with User group, %s, Port, %s, and Species, %s, does not exist.' % (group, single_port, species))
            
            #run the analysis
            analysis = Analysis()
            analysis_results = analysis.run(mpa, maps)
            if analysis_results < 0:
                return HttpResponseBadRequest('Error running analysis')
            
            #Cache analysis results 
            cache_analysis_results(analysis_results, group, mpa)
            
        #Expand results to include those species that exist within the group but not perhaps within this port (denoted with '---')
        analysis_results = flesh_out_results(group, single_port, analysis_results)

        #sort results alphabetically by species name
        analysis_results.sort(key=lambda obj: obj.species)
        
        #adjust recreational Fort Bragg display
        analysis_results = adjust_fortbragg_rec_display(analysis_results, group)
        
        mpa_results.append(analysis_results)
    return mpa_results
    
'''
Accessed via named url when a user selects the View Printable Report link at the bottom of analysis results display
'''
def print_report(request, feature_id, user_group):
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    if not user.has_perm('layers.view_ecotrustlayerlist'):
        return HttpResponse('You must have permission to view this information.', status=401)
        
    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    ports = GetPortsByGroup(user_group)
    all_results = []
    for single_port in ports:
        #should we ensure this only returns a single row?
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

def cache_analysis_results(results, group, mpa):
    for result in results:
        cache = FishingImpactResults(mpa_id=mpa.id, group=group, port=result.port, species=result.species, perc_value=result.mpaPercOverallValue, perc_area=result.mpaPercOverallArea)
        cache.save()

def adjust_fortbragg_rec_display(results, group):
    if group in ['Recreational Dive', 'Recreational Kayak', 'Recreational Private Vessel']:
        for result in results:
            if result.port == 'Fort Bragg':
                result.port = 'Fort Bragg / Albion'
    return results
        
'''
Called by display_mpa_analysis and print_report
Fills out analysis results with species that are relevant for the given group, but not yet present in the results
'''
def flesh_out_results(group, port, results):
    group_species = GetSpeciesByGroup(group)
    result_species = [result.species for result in results]
    missing_species = [specs for specs in group_species if specs not in result_species]
    for spec in missing_species:
        results.append(EmptyAnalysisResult(group, port, spec))
    if group == 'Commercial':
        results = adjust_commercial_species(results)
    if group == 'Edible Seaweed':
        for result in results:
            result.species = 'Seaweed (Hand Harvest)'
    return results
    
    
'''
Called by flesh_out_results
Modifies commercial species for appropriate display:
    Species Name(s) (Catch Method)
'''
def adjust_commercial_species(results):
    species_dict = Layers.COMMERCIAL_SPECIES_DISPLAY
    for result in results:
        result.species = species_dict[result.species]
    return results

    
'''
Primarily used for testing...
'''
def MpaEconAnalysis(request, feature_id):  
    user = request.user 
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401) 
    if not user.has_perm('layers.view_ecotrustlayerlist'):
        return HttpResponse('You must have permission to view this information.', status=401)
    if request.method != 'GET':
        return HttpResponseBadRequest('You must use GET')    

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
    
    return display_mpa_analysis(request, feature_id, group, port, species)

    
'''
Testing Remnant
Not ready to throw this away yet...
'''
def MpaEconAnalysisTest(request):
    #from Analysis import Analysis    
    analysis = Analysis()    
   
    mpa = {'array_id': '', 'name': u'CI - Painted CaveHarris Point', 'id': 3002}
    all_results = [[{'port': u'Santa Barbara', 'array_id': None, 'srPercOverallValue': '93.67', 'mpaArea': '100.02', 'user_grp': u'Commercial', 'totalValue': '100000.00', 'totalArea': '343.46', 'mpa_id': 2949, 'mpaPercSrValue': '41.25', 'mpaPercSrArea': '31.15', 'srPercOverallArea': '93.49', 'mpaPercOverallValue': '38.63', 'mpaPercOverallArea': '29.12', 'mpaCells': 4145.0, 'mpaValue': '38634.29', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '93665.50', 'srArea': '321.12'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 30849, 'srPercOverallValue': '80.38', 'mpaArea': '229.83', 'user_grp': u'Commercial', 'srCells': 10844, 'totalValue': '100000.00', 'totalArea': '744.43', 'mpa_id': 2949, 'mpaPercSrValue': '91.33', 'mpaPercSrArea': '87.83', 'srPercOverallArea': '35.15', 'mpaPercOverallValue': '73.42', 'mpaPercOverallArea': '30.87', 'mpaCells': 9524.0, 'mpaValue': '73415.79', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '80381.20', 'srArea': '261.68'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 19943, 'srPercOverallValue': '97.13', 'mpaArea': '142.59', 'user_grp': u'Commercial', 'srCells': 17870, 'totalValue': '100000.00', 'totalArea': '481.25', 'mpa_id': 2949, 'mpaPercSrValue': '37.60', 'mpaPercSrArea': '33.07', 'srPercOverallArea': '89.61', 'mpaPercOverallValue': '36.52', 'mpaPercOverallArea': '29.63', 'mpaCells': 5909.0, 'mpaValue': '36520.49', 'species': u'Lobster', 'home_type': u'Port', 'srValue': '97134.02', 'srArea': '431.23'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 3991, 'srPercOverallValue': '99.69', 'mpaArea': '30.84', 'user_grp': u'Commercial', 'srCells': 3984, 'totalValue': '100000.00', 'totalArea': '96.31', 'mpa_id': 2949, 'mpaPercSrValue': '23.04', 'mpaPercSrArea': '32.08', 'srPercOverallArea': '99.82', 'mpaPercOverallValue': '22.97', 'mpaPercOverallArea': '32.02', 'mpaCells': 1278.0, 'mpaValue': '22966.37', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99689.65', 'srArea': '96.14'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12979, 'srPercOverallValue': '99.24', 'mpaArea': '44.59', 'user_grp': u'Commercial', 'srCells': 12915, 'totalValue': '100000.00', 'totalArea': '313.20', 'mpa_id': 2949, 'mpaPercSrValue': '6.07', 'mpaPercSrArea': '14.31', 'srPercOverallArea': '99.51', 'mpaPercOverallValue': '6.02', 'mpaPercOverallArea': '14.24', 'mpaCells': 1848.0, 'mpaValue': '6020.58', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99243.44', 'srArea': '311.66'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12978, 'srPercOverallValue': '95.91', 'mpaArea': '133.04', 'user_grp': u'Commercial', 'srCells': 12251, 'totalValue': '100000.00', 'totalArea': '313.18', 'mpa_id': 2949, 'mpaPercSrValue': '51.96', 'mpaPercSrArea': '45.00', 'srPercOverallArea': '94.40', 'mpaPercOverallValue': '49.83', 'mpaPercOverallArea': '42.48', 'mpaCells': 5513.0, 'mpaValue': '49830.35', 'species': u'Rock Crab', 'home_type': u'Port', 'srValue': '95905.80', 'srArea': '295.63'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 8177, 'srPercOverallValue': '99.30', 'mpaArea': '27.17', 'user_grp': u'Commercial', 'srCells': 8131, 'totalValue': '100013.82', 'totalArea': '197.32', 'mpa_id': 2949, 'mpaPercSrValue': '8.10', 'mpaPercSrArea': '13.85', 'srPercOverallArea': '99.44', 'mpaPercOverallValue': '8.04', 'mpaPercOverallArea': '13.77', 'mpaCells': 1126.0, 'mpaValue': '8040.01', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '99316.73', 'srArea': '196.21'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 29015, 'srPercOverallValue': '43.11', 'mpaArea': '200.07', 'user_grp': u'Commercial', 'srCells': 10223, 'totalValue': '100000.00', 'totalArea': '700.17', 'mpa_id': 2949, 'mpaPercSrValue': '90.93', 'mpaPercSrArea': '81.10', 'srPercOverallArea': '35.23', 'mpaPercOverallValue': '39.20', 'mpaPercOverallArea': '28.57', 'mpaCells': 8291.0, 'mpaValue': '39198.96', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '43110.29', 'srArea': '246.70'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 2620, 'srPercOverallValue': '31.84', 'mpaArea': '8.20', 'user_grp': u'Commercial', 'srCells': 673, 'totalValue': '100000.00', 'totalArea': '63.22', 'mpa_id': 2949, 'mpaPercSrValue': '68.40', 'mpaPercSrArea': '50.52', 'srPercOverallArea': '25.69', 'mpaPercOverallValue': '21.78', 'mpaPercOverallArea': '12.98', 'mpaCells': 340.0, 'mpaValue': '21782.13', 'species': u'Spot Prawn', 'home_type': u'Port', 'srValue': '31843.52', 'srArea': '16.24'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 11151, 'srPercOverallValue': '99.56', 'mpaArea': '87.26', 'user_grp': u'Commercial', 'srCells': 11109, 'totalValue': '100000.00', 'totalArea': '269.09', 'mpa_id': 2949, 'mpaPercSrValue': '5.07', 'mpaPercSrArea': '32.55', 'srPercOverallArea': '99.62', 'mpaPercOverallValue': '5.05', 'mpaPercOverallArea': '32.43', 'mpaCells': 3616.0, 'mpaValue': '5049.70', 'species': u'Urchin', 'home_type': u'Port', 'srValue': '99557.05', 'srArea': '268.08'}],[{'port': u'Santa Barbara', 'array_id': None, 'srPercOverallValue': '93.67', 'mpaArea': '100.02', 'user_grp': u'Commercial', 'totalValue': '100000.00', 'totalArea': '343.46', 'mpa_id': 2949, 'mpaPercSrValue': '41.25', 'mpaPercSrArea': '31.15', 'srPercOverallArea': '93.49', 'mpaPercOverallValue': '38.63', 'mpaPercOverallArea': '29.12', 'mpaCells': 4145.0, 'mpaValue': '38634.29', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '93665.50', 'srArea': '321.12'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 30849, 'srPercOverallValue': '80.38', 'mpaArea': '229.83', 'user_grp': u'Commercial', 'srCells': 10844, 'totalValue': '100000.00', 'totalArea': '744.43', 'mpa_id': 2949, 'mpaPercSrValue': '91.33', 'mpaPercSrArea': '87.83', 'srPercOverallArea': '35.15', 'mpaPercOverallValue': '73.42', 'mpaPercOverallArea': '30.87', 'mpaCells': 9524.0, 'mpaValue': '73415.79', 'species': u'California Halibut', 'home_type': u'Port', 'srValue': '80381.20', 'srArea': '261.68'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 19943, 'srPercOverallValue': '97.13', 'mpaArea': '142.59', 'user_grp': u'Commercial', 'srCells': 17870, 'totalValue': '100000.00', 'totalArea': '481.25', 'mpa_id': 2949, 'mpaPercSrValue': '37.60', 'mpaPercSrArea': '33.07', 'srPercOverallArea': '89.61', 'mpaPercOverallValue': '36.52', 'mpaPercOverallArea': '29.63', 'mpaCells': 5909.0, 'mpaValue': '36520.49', 'species': u'Lobster', 'home_type': u'Port', 'srValue': '97134.02', 'srArea': '431.23'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 3991, 'srPercOverallValue': '99.69', 'mpaArea': '30.84', 'user_grp': u'Commercial', 'srCells': 3984, 'totalValue': '100000.00', 'totalArea': '96.31', 'mpa_id': 2949, 'mpaPercSrValue': '23.04', 'mpaPercSrArea': '32.08', 'srPercOverallArea': '99.82', 'mpaPercOverallValue': '22.97', 'mpaPercOverallArea': '32.02', 'mpaCells': 1278.0, 'mpaValue': '22966.37', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99689.65', 'srArea': '96.14'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12979, 'srPercOverallValue': '99.24', 'mpaArea': '44.59', 'user_grp': u'Commercial', 'srCells': 12915, 'totalValue': '100000.00', 'totalArea': '313.20', 'mpa_id': 2949, 'mpaPercSrValue': '6.07', 'mpaPercSrArea': '14.31', 'srPercOverallArea': '99.51', 'mpaPercOverallValue': '6.02', 'mpaPercOverallArea': '14.24', 'mpaCells': 1848.0, 'mpaValue': '6020.58', 'species': u'Nearshore Fishery', 'home_type': u'Port', 'srValue': '99243.44', 'srArea': '311.66'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 12978, 'srPercOverallValue': '95.91', 'mpaArea': '133.04', 'user_grp': u'Commercial', 'srCells': 12251, 'totalValue': '100000.00', 'totalArea': '313.18', 'mpa_id': 2949, 'mpaPercSrValue': '51.96', 'mpaPercSrArea': '45.00', 'srPercOverallArea': '94.40', 'mpaPercOverallValue': '49.83', 'mpaPercOverallArea': '42.48', 'mpaCells': 5513.0, 'mpaValue': '49830.35', 'species': u'Rock Crab', 'home_type': u'Port', 'srValue': '95905.80', 'srArea': '295.63'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 8177, 'srPercOverallValue': '99.30', 'mpaArea': '27.17', 'user_grp': u'Commercial', 'srCells': 8131, 'totalValue': '100013.82', 'totalArea': '197.32', 'mpa_id': 2949, 'mpaPercSrValue': '8.10', 'mpaPercSrArea': '13.85', 'srPercOverallArea': '99.44', 'mpaPercOverallValue': '8.04', 'mpaPercOverallArea': '13.77', 'mpaCells': 1126.0, 'mpaValue': '8040.01', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '99316.73', 'srArea': '196.21'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 29015, 'srPercOverallValue': '43.11', 'mpaArea': '200.07', 'user_grp': u'Commercial', 'srCells': 10223, 'totalValue': '100000.00', 'totalArea': '700.17', 'mpa_id': 2949, 'mpaPercSrValue': '90.93', 'mpaPercSrArea': '81.10', 'srPercOverallArea': '35.23', 'mpaPercOverallValue': '39.20', 'mpaPercOverallArea': '28.57', 'mpaCells': 8291.0, 'mpaValue': '39198.96', 'species': u'Sea Cucumber', 'home_type': u'Port', 'srValue': '43110.29', 'srArea': '246.70'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 2620, 'srPercOverallValue': '31.84', 'mpaArea': '8.20', 'user_grp': u'Commercial', 'srCells': 673, 'totalValue': '100000.00', 'totalArea': '63.22', 'mpa_id': 2949, 'mpaPercSrValue': '68.40', 'mpaPercSrArea': '50.52', 'srPercOverallArea': '25.69', 'mpaPercOverallValue': '21.78', 'mpaPercOverallArea': '12.98', 'mpaCells': 340.0, 'mpaValue': '21782.13', 'species': u'Spot Prawn', 'home_type': u'Port', 'srValue': '31843.52', 'srArea': '16.24'}, {'port': u'Santa Barbara', 'area_units': 'square miles', 'array_id': None, 'totalCells': 11151, 'srPercOverallValue': '99.56', 'mpaArea': '87.26', 'user_grp': u'Commercial', 'srCells': 11109, 'totalValue': '100000.00', 'totalArea': '269.09', 'mpa_id': 2949, 'mpaPercSrValue': '5.07', 'mpaPercSrArea': '32.55', 'srPercOverallArea': '99.62', 'mpaPercOverallValue': '5.05', 'mpaPercOverallArea': '32.43', 'mpaCells': 3616.0, 'mpaValue': '5049.70', 'species': u'Urchin', 'home_type': u'Port', 'srValue': '99557.05', 'srArea': '268.08'}]]

    return render_to_response('fishery_impacts.html', RequestContext(request, {'mpa':mpa, 'all_results': all_results}))
