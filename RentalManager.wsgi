#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/RentalManager/")

from RentalManager import app as application
application.secret_key = 'johannes-scheibe'
