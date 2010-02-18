from django.template.defaultfilters import slugify
from lingcod.straightline_spacing.models import *
import lingcod.intersection.views as int_views
import xlwt

def spacing_workbook(in_dict, ws_title):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('spacing_matrix')
    ws = spacing_worksheet(in_dict, ws_title,ws)
    return wb
    
def spacing_worksheet(in_dict,ws_title,ws):
    results = distance_matrix_and_labels(in_dict)
    label_list = results['labels']
    dist_mat = results['matrix']
    current_row = 0
    # put the title at the top
    if ws_title is not None:
        ws.row(current_row).write(0,unicode(ws_title))
        current_row += 2
    
    # write the header labels row across the top
    for i,lab in enumerate(label_list):
        ws.row(current_row).write(i+1,unicode(lab) )
    current_row += 1
    
    # write the rest of the matrix
    for i,row in enumerate(dist_mat):
        # write the label in the first column
        ws.row(current_row).write(0,unicode(label_list[i]))
        # write the distance values
        for x,distance in enumerate(row):
            ws.row(current_row).write(x+1,distance)
        current_row += 1
    return ws