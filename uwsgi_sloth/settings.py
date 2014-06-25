# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

FILTER_METHODS = ('GET', 'POST', 'PUT', 'DELETE')
FILTER_STATUS = ('200', )

LIMIT_URL_GROUPS = 200
LIMIT_PER_URL_GROUP = 20
DEFAULT_MIN_MSECS = 200

STATIC_PATH_BOOTSTRAP = 'http://maxcdn.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css'
STATIC_PATH_JQUERY = 'http://code.jquery.com/jquery-1.7.2.min.js'

REALTIME_UPDATE_INTERVAL = 5 * 60


