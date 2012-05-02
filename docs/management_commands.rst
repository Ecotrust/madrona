.. _management_commands:

Madrona/Django Management Commands
==============================================

Type ``manage.py help <subcommand>`` for help on a specific subcommand.

Commonly used subcommands::

    [auth]
        createsuperuser  # create a super user from the command line 

    [common]
        clear_cache  # clears the django cache
        install_cleangeometry  # installs the cleangeometry.sql PLPGSQL function
        install_media  # compiles madrona and project media to a single mediaroot directory
        runprofileserver  # runs a development server but with profiling output
        site  # sets the domain the site is running on

    [django]
        dbshell  # the postgres shell
        dumpdata  # dump model as json fixture
        loaddata  # load data from json fixuture
        runserver # run the dev server
        shell  # django ipython shell

    [djcelery]
        celeryd  # start the async process server

    [features]
        enable_sharing  # enable sharing controls for groups

    [gis]
        ogrinspect  # bootstraps creating models from shapefiles

    [south]
        migrate  # apply any outstanding migrations
        schemamigration  # create a new migration to reflect model changes
        syncdb  # create tables for apps not under migration

    [studyregion]
        create_study_region  # create a study region from a polygon shapefile
