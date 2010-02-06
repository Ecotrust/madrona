from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Max,Min
from django.utils.dateformat import format
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti
import lingcod.intersection.models as int_models
import lingcod.intersection.views as int_views
import lingcod.depth_range.models as depth_range
import mlpa.models as mlpa
from django.template.defaultfilters import slugify
import xlwt
#import django.contrib.gis.geos

from django.conf import settings
from django.utils.simplejson import dumps as json_encode

def load_study_region_totals(org_scheme):
    """
    This is unfinished.  Don't call it.  You'll be dissapointed.
    """
    sr = mlpa.StudyRegion.objects.current()
    est = mlpa.Estuaries.objects.all()
    sr_results = org_scheme.transformed_results(sr.geometry)
    est_results = org_scheme.transformed_results(est.multipolygon_clipped)

def max_str_length_in_list(list):
    max_len = 0
    for item in list:
        if item.__class__.__name__!='str':
            item = str(item)
        if len(item) > max_len:
            max_len = len(item)
    return max_len

def array_summary_excel_worksheet(array,ws):
    by_desig = array.summary_by_designation
    title_style = xlwt.easyxf('font: bold true;')
    heading_row_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true; borders: left hair, right hair, top hair, bottom medium;')
    area_style = xlwt.easyxf('alignment: horizontal center; borders: left hair, right hair, bottom hair, top hair;',num_format_str='#,##0.00')
    percent_style = xlwt.easyxf('alignment: horizontal center; borders: left hair, right hair, bottom hair, top hair;',num_format_str='0.0%')
    count_style = xlwt.easyxf('alignment: horizontal center; borders: left hair, right hair, bottom hair, top hair;',num_format_str='0')
    style_dict = {'count': count_style, 'area': area_style, 'percent_of_sr': percent_style, 'designation': count_style, 'lop': count_style }
    # create a title row
    current_row = 0
    page_title = 'Summary for %s as of %s' % (array.name,format(array.date_modified,"M d, Y"))
    ws.write_merge(current_row,current_row,0,3,page_title,title_style)
    current_row += 2
    ws.write_merge(current_row,current_row,0,3,'Summary of MPAs by Designation',title_style)
    current_row += 1
    desig_header_list = ['Designation Type', '# of MPAs','Area','Percent of Study Region']
    for i,header in enumerate(desig_header_list):
        ws.col(i).width = 256 * (len(header) + 4)
        ws.row(current_row).write(i,header,heading_row_style)
    current_row += 1
    # write the data for this table
    for key,sub_dict in by_desig.iteritems():
        # god damned Excel automatically multiplies by 100 when you format something as a percentage
        sub_dict['percent_of_sr'] = sub_dict['percent_of_sr'] / 100
        for col,v in dict(zip(range(0,4),['designation','count','area','percent_of_sr'])).iteritems():
            if not sub_dict[v]:
                out_value = 'Undesignated'
            else:
                out_value = sub_dict[v]
            ws.row(current_row).write(col,out_value,style_dict[v])
        current_row += 1
    # make a bit of space
    current_row += 2
    
    # create a title row
    ws.write_merge(current_row,current_row,0,3,'Summary of MPAs by Level of Protection',title_style)
    current_row += 1
    # make second header row
    lop_header_list = ['LOP', '# of MPAs','Area','Percent of Study Region']
    for i,header in enumerate(lop_header_list):
        ws.row(current_row).write(i,header,heading_row_style)
    current_row += 1
    by_lop = array.summary_by_lop
    for sub_dict in by_lop:
        # god damned Excel automatically multiplies by 100 when you format something as a percentage
        sub_dict['percent_of_sr'] = sub_dict['percent_of_sr'] / 100
        for col,v in dict( zip( range(0,4), ['lop','count','area','percent_of_sr'] )).iteritems():
            if sub_dict[v].__class__.__name__ == 'str':
                out_value = sub_dict[v].title()
            else:
                out_value = sub_dict[v]
            ws.row(current_row).write(col,out_value,style_dict[v])
        current_row += 1
    return ws
    
def array_attributes_excel_worksheet(array,ws):
    headings = ['MPA Name','MPA ID','Bioregion','MPA Boundaries (Exact or Approximate)','Designation','Level of Protection','Proposed Take Regulations',
    'Other Proposed Regulations','Regional Goals/Objectives','Site Specific Rationale','Other Considerations']
    heading_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true; borders: left hair, right hair, top hair, bottom hair')
    title_style = xlwt.easyxf('font: bold true;')
    cen = xlwt.easyxf('alignment: horizontal center, vertical top, wrap true; borders: left hair, right hair, top hair, bottom hair', num_format_str='0')
    lef = xlwt.easyxf('alignment: horizontal left, vertical top, wrap true; borders: left hair, right hair, top hair, bottom hair', num_format_str='0')
    data_style_list = [cen,cen,cen,lef,cen,cen,lef,lef,lef,lef,lef]
    wide = 256 * 30
    narrow = 256 * 16
    width_list = [wide,narrow,narrow,wide,narrow,narrow,wide,wide,wide,wide,wide]
    heading_dict = dict( zip( headings, width_list ))
    current_row = 0
    page_title = 'MPA Attributes for %s as of %s' % (array.name,format(array.date_modified,"M d, Y"))
    ws.write_merge(current_row,current_row,0,3,page_title,title_style)
    current_row += 2
    current_col = 0
    for heading in headings:
        ws.col(current_col).width = heading_dict[heading]
        ws.row(current_row).write(current_col,heading,heading_style)
        current_col += 1
    current_row += 1
    for mpa in array.mpa_set.all():
        mpa_lop = mpa.lop
        if mpa_lop:
            lop_name = mpa_lop.name
        else:
            lop_name = 'N/A'
        mdl = [mpa.name]
        mdl.append(mpa.pk)
        mdl.append(mpa.bioregion.name)
        mdl.append(mpa.boundary_description)
        if mpa.designation:
            mdl.append(mpa.designation.acronym)
        else:
            mdl.append('Undesignated')
        mdl.append(lop_name)
        mdl.append(mpa.get_allowed_uses_text()) #'Proposed Take Regulations',
        mdl.append('Allowed Uses: ' + mpa.other_allowed_uses + '\n' + 'Regulated Activities: ' + mpa.other_regulated_activities) #'Other Proposed Regulations',
        mdl.append(mpa.short_g_o_str(really_short=True))    #'Regional Goals/Objectives',
        mdl.append(mpa.specific_objective)    #'Site Specific Rationale',
        mdl.append('')              #'Other Considerations'
        for i,thing in enumerate(mdl):
            ws.row(current_row).write(i,str(thing),data_style_list[i])
        current_row += 1
    return ws
        
def array_habitat_excel_worksheet(array,ws):
    osc = int_models.OrganizationScheme.objects.get(name='excelhabitat')
    habinfo = osc.info['feature_info']
    heading_column_style = xlwt.easyxf('font: bold true;')
    heading_row_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true;')
    data_style = xlwt.easyxf('alignment: horizontal center;',num_format_str='#,##0.00')
    mpa_id_style = xlwt.easyxf('alignment: horizontal center;',num_format_str='0')
    column_width = 256 * 16 # 256 is the width of the '0' character so this is essentially 16 zeros wide    
    ws.panes_frozen = True
    ws.horz_split_pos = 1
    ws.vert_split_pos = 3
    # 0,0 is blank.  first column will start at 0,1.  second column will start at 1,1 so we don't overwrite the heading
    first_column = ['MPA ID','MPA Designation','Level of Protection','SAT Evaluation Bioregion','Area','Alongshore Span','Min Depth','Max Depth','Estuary']
    second_column = ['','','','','sq miles','miles','feet','feet','sq miles']
    # find the longest string in the first column so we can set the width
    whole_first_column = first_column + [ sub['name'] for sub in habinfo.values() ]
    max_len = max_str_length_in_list(whole_first_column) # I'll use this to figure out the width of the first column
        
    # header row will start at 0,0 (blank) and go across
    header_row = ['','How Measured','Total Available Habitat']
    # write first column static stuff (headings)
    first_column_row = 1
    for item in first_column:
        ws.col(0).width = 256 * max_len # set the width wide enough to accomodate the longest heading
        ws.write(first_column_row,0,item,heading_column_style)
        first_column_row += 1
    # write second column static values
    second_column_row = 1 # start at 1 so we don't overwrite the heading
    for item in second_column:
        ws.col(1).width = 256 * 10
        ws.write(second_column_row,1,item,data_style)
        second_column_row += 1
    # at this point we should be at the same row with the first and second column.  If we're not, something is wrong.
    assert (first_column_row==second_column_row), "There was a problem writing the static portion of the array habitat excel worksheet.  Please report this problem.  Sorry about that."
    # calculate values for the study region totals for Area, Min Depth, Max Depth, and Estuary
    sr_area = mlpa.StudyRegion.objects.current().area_sq_mi
    along_shore_span = 'NA'
    min_depth = 0
    max_depth = depth_range.DepthSounding.objects.aggregate(Max('depth_ft'))['depth_ft__max']
    estuary_area = mlpa.Estuaries.objects.total_area_sq_mi
    available_hab_results = [sr_area,along_shore_span,min_depth,max_depth,estuary_area]
    start_at_row = 5
    # put this in a dict to make the next loop easier
    available_hab_dict = {}
    for item in available_hab_results:
        available_hab_dict.update( {start_at_row:item} ) 
        start_at_row += 1
        
    # write this stuff in the right cells
    for row_num, value in available_hab_dict.iteritems():        
        ws.write(row_num,2,value,data_style)
    
    # write first column habitat names and write the units and study region totals while we're at it
    for sub_dict in habinfo.values():
        ws.write(first_column_row,0,sub_dict['name'],heading_column_style)
        ws.write(first_column_row,1,sub_dict['units'],data_style)
        ws.col(2).width = column_width
        ws.write(first_column_row,2,sub_dict['study_region_total'],data_style)
        first_column_row += 1
    # write header row static stuff
    col_num = 0
    for item in header_row:
        if item=='':
            ws.row(0).write(col_num,item,xlwt.easyxf('font: height 700;'))
        else:
            ws.row(0).write(col_num,item,heading_row_style)
        col_num += 1
    # write full columns for each MPA in the array
    for mpa in array.mpa_set.all():
        # start with the stuff that does not come from the intersection results
        d_range = mpa.depth_range
        if mpa.is_estuary:
            est_area = mpa.area_sq_mi
        else:
            est_area = 0.0
        mpa_data = []
        mpa_data.append(mpa.name)                      # mpa name
        mpa_data.append(mpa.pk)                        # mpa id
        mpa_data.append(mpa.designation.acronym)       # mpa designation
        mpa_data.append(mpa.lop.name.title())          # level of protection
        mpa_data.append(mpa.bioregion.name.title())    # sat evaluation bioregion
        mpa_data.append(mpa.area_sq_mi)                # area
        mpa_data.append('')                            # alongshore span (to be entered by hand ...for no apparent reason)
        mpa_data.append(d_range['min'])                # min depth
        mpa_data.append(d_range['max'])                # max depth
        mpa_data.append(est_area)                      # estuary
        
        # get the hab results
        hab_results = int_models.use_sort_as_key(osc.transformed_results(mpa.geometry_final))
        for result in hab_results.values():
            mpa_data.append(result['result'])
        
        # set column width
        ws.col(col_num).width = 256 * max_str_length_in_list(mpa_data)
            
        # write this crap to a column:
        for i,md in enumerate(mpa_data):
            if i == 0:
                ws.write(i,col_num,md,heading_row_style)
            elif i == 1:
                ws.write(i,col_num,md,mpa_id_style)
            else:
                ws.write(i,col_num,md,data_style)
        col_num += 1
            
    
    return ws
    
def array_habitat_excel(request, array_id):
    array = mlpa.MpaArray.objects.get(pk=array_id)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(slugify(array.name[0:30]))
    ws = array_habitat_excel_worksheet(array,ws)
    response = int_views.build_excel_response(slugify(array.name[0:10]),wb)
    return response
    
def array_list_habitat_excel(request, array_id_list_str):
    array_set = mlpa.MpaArray.objects.filter(pk__in=array_id_list_str.split(',') )
    wb = xlwt.Workbook(encoding='utf-8')
    if array_set.count()==1:
        wb_name = array_set[0].name[:10]
    else:
        wb_name = 'MLPA_Arrays'
    for array in array_set:
        ws = wb.add_sheet(slugify(array.name[0:30]))
        ws = array_habitat_excel_worksheet(array,ws)
        
    response = int_views.build_excel_response(slugify(wb_name),wb)
    return response


def mpa_habitat_representation(request, mpa_id, format='json', with_geometries=False, with_kml=False):
    mpa = mlpa.MlpaMpa.objects.get(pk=mpa_id)
    geom = mpa.geometry_final
    if mpa.is_estuary is None:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
    elif mpa.is_estuary:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE)
    else:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
        
    result = org_sch.transformed_results(geom,with_geometries,with_kml)
    if format=='csv':
        return int_views.build_csv_response(result, slugify(mpa.name) )
    elif format=='json':
        return HttpResponse(json_encode(result), mimetype='text/json')
    elif format=='html':
        template = 'mpa_representation_panel.html'
        return render_to_response(template, {'result': int_models.use_sort_as_key(result)}, context_instance=RequestContext(request) )
    # I was going to try and make this interface with the intersection app through urls so that
    # the intersection app could be on a different server but that's not working out and I'm in 
    # a hurry.
    # redirect_url = '/intersection/%s/%s/%s/' % (org_scheme_name,format,str(geom_wkt))
    # return HttpResponseRedirect(redirect_url)

def oc_or_est(results,oc_keys,est_keys):
    """
    labels each result as from estuaries, open coast, or combined
    """
    for hab,sub_dict in results.iteritems():
        if hab in oc_keys and hab in est_keys:
            sub_dict.update({'from':'Combined'})
        elif hab in oc_keys:
            sub_dict.update({'from':'Open Coast'})
        else:
            sub_dict.update({'from':'Estuarine'})
    return results

def oc_or_est_from_org_scheme(results):
    for hab,sub_dict in results.iteritems():
        for k,v in sub_dict.iteritems():
            if k == 'org_scheme_id':
                if v==int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE).pk:
                    new_part = {'from':'Estuaries'}
                elif v==int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST).pk:
                    new_part = {'from':'Open Coast'}
        sub_dict.update(new_part)
    return results

def geometries_to_wkt(results,srid=None, simplify=None):
    """
    Take a dictionary, find values that are geometry objects and replace them with wkt representations of the geometries.
    """
    geometry_classes = ['GeometryCollection','MultiPolygon','Polygon','MultiLineString','LineString','MultiPoint','Point']
    for k,v in results.iteritems():
        if v.__class__.__name__ in geometry_classes:
            new_geom = v
            if simplify:
                #print str(v.num_points) + ': ',
                v = v.simplify(simplify,True)
                #print str(v.num_points)
            if srid:
                v.set_srid(settings.GEOMETRY_DB_SRID)
                v.transform(srid)
            results[k] = v.wkt
        elif v.__class__.__name__=='dict':
            v.update(geometries_to_wkt(v,srid,simplify))
    return results

def array_summary_excel(request, array_id_list_str):
    array_set = mlpa.MpaArray.objects.filter(pk__in=array_id_list_str.split(',') )
    wb = xlwt.Workbook(encoding='utf-8')
    if array_set.count()==1:
        wb_name = array_set[0].name[:10]
    else:
        wb_name = 'MLPA_Array_Summaries'
    for array in array_set:
        ws = wb.add_sheet(slugify(array.name[0:26] + '_att'))
        ws = array_attributes_excel_worksheet(array,ws)
        ws = wb.add_sheet(slugify(array.name[0:26] + '_sum'))
        ws = array_summary_excel_worksheet(array,ws)

    response = int_views.build_excel_response(slugify(wb_name),wb)
    return response

def array_summary(request, array_id, format='excel'):
    array = mlpa.MpaArray.objects.get(pk=array_id)
    by_desig = array.summary_by_designation
    
    if format=='html':
        template = 'array_summary_panel.html'
        return render_to_response(template, {'array': array, 'desig_dict': by_desig }, context_instance=RequestContext(request) )
        

def array_habitat_replication(request, array_id, format='html'):
    array = mlpa.MpaArray.objects.get(pk=array_id)
    if format=='html':
        template = 'array_replication_panel.html'
    elif format=='print':
        template = 'array_replication_page_print.html'
    return render_to_response(template, {'results': array.clusters_with_habitat, 'array': array}, context_instance=RequestContext(request) )
            
def array_habitat_representation_summed(request, array_id, format='json', with_geometries=False, with_kml=False, oc_est_combined=False):
    if format != 'json':
        with_geometries = False
        with_kml = False
    array = mlpa.MpaArray.objects.get(pk=array_id)
    oc_gc = array.opencoast_geometry_collection
    est_gc = array.estuarine_geometry_collection
    oc_org = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
    est_org = int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE)
    oc_results = oc_org.transformed_results(oc_gc,with_geometries,with_kml)
    est_results = est_org.transformed_results(est_gc,with_geometries,with_kml)
    oc_keys = oc_results.keys()
    est_keys = est_results.keys()
    if oc_est_combined:
        all_results = [oc_results,est_results]
        results = int_models.sum_results(all_results)
        results = oc_or_est(results,oc_keys,est_keys)
        results = geometries_to_wkt(results)
    elif not oc_est_combined and format=='json':
        oc_results = geometries_to_wkt(oc_results)
        est_results = geometries_to_wkt(est_results)
        results = { settings.SAT_OPEN_COAST: oc_results, settings.SAT_ESTUARINE: est_results }
    elif not oc_est_combined and format=='csv':
        return int_views.build_array_mpa_csv_response([oc_or_est_from_org_scheme(oc_results), oc_or_est_from_org_scheme(est_results)], slugify(array.name), array.name, 'array' )
        
    if format=='json':
        return HttpResponse(json_encode(results), mimetype='text/json')
    elif format=='csv':
        return int_views.build_csv_response(results, slugify(array.name) )
    