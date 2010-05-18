# $WORKSPACE
# $JOB_NAME
echo 
echo 
echo Building MarineMap docs : revision $MERCURIAL_REVISION
echo
echo
python build_docs.py -d /var/www/marinemap-docs -j  /usr/local/jsdoc-toolkit-read-only/jsdoc-toolkit 

echo 
echo 
echo Testing MarineMap : revision $MERCURIAL_REVISION
echo
echo
coverage run run_tests.py

echo 
echo 
echo Analyzing coverage : revision $MERCURIAL_REVISION
echo
echo
coverage xml --omit /usr/share

