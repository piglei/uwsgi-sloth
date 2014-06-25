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


