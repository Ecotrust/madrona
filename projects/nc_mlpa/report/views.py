from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Max,Min
from django.utils.dateformat import format
from lingcod.common import mimetypes, utils
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti
import lingcod.intersection.models as int_models
import lingcod.intersection.views as int_views
from lingcod.sharing.utils import *
from lingcod.spacing.views import *
from lingcod.spacing.models import Land, SpacingPoint, fish_distance, sorted_points_and_labels
import lingcod.depth_range.models as depth_range
import mlpa.models as mlpa
from report.models import *
from lingcod.shapes.views import ShpResponder
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
    
def replication_habitats():
    """
    Return a queryset containing organization scheme feature mappings that represent
    all the habitats that are supposed to have replication analysis performed on them.
    """
    org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST_REPLICATION)
    return org_sch.featuremapping_set.all()
    
def array_spacing_report(request, array_id, format='html'):
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    #array = mlpa.MpaArray.objects.get(pk=array_id)
    if format=='html':
        template = 'array_spacing_panel.html'
    return render_to_response(template, {'array': array, 'session_key': request.session.session_key}, context_instance=RequestContext(request) )

def array_spacing_kml(request,array_id,lop_value,session_key,use_centroids=False):
    array_class = utils.get_array_class()
    load_session(request, session_key)
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    lop = mlpa.Lop.objects.get(value=lop_value)
    clusters = array.clusters_with_habitat.filter(lop=lop)
    cluster_points = []
    # Test to make sure cluster centroids don't fall on the land polygon.  I doubt they ever will but 
    # spacing won't work if they do.
    for cl in clusters:
        if True in [ l.geometry.contains(cl.geometry_collection.centroid) for l in Land.objects.all() ]:
            raise Exception('One of the cluster centroids is on land.  I can not work out the spacing.')
    habitats = replication_habitats()
    doc_title = "Spacing for %s at %s LOP" % (array.name,lop.name.title())
    document = { 'name': doc_title, 'folders': [] }
    for hab in habitats:
        # Make a kml folder dictionary to work with the kml template
        folder_title = "%s Replicates and Gaps" % hab.name.title()
        folder = { 'name': folder_title, 'placemarks': [] }
        # Find the cluster habitat info objects for this hab that qualify as replicates
        chis = ClusterHabitatInfo.objects.filter(cluster__in=clusters,habitat=hab,replicate=True)
        # Get the clusters attatched to those Habitat Info objects
        hab_rep_clusters = [ chi.cluster for chi in chis ]
        # Make a dict to hold the points and names that we need spacing paths for
        points_and_names = {}
        # Include the SpacingPoints for north and south ends
        [ points_and_names.update({ s.geometry: s.name }) for s in SpacingPoint.objects.all() ]
        if use_centroids:
            # Add in the centroids and names for the clusters
            [ points_and_names.update({ c.geometry_collection.centroid: c.name }) for c in hab_rep_clusters ]
        else:
            # Add in the actual cluster geom collections
            [ points_and_names.update({ c.geometry_collection: c.name }) for c in hab_rep_clusters ]
        # Make sure all the points have their srid assigned so they can be transformed
        for p in points_and_names.keys():
            if p.srid == None:
                p.srid = settings.GEOMETRY_DB_SRID
        # Sort those points and names from North to South
        sorted_dict = sorted_points_and_labels(points_and_names)
        points = sorted_dict['points']
        #print [ "(" + str(p.x) + "," + str(p.y) + "), " for p in points ]
        names = sorted_dict['labels']
        # Get the fish distance line kmls between these clusters
        # if use_centroids==False, 'points' aren't actually points in this next for loop.
        # They are whatever type of geometry was passed in.  Anything should work, including
        # geometry collections.
        for i in range(0,len(points)-1):
            distance, line = fish_distance_from_edges(points[i],points[i+1])
            line.srid = settings.GEOMETRY_DB_SRID
            line.transform(settings.GEOMETRY_CLIENT_SRID)
            line_name = "%.1f mile %s Gap" % (distance, hab.name.title())
            line_description = "%f miles" % distance
            if distance >= 62.0:
                styleurl = '#too_far_map'
            else:
                styleurl = '#close_enough_map'
            geom_collection = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
            geom_collection.extend([line,line.centroid])
            pm = { 'name': line_name, 'description': line_description, 'geometry': geom_collection.kml, 'styleurl': styleurl }
            folder['placemarks'].append(pm)
        for cl in hab_rep_clusters:
            cl_description = 'Cluster of %f sq. miles at %s level of protection that counts as a replicate of %s.' % (cl.area_sq_mi,lop.name,hab.name)
            geom = cl.geometry_collection
            geom.srid = settings.GEOMETRY_DB_SRID
            geom.transform(settings.GEOMETRY_CLIENT_SRID)
            pm = { 'name': cl.name, 'description': cl_description, 'geometry': geom.kml }
            folder['placemarks'].append(pm)
        
        # Add the folder dictionary that we created to the kml document dictionary
        document['folders'].append(folder)
        
    template = 'document.kml'
    t = get_template(template)
    response = HttpResponse(t.render(Context({'document':document})), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'spacing'
    return response # render_to_response(template, {'document':document}, context_instance=RequestContext(request), mimetype='application/vnd.google-earth.kml+xml' )

def array_size_by_lop_worksheet(array,ws):    
    title_style = xlwt.easyxf('font: bold true;')
    heading_row_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true; borders: left thin, right thin, top thin, bottom medium;')
    area_style = xlwt.easyxf('alignment: horizontal center; borders: left thin, right thin, bottom thin, top thin;',num_format_str='#,##0.00')
    all_clusters = array.clusters | array.clusters_at_lowest_lop
    lops = mlpa.Lop.objects.filter(run=True) | mlpa.Lop.objects.filter(value=0)
    current_row = 0
    # Write out the page title
    page_title = 'Cluster Size (Sq Miles) by LOP for %s as of %s' % (array.name,format(array.date_modified,settings.DATETIME_FORMAT))
    ws.write_merge(current_row,current_row,0,4,page_title,title_style)
    current_row += 2
    # Write out the header row containing the LOP names
    for i,lop in enumerate(lops):
        ws.col(i).width = 256 * ( len(lop.name) + 4 )
        ws.row(current_row).write(i,lop.name.title(),heading_row_style)
    current_row += 1
    # Write out the areas for clusters at each LOP
    for i,lop in enumerate(lops):
        for x,cl in enumerate(all_clusters.filter(lop=lop)):
            ws.row(current_row + x).write(i,cl.area_sq_mi,area_style)
    return ws

def array_summary_excel_worksheet(array,ws):
    by_desig = array.summary_by_designation
    title_style = xlwt.easyxf('font: bold true;')
    heading_row_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true; borders: left thin, right thin, top thin, bottom medium;')
    area_style = xlwt.easyxf('alignment: horizontal center; borders: left thin, right thin, bottom thin, top thin;',num_format_str='#,##0.00')
    percent_style = xlwt.easyxf('alignment: horizontal center; borders: left thin, right thin, bottom thin, top thin;',num_format_str='0.0%')
    count_style = xlwt.easyxf('alignment: horizontal center; borders: left thin, right thin, bottom thin, top thin;',num_format_str='0')
    style_dict = {'count': count_style, 'area': area_style, 'percent_of_sr': percent_style, 'designation': count_style, 'lop': count_style }
    # create a title row
    current_row = 0
    page_title = 'Summary for %s as of %s' % (array.name,format(array.date_modified,settings.DATETIME_FORMAT))
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
            if v=='designation' and not sub_dict[v]:
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
            if col == 0:
                out_value = sub_dict[v].title()
            else:
                out_value = sub_dict[v]
            ws.row(current_row).write(col,out_value,style_dict[v])
        current_row += 1
    return ws
    
def array_attributes_excel_worksheet(array,ws):
    """
    MPA ID, Name, Bioregion, Boundary Text, Designation, LOP, Allowed 
    Uses, Other Allowed Uses, Other Regulated Activities, Goals/Objectives, Site-Specific Rationale, 
    Design Considerations, MPA Evaluation Notes
    """
    ws.panes_frozen = True
    ws.horz_split_pos = 3
    ws.vert_split_pos = 1
    headings = ['MPA Name','MPA ID','Bioregion','MPA Boundaries (Exact or Approximate)','Designation','Level of Protection','Proposed Take Regulations',
    'Other Allowed Uses','Other Proposed Regulations','Regional Goals/Objectives','Site Specific Rationale','Other Considerations',
    'Staff Evolution Notes']
    heading_style = xlwt.easyxf('font: bold true; alignment: horizontal center, wrap true; borders: left thin, right thin, top thin, bottom thin')
    title_style = xlwt.easyxf('font: bold true;')
    cen = xlwt.easyxf('alignment: horizontal center, vertical top, wrap true; borders: left thin, right thin, top thin, bottom thin', num_format_str='0')
    lef = xlwt.easyxf('alignment: horizontal left, vertical top, wrap true; borders: left thin, right thin, top thin, bottom thin', num_format_str='0')
    data_style_list = [cen,cen,cen,lef,cen,cen,lef,lef,lef,lef,lef,lef,lef]
    wide = 256 * 30
    narrow = 256 * 16
    width_list = [wide,narrow,narrow,wide,narrow,narrow,wide,wide,wide,wide,wide,wide,wide]
    heading_dict = dict( zip( headings, width_list ))
    current_row = 0
    page_title = 'MPA Attributes for %s as of %s' % (array.name,format(array.date_modified,settings.DATETIME_FORMAT))
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
            lop_name = mpa_lop.name.title()
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
        mdl.append(mpa.other_allowed_uses) # 'Other Allowed Uses'
        mdl.append(mpa.other_regulated_activities) #'Other Proposed Regulations',
        mdl.append(mpa.short_g_o_str(really_short=True))    #'Regional Goals/Objectives',
        mdl.append(mpa.specific_objective)    #'Site Specific Rationale',
        mdl.append(mpa.design_considerations)      #'Other Considerations'
        mdl.append(mpa.evolution)          # 'Staff Evolution Notes'
        for i,thing in enumerate(mdl):
            ws.row(current_row).write(i,unicode(thing),data_style_list[i])
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
    min_depth, max_depth = depth_range.total_depth_range()
    # Check for nulls and replace with N/A.  This'll happen if the MPA is in an area with no depth soundings, like an estuary.
    min_depth = min_depth if min_depth is not None else 'N/A'
    max_depth = max_depth if max_depth is not None else 'N/A'
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
    for key,sub_dict in sorted( habinfo.iteritems() ):
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
        for k,v in d_range.iteritems():
            v = v if v is not None else 'N/A'
            d_range[k] = v
        if mpa.is_estuary:
            est_area = mpa.area_sq_mi
        else:
            est_area = 0.0
        mpa_data = []
        mpa_data.append(mpa.name)                      # mpa name
        mpa_data.append(mpa.pk)                        # mpa id
        if mpa.designation:
            mpa_data.append(mpa.designation.acronym)       # mpa designation
        else:
            mpa_data.append('Undesignated')
        if mpa.lop:
            mpa_data.append(mpa.lop.name.title())          # level of protection
        else:
            mpa_data.append('N/A')
        mpa_data.append(mpa.bioregion.name.title())    # sat evaluation bioregion
        mpa_data.append(mpa.area_sq_mi)                # area
        mpa_data.append('')                            # alongshore span (to be entered by hand ...for no apparent reason)
        mpa_data.append(d_range['min'])                # min depth
        mpa_data.append(d_range['max'])                # max depth
        mpa_data.append(est_area)                      # estuary
        
        # get the hab results
        hab_results = int_models.use_sort_as_key(osc.transformed_results(mpa.geometry_final))
        for key,result in sorted( hab_results.iteritems() ):
            # can use this commented line below to make sure habitat types are lining up with labels
            # mpa_data.append(result['name'] + ': ' + str(result['result']))
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

def array_cluster_spacing_excel(request, array_id):
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)  # mlpa.MpaArray.objects.get(pk=array_id)
    # get the lowest lop that is used to run replication and clustering
    lop = mlpa.Lop.objects.filter(run=True).order_by('value')[0]
    clusters = array.clusters.filter(lop=lop)
    point_dict = {}
    for cl in clusters:
        point_dict[cl.geometry_collection.centroid] = cl.name
    ws_title = 'MPA Spacing for %s as of %s' % (array.name,format(array.date_modified,settings.DATETIME_FORMAT))
    wb = spacing_workbook(point_dict, ws_title)
    response = int_views.build_excel_response(slugify(array.name[0:10]),wb)
    return response
    
def array_habitat_excel(request, array_id):
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    #array = mlpa.MpaArray.objects.get(pk=array_id)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(slugify(array.name[0:30]))
    ws = array_habitat_excel_worksheet(array,ws)
    response = int_views.build_excel_response(slugify(array.name[0:10]),wb)
    return response
    
def array_list_habitat_excel(request, array_id_list_str):
    array_class = utils.get_array_class()
    array_id_list = array_id_list_str.split(',')
    wb = xlwt.Workbook(encoding='utf-8')
    if array_id_list.__len__()==1:
        wb_name = array_set[0].name[:10]
    else:
        wb_name = 'MLPA_Arrays'
    for array_id in array_id_list:
        array = get_viewable_object_or_respond(array_class,array_id,request.user)
        ws = wb.add_sheet(slugify(array.name[0:30]))
        ws = array_habitat_excel_worksheet(array,ws)
        
    response = int_views.build_excel_response(slugify(wb_name),wb)
    return response
    
def array_summary_excel(request, array_id_list_str):
    #array_set = mlpa.MpaArray.objects.filter(pk__in=array_id_list_str.split(',') )
    array_class = utils.get_array_class()
    array_id_list = array_id_list_str.split(',')
    wb = xlwt.Workbook(encoding='utf-8')
    # if array_id_list.__len__()==1:
    #     wb_name = array_set[0].name[:10]
    # else:
    #     wb_name = 'MLPA_Array_Summaries'
    for array_id in array_id_list:
        array = get_viewable_object_or_respond(array_class,array_id,request.user)
        if array.short_name:
            wb_name = array.short_name
        else:
            wb_name = array.name[:10]
        ws = wb.add_sheet('Attributes') #slugify(array.name[0:26] + '_att'))
        ws = array_attributes_excel_worksheet(array,ws)
        ws = wb.add_sheet('Summary') #slugify(array.name[0:26] + '_sum'))
        ws = array_summary_excel_worksheet(array,ws)
        ws = wb.add_sheet('Habitat') #slugify(array.name[0:26] + '_hab'))
        ws = array_habitat_excel_worksheet(array,ws)
        ws = wb.add_sheet('Spacing') #slugify(array.name[0:26] + '_spa'))
        lop = mlpa.Lop.objects.filter(run=True).order_by('value')[0]
        clusters = array.clusters.filter(lop=lop)
        point_dict = {}
        for cl in clusters:
            point_dict[cl.geometry_collection] = cl.name
        ws_title = 'MPA Spacing for %s as of %s' % (array.name,format(array.date_modified,settings.DATETIME_FORMAT))
        ws = spacing_worksheet(point_dict,ws_title,ws)
        ws = wb.add_sheet('Cluster Size') 
        ws = array_size_by_lop_worksheet(array,ws)

    response = int_views.build_excel_response(slugify(wb_name),wb)
    return response

def array_summary(request, array_id, format='excel'):
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    #array = mlpa.MpaArray.objects.get(pk=array_id)
    by_desig = array.summary_by_designation

    if format=='html':
        template = 'array_summary_panel.html'
        return render_to_response(template, {'array': array, 'desig_dict': by_desig }, context_instance=RequestContext(request) )

def array_habitat_replication(request, array_id, format='html'):
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    #array = mlpa.MpaArray.objects.get(pk=array_id)
    if format=='html':
        template = 'array_replication_panel.html'
    elif format=='print':
        template = 'array_replication_page_print.html'
    return render_to_response(template, {'results': array.clusters_with_habitat.filter(lop__run=True).order_by('lop__value', 'bioregion', '-northing'), 'array': array}, context_instance=RequestContext(request) )

def array_habitat_representation_summed(request, array_id, format='json', with_geometries=False, with_kml=False, oc_est_combined=False):
    if format != 'json':
        with_geometries = False
        with_kml = False
    #array = mlpa.MpaArray.objects.get(pk=array_id)
    array_class = utils.get_array_class()
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
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

def array_shapefile(request, array_id_list_str):
    array_class = utils.get_array_class()
    array_id_list = array_id_list_str.split(',')
    #array_set = mlpa.MpaArray.objects.filter(pk__in=array_id_list_str.split(',') )
    array_id = array_id_list[0] # for now we're only expecting to get one
    array = get_viewable_object_or_respond(array_class,array_id,request.user)
    if array.short_name:
        file_name = array.short_name
    else:
        file_name = array.name[0:8]
    shp_response = ShpResponder(array.shapefile_export_query_set)
    shp_response.file_name = slugify(file_name)
    return shp_response()
    
def mpa_shapefile(request, mpa_id_list_str):
    mpa_class = utils.get_mpa_class()
    mpa_id_list = mpa_id_list_str.split(',')
    mpa_id = mpa_id_list[0] # only expecting one for now
    mpa = get_viewable_object_or_respond(mpa_class,mpa_id,request.user)
    shp_response = ShpResponder(mpa.export_query_set)
    shp_response.file_name = slugify(mpa.name[0:8])
    return shp_response()

def mpa_habitat_representation(request, mpa_id, format='json', with_geometries=False, with_kml=False):
    mpa_class = utils.get_mpa_class()
    mpa = get_viewable_object_or_respond(mpa_class,mpa_id,request.user)
    #mpa = mlpa.MlpaMpa.objects.get(pk=mpa_id)
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
        return render_to_response(template, {'json': json_encode(result), 'result': int_models.use_sort_as_key(result)}, context_instance=RequestContext(request) )
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
