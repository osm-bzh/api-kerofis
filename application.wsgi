import os, sys

PROJECT_DIR = '/Users/mael/Sites/htdocs/osm-br/api/'

activate_this = os.path.join(PROJECT_DIR, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)

from helloflask import app as application

