.. _virtualenv:

Virtual Environment
===================

While you can install the python dependencies globally, we highly recommend :ref:`creating a 
virtual environment<virtualenv>` and running these commands from within the activated virtualenv.
This will allow you to isolate the python dependencies from other projects on the same
server. 

Create a virtual env that looks at site packages::

    virtualenv --system-site-packages env
    cd env
    source bin/activate

While the prefered way to create a virtual env is to be completely isolated from the system site packages,
there are several python dependencies that were installed system wide because they are difficult to 
`pip install`. If you want to avoid the system packages, you can symlink the other dependencies into the 
clean virtualenv site dir::

    virtualenv --no-site-packages env
    cd env
    source bin/activate
    echo "/usr/lib/python2.7/dist-packages" > <env>/lib/python2.7/site-packages/mapnik.pth
    echo "/usr/local/lib/python2.7/dist-packages" > <env>/lib/python2.7/site-packages/osgeo.pth

`pip install` works in the local env:: 

    pip install madrona

    # If you have packages installed globally,you can upgrade 
    pip install --upgrade madrona

    # Or to upgrade ONLY madrona and not the dependencies
    pip install --upgrade --no-deps madrona
