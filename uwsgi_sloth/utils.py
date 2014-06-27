# -*- coding: utf-8 -*-
import os
import re

def parse_url_rules(urls_fp):
    """URL rules from given fp"""
    url_rules = []
    for line in urls_fp:
        re_url = line.strip()
        if re_url:
            url_rules.append({'str': re_url, 're': re.compile(re_url)})
    return url_rules


def makedir_if_none_exists(d):
    if not os.path.exists(d):
        os.makedirs(d)


def total_seconds(td):
    """Return timedelta's total seconds"""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6


def smart_str(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s.encode(encoding)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', 'ignore').encode(encoding, 'ignore')
    else:
        return str(s)
    
def smart_unicode(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding, 'ignore')


