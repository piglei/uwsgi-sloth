# -*- coding: utf-8 -*-
"""Template shortcut & filters"""
import os
import datetime
from jinja2 import Environment, FileSystemLoader

from uwsgi_sloth.settings import ROOT
from uwsgi_sloth import settings, __VERSION__

template_path = os.path.join(ROOT, 'templates')
env = Environment(loader=FileSystemLoader(template_path))

# Template filters

def friendly_time(msecs):
    secs, msecs = divmod(msecs, 1000)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return '%dh%dm%ds' % (hours, mins, secs)
    elif mins:
        return '%dm%ds' % (mins, secs)
    elif secs:
        return '%ds%dms' % (secs, msecs)
    else:
        return '%.2fms' % msecs

env.filters['friendly_time'] = friendly_time


def render_template(template_name, context={}):
    template = env.get_template(template_name)
    context.update(
        SETTINGS=settings,
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        version='.'.join(map(str, __VERSION__)))
    return template.render(**context)


