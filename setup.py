import warnings
import subprocess
import re
import os
import sys

# setuptools messes up `sdist`
# but it works for `develop`
if len(sys.argv) > 1 and sys.argv[1] == 'develop':
    print("using setuptools.setup")
    from setuptools import setup
else:
    print("using distutils.setup")
    from distutils.core import setup

from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

readme_text = open('README.rst', 'r').read()

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('madrona'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

version = __import__('madrona').get_version()

setup_args = {
    'name': 'madrona',
    'version': version,
    'description': 'A software framework for effective place-based decision making',
    'author': 'MarineMap Consortium, Ecotrust',
    'author_email': 'mperry@ecotrust.org',
    'maintainer': 'Ecotrust',
    'maintainer_email': 'ksdev@ecotrust.org',
    'url': 'http://ecotrust.github.com/madrona',
    'license': 'New BSD License',
    'keywords': 'kml marine decisionsupport science gis',
    'long_description': readme_text,
    'packages': packages,
    'data_files': data_files,
    'scripts': [
        'madrona/installer/bin/create-madrona-project.py',
        ],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        'Framework :: Django',
    ],
    # Test suite from setup.py not yet functional
    # requires ./test_settings.py
    # challenge is, of course, install_media
    # and using setuptools messes with
    #   django's package and datafile handling
    # might need to create custom test_suite entry point
    #    test_suite = 'setuptest.SetupTestSuite',
    #    tests_require = (
    #        'django-setuptest',
    #        'django-unittest-depth',
    #        'unittest-xml-reporting',
    #        'BeautifulSoup',
    #        ),
}

#Make sure postgres is ready
try:
    sd = subprocess.check_output(["pg_config", "--sharedir"]).strip()
    # TODO check contrib/postgis*/ for sql files
except Exception as e:
    print( "Failed to locate postgres installation.\n%s" % str(e) )

setup(**setup_args)
