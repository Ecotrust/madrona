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
        return display_mpa_analysis(request, feature_id, group_name)
    else:
        #the following port and species parameters are for testing on my local machine
        #return display_array_analysis(request, feature_id, group_name, port='Eureka', species='Salmon')
        return display_array_analysis(request, feature_id, group_name)


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
    #Sum results for each species, for each mpa in the array
    #What to do if mpa_analysis_results returns a Response object instead of a result?
    for mpa in mpas:
        if mpa.designation_id is not None: #ignore Stewardship Zones and other mpas that have no LOP
            mpa_results = mpa_analysis_results(mpa, group, port, species)
            array_results.append(mpa_results)
    
    #what to do if the following throws an exception/error?
    #could happen if array_results is empty (no mpas with lops for example)
    analysis_results = aggregate_array_results(array, array_results, group, port, species)
    
    return render_to_response(template, RequestContext(request, {'array':array, 'array_results': analysis_results}))  

    
def aggregate_array_results(array, array_results, group, port, species):
    analysis_results = []
    if group == 'Commercial':
        aggregated_results = aggregate_com_array_results(array_results)
        for species, results in aggregated_results.iteritems():
            analysis_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
        #sort results by species name (alphabetically)
        analysis_results = sort_results_by_species(analysis_results)
        analysis_results = roundPercentageValues(analysis_results, 1)
    elif group == 'Commercial Passenger Fishing Vessel':
        aggregated_results = aggregate_cpfv_array_results(array_results)
        for port, results in aggregated_results.iteritems():
            analysis_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
        #sort results by port name (north to south)
        analysis_results = sort_results_by_port(analysis_results, group) 
        analysis_results = roundPercentageValues(analysis_results, 1) 
    else:
        aggregated_results = aggregate_rec_array_results(array_results, group)
        for port, dict in aggregated_results.iteritems():
            port_results = []
            for species, results in dict.iteritems():
                port_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
            #sort results by species name (alphabetically)
            port_results = sort_results_by_species(port_results)
            port_results = roundPercentageValues(port_results, 1)  
            analysis_results.append(port_results)
        #sort results by port name (north to south)
        analysis_results = sort_results_by_port(analysis_results, group) 
    return analysis_results

def aggregate_com_array_results(array_results):
    aggregated_array_results = get_empty_array_results_dictionary('Commercial')
    for mpa_results in array_results:
        #why does this have to be index 0?  
        #is there an unneeded list here?
        for result in mpa_results[0]:
            if result.percOverallValue == '---':
                pass
            elif aggregated_array_results[result.species]['Value'] == '---':
                aggregated_array_results[result.species]['Value'] = float(result.percOverallValue)
                aggregated_array_results[result.species]['Area'] = float(result.percOverallArea)
            else:
                aggregated_array_results[result.species]['Value'] += result.percOverallValue
                aggregated_array_results[result.species]['Area'] += result.percOverallArea
    return aggregated_array_results       
        

def aggregate_cpfv_array_results(array_results):
    group = 'Commercial Passenger Fishing Vessel'
    aggregated_array_results = get_empty_array_results_dictionary(group)
    group_ports = GetPortsByGroup(group)
    #sum up the value percentages at each port, keeping track of the number of summations made
    #why does this have to be index 0?  
    #is there an unneeded list here?
    for mpa_results in array_results:
        #port_counts is used for determining average gei% among all relevant species for each port 
        #(will be the same regardless of which mpa results we look at)
        port_counts = dict( (port, 0) for port in group_ports)
        for port_results in mpa_results:
            for result in port_results:
                if result.percOverallValue == '---':
                    pass
                elif aggregated_array_results[result.port]['Value'] == '---':
                    aggregated_array_results[result.port]['Value'] = float(result.percOverallValue)
                    aggregated_array_results[result.port]['Area'] = float(result.percOverallArea)
                    port_counts[result.port] = 1
                else:
                    aggregated_array_results[result.port]['Value'] += result.percOverallValue
                    aggregated_array_results[result.port]['Area'] += result.percOverallArea
                    port_counts[result.port] += 1
    for port in group_ports:
        if aggregated_array_results[port]['Value'] != '---':
            aggregated_array_results[port]['Value'] /= port_counts[port]
    return aggregated_array_results       
    
def aggregate_rec_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    for mpa_results in array_results[0]:
        #why does this have to be index 0?  
        #is there an unneeded list here?
        for result in mpa_results:
            if result.percOverallValue == '---':
                pass
            elif aggregated_array_results[result.port][result.species]['Value'] == '---':
                aggregated_array_results[result.port][result.species]['Value'] = float(result.percOverallValue)
                aggregated_array_results[result.port][result.species]['Area'] = float(result.percOverallArea)
            else:
                aggregated_array_results[result.port][result.species]['Value'] += result.percOverallValue
                aggregated_array_results[result.port][result.species]['Area'] += result.percOverallArea
    return aggregated_array_results       
    
def sort_results_by_species(results):   
    #sort results alphabetically by species name
    results.sort(key=lambda obj: obj.species)  
    return results
    
def sort_results_by_port(results, group):
    #sort results by port name (north to south)
    ports = GetPortsByGroup(group)
    count = 0
    ordering = {}
    for port in ports:
        count += 1
        ordering[port] = count
    if 'Recreational' in group:
        results.sort(lambda x, y : cmp (ordering[x[0].port], ordering[y[0].port])) 
    else: 
        results.sort(lambda x, y : cmp (ordering[x.port], ordering[y.port])) 
    return results
    
    
def get_empty_array_results_dictionary(group):
    group_species = GetSpeciesByGroup(group)
    group_ports = GetPortsByGroup(group)
    initialValue = '---'
    initialArea = '---'
    if group == 'Commercial':
        empty_results = dict( (Layers.COMMERCIAL_SPECIES_DISPLAY[species], {'Value':initialValue, 'Area':initialArea}) for species in group_species)
    elif group == 'Commercial Passenger Fishing Vessel':
        empty_results = dict( (port, {'Value':initialValue, 'Area':initialArea}) for port in group_ports)
    else:
        empty_results = dict( (port, dict( (species, {'Value':initialValue, 'Area':initialArea}) for species in group_species)) for port in group_ports) 
    return empty_results
  
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
        for port_results in mpa_results:
            port_results = roundPercentageValues(port_results, 1)
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
        port_results = []
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
                port_results.append(AnalysisResult(id=result.mpa_id, type='mpa', group=group, port=single_port, species=result.species, percOverallArea=result.perc_area, percOverallValue=result.perc_value))
        else: 
            #since at least one cache was not current, remove all related entries as they will all be recreated and recached below
            for single_cache in cache:
                single_cache.delete()
            #Get all maps from the group and port (and possibly species) that we want to analyze
            maps = FishingImpactAnalysisMap.objects.getSubset(group, single_port, species)
            #WILL THIS SOMETIMES BE EMPTY?
            #AND IF SO, SHOULD THIS BE ALLOWED (I'M SEEING EMPTY RIGHT NOW WITH EUREKA SALMON ON DIV) -- RETURNS [] (NOT '')
            #IF IT'S ALLOWED, WE CAN SIMPLY COUCH THE REST OF THIS ELSE IN AN IF LEN(MAPS) > 0
            if maps is '':
                return HttpResponseBadRequest('A Fishing Map with User group, %s, Port, %s, and Species, %s, does not exist.' % (group, single_port, species))
            if len(maps) > 0:
                #run the analysis
                analysis = Analysis()
                port_results = analysis.run(mpa, maps)
                if port_results < 0:
                    return HttpResponseBadRequest('Error running analysis')
                #Cache analysis results 
                cache_analysis_results(port_results, group, mpa)
            
        #Expand results to include those species that exist within the group but not perhaps within this port (denoted with '---')
        port_results = flesh_out_results(group, single_port, port_results)

        #sort results alphabetically by species name
        port_results.sort(key=lambda obj: obj.species)
                
        mpa_results.append(port_results)
    return mpa_results
    
def roundPercentageValues(results, sig_digs):
    import utilities as mmutil  
    for result in results:
        if result.type == 'mpa': 
            if result.percOverallValue != '---':
                result.percOverallArea = mmutil.trueRound(float(result.percOverallArea), sig_digs)
                result.percOverallValue = mmutil.trueRound(float(result.percOverallValue), sig_digs)
        else:
            if result.percGEI != '---':
                result.percGEI = mmutil.trueRound(float(result.percGEI), sig_digs)
            if result.percNEI != '---':
                result.percNEI = mmutil.trueRound(float(result.percNEI), sig_digs)
            if result.GEI != '---':
                result.GEI = mmutil.trueRound(float(result.GEI), 0)
            if result.NEI != '---':
                result.NEI = mmutil.trueRound(float(result.NEI), 0)
    return results
    
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
            analysis_results.append(AnalysisResult(id=result.mpa_id, type='mpa', group=user_group, port=single_port, species=result.species, percOverallArea=result.perc_area, percOverallValue=result.perc_value))
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
        cache = FishingImpactResults(mpa_id=mpa.id, group=group, port=result.port, species=result.species, perc_value=result.percOverallValue, perc_area=result.percOverallArea)
        #WHY IS THIS NOT SAVING DURING ARRAY ANALYSIS???
        cache.save()
        
'''
Called by display_mpa_analysis and print_report
Fills out analysis results with species that are relevant for the given group, but not yet present in the results
'''
def flesh_out_results(group, port, results):
    group_species = GetSpeciesByGroup(group)
    result_species = [result.species for result in results]
    missing_species = [specs for specs in group_species if specs not in result_species]
    for spec in missing_species:
        results.append(EmptyAnalysisResult(group, port, spec, 'mpa'))
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

