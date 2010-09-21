from django.shortcuts import get_object_or_404
import mapnik
from lingcod.staticmap.models import MapConfig
from views import process_mapfile_text, get_designation_style, auto_extent

'''
Create map image and save in a temporary location
Return path to temporary location
'''    
def save_to_temp(params, map_name='default'):
    """Saves a map with the study region geometry.  """
    maps = get_object_or_404(MapConfig,mapname=map_name)
    mapfile = str(maps.mapfile.path)
     
    # Grab the image dimensions
    width, height = get_dimensions(maps, params)

    # Create a blank image
    draw = mapnik.Image(width,height)
    m = mapnik.Map(width,height)

    mpas = [int(params['mpas'])]
    
    # Do the variable substitution
    xmltext = process_mapfile_text(mapfile, mpas)
    mapnik.load_map_from_string(m,xmltext)

    # Override the mpa_style according to MPA designations
    s = get_designation_style(mpas)
    m.append_style('mpa_style',s)
     
    # Grab the bounding coordinates 
    x1, y1, x2, y2 = get_bounding_coords(maps, params, mpas)

    bbox = mapnik.Envelope(mapnik.Coord(x1,y1), mapnik.Coord(x2,y2))
    m.zoom_to_box(bbox)
    
    # Render image 
    mapnik.render(m, draw)
    img = draw.tostring('png')

    #generate image in temporary location and return path
    filename = generate_filename(mpas)
    pathname = write_to_temp(filename, img)
    return pathname
    
'''
Called by save_to_temp
'''    
def get_dimensions(maps, params):
    try:
        width = int(params['width'])
        height = int(params['height'])
    except:
        # fall back on defaults
        width, height = maps.default_width, maps.default_height
    return width, height
    
'''
Called by save_to_temp
'''    
def get_bounding_coords(maps, params, mpas):
    # first, assume default image extent
    x1, y1 = maps.default_x1, maps.default_y1
    x2, y2 = maps.default_x2, maps.default_y2
    
    if "autozoom" in params.keys():
        if params['autozoom'].lower() == 'true' and mpas and len(mpas)>0:
            x1, y1, x2, y2 = auto_extent(mpas, maps.default_srid)
    elif "bbox" in params.keys():
        try:
            x1, y1, x2, y2 = [float(x) for x in str(params['bbox']).split(',')]
        except:
            pass
    return x1, y1, x2, y2
    
'''
Called by save_to_temp
'''    
def generate_filename(mpas):
    import datetime
    import random
    randnum = random.randint(0, 1000000000)
    timestamp = datetime.datetime.now().strftime('%m_%d_%y_%H%M')       
    filename = 'mpa'+str(mpas[0])+'_'+timestamp+'_'+str(randnum)+'.png'
    return filename
        
'''
Called by save_to_temp
'''    
def write_to_temp(filename, img):  
    import tempfile
    import os
    pathname = os.path.join(tempfile.gettempdir(),filename)
    temp = open(pathname, 'wb')
    temp.write(img)
    temp.close()  
    return pathname
    
