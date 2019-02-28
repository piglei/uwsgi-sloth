# -*- coding: utf-8 -*-

__version__ = '3.0.2'
__VERSION__ = __version__

# Init logger
import logging
import logging.handlers
logger = logging.getLogger('uwsgi_sloth')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

handler.setLevel(logging.DEBUG)

import uwsgi_sloth.compat
