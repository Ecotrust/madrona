echo Testing Madrona : revision $GIT_REVISION
coverage run run_tests.py

echo Building Madrona docs : revision $GIT_REVISION
#python build_docs.py -d /var/www/madrona-docs -j  /usr/local/jsdoc-toolkit-read-only/jsdoc-toolkit 

echo Analyzing coverage : revision $GIT_REVISION
coverage xml --include=*madrona*

