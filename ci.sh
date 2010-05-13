# $WORKSPACE
# $JOB_NAME
echo 
echo 
echo Testing MarineMap revision $MERCURIAL_REVISION
echo
echo

# If env1 exists, it wont be clobbered so we can safely do this
virtualenv env1
cd env1
source bin/activate

# If deps are already installed in this virtualenv, this shouldn't take too long
pip install -r marinemap_requirements.txt 

# Update 
# Note.. env variable may change to HG_REVISION in later version of mercurial hudson plugin
#  see http://issues.hudson-ci.org/browse/HUDSON-4280
pip install -e hg+https://marinemap.googlecode.com/hg@$MERCURIAL_REVISION#egg=marinemap

# Run tests
cd src/marinemap
python build_docs.py -d /var/www/marinemap-docs -j  /usr/local/jsdoc-toolkit-read-only/jsdoc-toolkit 
coverage run run_tests.py
coverage xml --omit /usr/share

