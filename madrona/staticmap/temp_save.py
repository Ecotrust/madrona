from views import draw_map

'''
Create map image from a parameter dict
'''    
def img_from_params(params, user=None):
    opts = ['uids', 'width', 'height', 'autozoom', 'bbox', 'show_extent']

    class X:
        pass
    x = X()

    for opt in opts:
        try:
            setattr(x,opt,params[opt])
        except:
            setattr(x,opt,False)

    try: 
        x.map_name = params[map_name]
    except:
        x.map_name = 'default'

    # Note:: with user set to None, no perms checking happens 
    # so anything that calls this better make sure
    # that request.user has permissions to view uids!!
    img = draw_map(x.uids.split(','), user, int(x.width), int(x.height), x.autozoom, x.bbox, x.show_extent, x.map_name)
    return img
     
