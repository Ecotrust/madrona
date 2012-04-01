import warnings
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools import setup, find_packages

readme_text = file('README.rst', 'rb').read()
packages = ['madrona.%s' % x for x in find_packages('madrona')]
packages.append('madrona')

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)
    return requirements

setup_args = dict(
    name = 'madrona',
    version = '4.0dev',
    description = 'A framework for building spatial decisison support tools',
    author = 'MarineMap Consortium, Ecotrust',
    author_email = 'mperry@ecotrust.org',
    maintainer = 'Ecotrust',
    maintainer_email = 'ksdev@ecotrust.org',
    url = 'http://ecotrust.github.com/madrona',
    license = 'New BSD License',
    keywords = 'kml marine decisionsupport science gis',
    long_description = readme_text,
    packages = packages,
    scripts = [
        'madrona/installer/create-madrona-project.py',
        'madrona/installer/create-madrona-env'
        ],
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = [
        'https://github.com/springmeyer/djmapnik/tarball/8d736a73470b/#egg=djmapnik-0.1.3',
        ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
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
