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


def force_bytes(s, encoding='utf-8', errors='strict'):
    """A function turns "s" into bytes object, similar to django.utils.encoding.force_bytes
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)

    
def force_text(s, encoding='utf-8',  errors='strict'):
    """A function turns "s" into text type, similar to django.utils.encoding.force_text
    """
    if issubclass(type(s), str):
        return s
    try:
        if isinstance(s, bytes):
            s = str(s, encoding, errors)
        else:
            s = str(s)
    except UnicodeDecodeError as e:
        raise DjangoUnicodeDecodeError(s, *e.args)
    return s