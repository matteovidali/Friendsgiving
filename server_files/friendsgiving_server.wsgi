#!/user/bin/python3
import sys
import logging
logging.basicConf(stream=sys.stderr)
sys.path.insert(0, "/var/www/friendsgiving")

from friendsgiving import api as application
