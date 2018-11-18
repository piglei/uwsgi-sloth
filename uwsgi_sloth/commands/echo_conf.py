# -*- coding: utf-8 -*-
from __future__ import print_function
import pkg_resources
from uwsgi_sloth.utils import force_text


def echo_conf(args):
    print(force_text(pkg_resources.resource_string('uwsgi_sloth', "sample.conf")))


def load_subcommand(subparsers):
    """Load this subcommand"""
    parser_analyze = subparsers.add_parser('echo_conf', help='Echo sample configuration file')
    parser_analyze.set_defaults(func=echo_conf)
    

