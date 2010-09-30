import warnings

try:
    from distribute_setup import use_setuptools
    use_setuptools()
except:
    warnings.warn(
    "Failed to import distribute_setup, continuing without distribute.", 
    Warning)

from setuptools import setup, find_packages

readme_text = file('README.txt', 'rb').read()

setup_args = dict(
    name                = 'marinemap',
    version             = '1.9dev',
    #requires_python     = '>=2.5,<3',
    #requires_external  = 
    description         = 'A framework for building decisison support tools supporting marine spatial planning',
    author              = 'MarineMap Consortium',
    author_email        = 'mcclintock@msi.ucsb.edu',
    maintainer          = 'MarineMap Consortium',
    maintainer_email    = 'mcclintock@msi.ucsb.edu',
    url                 = 'http://code.google.com/p/marinemap',
    license             = 'New BSD License',
    keywords            = 'kml marine decisionsupport science gis',
    long_description    = readme_text,
    packages            = ['lingcod.%s' % x for x in find_packages('lingcod')],
    #scripts            = 
    #test_suite         = 
    classifiers         = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        'Framework :: Django',
        'Environment :: Web Development'
        ],
    )

setup(**setup_args)
