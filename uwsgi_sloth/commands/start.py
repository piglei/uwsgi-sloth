# -*- coding: utf-8 -*-
"""Start uwsgi-sloth workers"""
import os
import signal
import argparse
import datetime
from configobj import ConfigObj

from uwsgi_sloth.analyzer import format_data, RealtimeLogAnalyzer, URLClassifier
from uwsgi_sloth.tailer import Tailer, no_new_line
from uwsgi_sloth.template import render_template
from uwsgi_sloth.utils import makedir_if_none_exists, total_seconds, parse_url_rules
from uwsgi_sloth.models import merge_requests_data_to, RequestsData, SavePoint
from uwsgi_sloth.settings import REALTIME_UPDATE_INTERVAL, DEFAULT_MIN_MSECS

import logging
logger = logging.getLogger('uwsgi_sloth')


class HTMLRender(object):
    """helper for render HTML"""
    def __init__(self, html_dir, domain=None):
        self.html_dir = html_dir
        self.domain = domain

    def render_requests_data_to_html(self, data, file_name, context={}):
        """Render to HTML file"""
        file_path = os.path.join(self.html_dir, file_name)
        logger.info('Rendering HTML file %s...' % file_path)
        data = format_data(data)
        data.update(context)
        data.update(domain=self.domain)
        with open(file_path, 'w') as fp:
            fp.write(render_template('realtime.html', data))


def update_html_symlink(html_dir):
    """"Maintail symlink: "today.html", "yesterday.html" """
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    for from_date, alias_name in (
            (today, 'today.html'), (yesterday, 'yesterday.html')):
        from_date_file_path = os.path.join(html_dir, 'day_%s.html' % from_date)
        symlink_path = os.path.join(html_dir, alias_name)
        try:                                                                                         
            os.unlink(symlink_path)                                                                  
        except OSError:                                                                              
            pass                                                                                     
        os.symlink(from_date_file_path, symlink_path)


def start(args):
    # Load config file
    config = ConfigObj(infile=args.config.name)
    data_dir = config['data_dir']
    uwsgi_log_path = config['uwsgi_log_path']
    min_msecs = int(config.get('min_msecs', DEFAULT_MIN_MSECS))
    url_file = config.get('url_file')

    # Load custom url rules
    url_rules = []
    if url_file:
        with open(url_file, 'r') as fp:
            url_rules = parse_url_rules(fp)

    html_dir = os.path.join(data_dir, 'html')
    db_dir = os.path.join(data_dir, 'data')
    makedir_if_none_exists(html_dir)
    makedir_if_none_exists(db_dir)

    save_point = SavePoint(db_dir)
    last_log_datetime = save_point.get_last_datetime() or \
                    (datetime.datetime.now() - datetime.timedelta(seconds=REALTIME_UPDATE_INTERVAL))
    logger.info('Start from last savepoint, last_log_datetime: %s' % last_log_datetime)

    last_update_datetime = None
    url_classifier = URLClassifier(user_defined_rules=url_rules)
    analyzer = RealtimeLogAnalyzer(url_classifier=url_classifier, min_msecs=min_msecs,
                                   start_from_datetime=last_log_datetime)
    file_tailer = Tailer(uwsgi_log_path)
    html_render = HTMLRender(html_dir, domain=config.get('domain'))

    # Listen INT/TERM signal
    def gracefully_exit(*args):
        logger.info('Sinal received, exit.')
        file_tailer.stop_follow()
    signal.signal(signal.SIGINT, gracefully_exit) 

    for line in file_tailer:
        # Analyze line
        if line != no_new_line:
            analyzer.analyze_line(line)

        now = datetime.datetime.now()
        if not file_tailer.trailing:
            continue
        if last_update_datetime and \
                total_seconds(now - last_update_datetime) < REALTIME_UPDATE_INTERVAL:
            continue

        # Render HTML file when:
        # - file_tailer reaches end of file.
        # - last_update_datetime if over one `interval` from now

        # Render latest interval HTML file
        html_render.render_requests_data_to_html(analyzer.get_data('last_interval'),
             'latest_5mins.html', context={'datetime_range': 'Last 5 minutes'})
        analyzer.clean_data_by_key('last_interval')

        for date in analyzer.data.keys():
            day_requests_data = RequestsData(date, db_dir)
            merge_requests_data_to(day_requests_data.data, analyzer.get_data(date))
            # Render to HTML file
            html_render.render_requests_data_to_html(day_requests_data.data,
                'day_%s.html' % date, context={'datetime_range': date})
            # Save data to pickle file
            day_requests_data.save()
            # Reset Everything
            analyzer.clean_data_by_key(date)

        update_html_symlink(html_dir)
        last_update_datetime = now
        if analyzer.last_analyzed_datetime:
            save_point.set_last_datetime(analyzer.last_analyzed_datetime)
            save_point.save()


def load_subcommand(subparsers):
    """Load this subcommand"""
    parser_start = subparsers.add_parser('start', help='Start uwsgi-sloth process for realtime analyzing.')
    parser_start.add_argument('-c', '--config', type=argparse.FileType('r'), dest='config',
                                help='uwsgi-sloth config file, use "uwsgi-sloth echo_conf" for a default one', required=True)
    parser_start.set_defaults(func=start)

