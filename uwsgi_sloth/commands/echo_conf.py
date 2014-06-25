# -*- coding: utf-8 -*-
import pkg_resources


def echo_conf(args):
    print pkg_resources.resource_string('uwsgi_sloth', "sample.conf")


def load_subcommand(subparsers):
    """Load this subcommand"""
    parser_analyze = subparsers.add_parser('echo_conf', help='Echo sample configuration file')
    parser_analyze.set_defaults(func=echo_conf)
    

