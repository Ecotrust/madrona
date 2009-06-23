from elementtree import ElementTree as et
import os

ROOT_PATH = ''

def get_js_files():
    """Returns a list of all the javascript files listed in 
    media/common/js/includes.xml"""
    files = []
    path = os.path.dirname(os.path.abspath(__file__))
    tree = et.parse(path+'/../../media/js_includes.xml')
    for f in tree.findall('file'):
        files.append(ROOT_PATH + f.get('path'))
    return files
    
def get_js_test_files():
    """Returns a list of all the javascript test files listed in 
    media/common/js/includes.xml"""
    files = []
    path = os.path.dirname(os.path.abspath(__file__))
    tree = et.parse(path+'/../../media/js_includes.xml')
    for f in tree.findall('test'):
        files.append(ROOT_PATH + f.get('path'))
    return files
    
def get_css_files():
    """Returns a list of all css files listed in 
    media/common/css/includes.xml"""
    files = []
    path = os.path.dirname(os.path.abspath(__file__))
    tree = et.parse(path+'/../../media/css_includes.xml')
    for f in tree.findall('file'):
        files.append(ROOT_PATH + f.get('path'))
    return files
