# -*- coding: utf-8 -*-
import sys

__VERSION__ = [1, 0, 1]

# Init logger
import logging
import logging.handlers
logger = logging.getLogger('uwsgi_sloth')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

handler.setLevel(logging.DEBUG)

