import os
from fabric.api import *

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def bootstrap():
    """
    Local development bootstrap: you should only run this once.
    """
    # Install requirements
    local("pip install -r ./requirements.txt")
        
    # Set virtualenv vars for local dev
    local('echo "export DJANGO_SETTINGS_MODULE=campfin.settings\"')
    local('echo "export PYTHONPATH=%s:%s/campfin"' % (BASE_DIR, BASE_DIR))

    # Create database
    local("python ./%(project_name)s/manage.py syncdb --noinput" % env)