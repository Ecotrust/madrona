echo $WORKSPACE
echo $JOB_NAME
exit

# If env1 exists, it wont be clobbered so we can safely do this
virtualenv env1

# If deps are already installed in this virtualenv, this shouldn't take too long
pip install -r marinemap_requirements.txt -E env1

# Update 
# Note.. env variable may change to HG_REVISION in later version of mercurial hudson plugin
#  see http://issues.hudson-ci.org/browse/HUDSON-4280
pip install -e hg+https://marinemap.googlecode.com/hg@$MERCURIAL_REVISION#egg=marinemap

# Go into virtualenv and run tests
