
Linux
=====

Installing from packages on Ubuntu
----------------------------------

On Ubuntu 11.10, most of the dependencies can be handled by the package management system::

    # Ubuntu packages
    sudo apt-get install python-dev gcc-4.4 \
         postgresql-9.1-postgis postgresql-server-dev-9.1 \
         python-gdal python-imaging python-pip csstidy \
         apache2 libapache2-mod-wsgi
     
    # Mapnik
    sudo add-apt-repository ppa:mapnik/nightly-2.0
    sudo apt-get update
    sudo apt-get install libmapnik mapnik-utils python-mapnik

    # Python PyPi packages
    sudo pip install virtualenv

Installing from source
----------------------

Use packages to some of the dependencies. On Ubuntu Oneric::

    sudo apt-get install htop checkinstall hardinfo sysstat language-pack-gnome-en \
    language-pack-gnome-en-base xorg xorg-docs xterm xserver-xorg x11-apps x11-session-utils \
    x11-utils libx11-dev x11proto-bigreqs-dev x11proto-core-dev x11proto-damage-dev \
    x11proto-dmx-dev x11proto-fixes-dev x11proto-fonts-dev x11proto-gl-dev x11proto-input-dev \
    x11proto-kb-dev x11proto-randr-dev x11proto-record-dev x11proto-render-dev x11proto-resource-dev \
    x11proto-video-dev x11proto-xcmisc-dev x11proto-xext-dev x11proto-xf86bigfont-dev \
    x11proto-xf86dga-dev x11proto-xf86dri-dev x11proto-xf86misc-dev x11proto-xf86vidmode-dev \
    x11proto-xinerama-dev x11-xfs-utils x11-xkb-utils x11-xserver-utils whois apachetop apache2 \
    apache2-mpm-prefork apache2-doc apache2-prefork-dev apache2-utils apache2.2-common idle-python2.6 \
    python-clientform python-crypto python-dbg python-docutils python-doc python-mechanize \
    python-numpy python-numpy-doc python-numpy-dbg python-psycopg2 python-psycopg2-dbg python-pydot \
    python-pyparsing python-roman python-setuptools python-tk python-twisted-conch python-twisted-web2 \
    python-tz python2.6-dbg python2.6-dev python2.6-doc automake1.9 automake1.9-doc g++ g++ \
    g++-multilib fail2ban flex flex-doc clex python-gtkglext1 bison bison-doc bisonc++ \
    bisonc++-doc gcc-4.4 gcc-4.4-doc gcc-4.4-locales gcc-4.4-multilib gcc-4.4-source libgcc1-dbg \
    java-common gcj-jre gcj-jre-headless cmake icmake make-doc mmake munin-node optipng p7zip-full \
    p7zip-rar perl-doc pgadmin3 pgadmin3-data subversion subversion-tools gawk zope-common pgagent \
    gsfonts-x11 libgl1-mesa-dri xutils byacc perl-byacc libtiff-doc libtiff-opengl libtiff-tools \
    libtiff4-dev libtiffxx0c2 libpng12-dev swig swig-doc ipython unzip spe libcunit1-doc \
    libcunit1-ncurses-dev python-zodb automake dblatex xsltproc docbook docbook-defguide \
    docbook-html-forms docbook-xsl-doc-html docbook-xsl-doc-pdf docbook-xsl-doc-text \
    docbook-xsl-saxon docbook-xsl-saxon-gcj docbook2x docbook-dsssl libfreetype6-dev libicu4j-java \
    xml2 python-libxml2-dbg libxml2-dbg libxml2-dev libxml2-doc libltdl-dev pkg-config \
    libboost1.46-all-dev libboost1.46-dev libboost1.46-doc \
    python-opengl libopengl-perl imagemagick imagemagick-dbg imagemagick-doc postgresql-plperl-9.1 \
    postgresql-pltcl-9.1 postgresql-server-dev-9.1 postgresql-plpython-9.1 subversion  \
    libcurses-perl libncurses5-dbg libncurses5-dev libncursesw5-dbg libncursesw5-dev libjpeg62-dbg \
    libjpeg62-dev libopenjpeg2 libopenjpeg2-dbg optipng fftw-dev fftw-docs libfftw3-3 libfftw3-dev \
    libfftw3-doc python-cairo python-cairo-dbg python-cairo-dev libcairo2-dbg libcairo2-dev \
    libcairo2-doc libcairomm-1.0-1 libcairomm-1.0-dev libcairomm-1.0-doc libapache2-mod-wsgi \
    libjava-gnome-jni python-cjson python-cjson-dbg python-pip mercurial python-dev \
    ruby libruby munin-plugins-extra libsigc++-dev libsigx-2.0-2 libsigx-2.0-dev \
    libsigx-2.0-doc python-nose libcurl-ocaml libcurl-ocaml-dev screen libgle3 libgle3-dev \
    git python-virtualenv

DJANGO::

    cd /usr/local/src/
    sudo svn co http://code.djangoproject.com/svn/django/trunk/ django
    cd /usr/local/src/django
    sudo python setup.py install
    sudo ln -s /usr/local/src/django/ /usr/lib/python2.7/dist-packages/

GEOS(3.3.2)::

    cd /usr/local/src/
    sudo wget http://download.osgeo.org/geos/geos-3.3.2.tar.bz2
    sudo tar -xvf geos-3.3.2.tar.bz2
    sudo rm -rf geos-3.3.2.tar.bz2
    cd geos-3.3.2/
    sudo ./configure --enable-python
    sudo make
    sudo make install

PROJ (4.8.0)::

    cd /usr/local/src
    sudo wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
    sudo tar -xvf proj-4.8.0.tar.gz
    sudo rm -rf proj-4.8.0.tar.gz
    sudo chmod 755 -R proj-4.8.0
    cd proj-4.8.0/nad/
    sudo wget http://download.osgeo.org/proj/proj-datumgrid-1.5.zip
    sudo unzip proj-datumgrid-1.5.zip
    sudo rm -rf proj-datumgrid-1.5.zip
    cd ../
    sudo ./configure
    sudo make
    sudo make install
    cd /etc/ld.so.conf.d/
    sudo ln -s /usr/local/lib/libproj.so.0
    sudo ldconfig

GDAL (1.9.0)::

    cd /usr/local/src/
    sudo wget http://download.osgeo.org/gdal/gdal-1.9.0.tar.gz
    sudo tar -xvf gdal-1.9.0.tar.gz
    sudo rm -rf gdal-1.9.0.tar.gz
    cd gdal-1.9.0/
    sudo ./configure --with-python
    sudo make
    sudo make install

PostGIS (1.5.3)::

    cd /usr/local/src/
    sudo wget http://postgis.refractions.net/download/postgis-1.5.3.tar.gz
    sudo tar -xvf postgis-1.5.3.tar.gz
    sudo rm -rf postgis-1.5.3.tar.gz
    cd postgis-1.5.3/
    sudo ./configure
    sudo make
    sudo make install

MAPNIK::

    cd /usr/local/src/
    sudo git clone https://github.com/mapnik/mapnik.git
    cd mapnik/
    sudo ./configure
    sudo make
    sudo make install

GRASS (6.4.2 RC3) -- Optional::

    cd /usr/local/src/
    sudo wget http://grass.osgeo.org/grass64/source/grass-6.4.2RC3.tar.gz
    sudo tar -xvf grass-6.4.2RC3.tar.gz
    sudo rm -rf grass-6.4.2RC3.tar.gz
    cd grass-6.4.2RC3.tar.gz/
    sudo ./configure --enable-64bit --with-cxx --with-python=/usr/bin/python2.7-config --without-tcltk --without-opengl --with-freetype-includes='/usr/include/freetype2' --with-postgres --with-postgres-includes='/usr/include/postgresql' --with-x --with-cairo --with-geos
    sudo make
    sudo make install

