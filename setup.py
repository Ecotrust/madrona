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

from madrona.common.default_settings import RELEASE

setup_args = dict(
    name                = 'madrona',
    version             = RELEASE,
    description         = 'A framework for building decisison support tools supporting marine spatial planning',
    author              = 'MarineMap Consortium, Ecotrust',
    author_email        = 'mcclintock@msi.ucsb.edu',
    maintainer          = 'Ecotrust',
    maintainer_email    = 'ksdev@ecotrust.org',
    url                 = 'http://ecotrust.github.com/madrona',
    license             = 'New BSD License',
    keywords            = 'kml marine decisionsupport science gis',
    long_description    = readme_text,
    packages            = ['madrona.%s' % x for x in find_packages('madrona')],
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
