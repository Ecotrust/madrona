import numpy as np
#Take a list of numeric values and return a dictionary that translates those
#values to hex colors for use in the generation of kml that's styled to
#sybolize values.

def convert_to_color_ramp(the_list,base_color='green',alpha=0.5):
    # kml color format: aabbggrr
    # change the alpha to a hex value
    hex_alpha = hex(int(alpha*255))[2:]
    min = np.min(the_list)
    max = np.max(the_list)
    # transform the list into a range of color values
    def color_int(x): return int(((x-min)/(max-min))*255)
    color_int_list = map(color_int,the_list)
    def hex_string(x):
        if x==0:
            return '00'
        else:
            return hex(x)[2:]
    hex_mapped = map(hex_string,color_int_list)
    if base_color=='green':
        def green(hex_num): return '%s00%s00' % ( str(hex_alpha),str(hex_num) )
        color_hex_list = [ green(x) for x in hex_mapped ]
    return dict(zip(the_list,color_hex_list))