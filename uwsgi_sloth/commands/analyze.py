# -*- coding: utf-8 -*-
import sys
import time
import logging
import argparse

from uwsgi_sloth.settings import LIMIT_URL_GROUPS, LIMIT_PER_URL_GROUP
from uwsgi_sloth.analyzer import URLClassifier, LogAnalyzer, format_data
from uwsgi_sloth.template import render_template
from uwsgi_sloth.utils import parse_url_rules, smart_str

logger = logging.getLogger('uwsgi_sloth.analyze')


def analyze_log(fp, configs, url_rules):
    """Analyze log file"""
    url_classifier = URLClassifier(url_rules)
    analyzer = LogAnalyzer(
        url_classifier=url_classifier, min_msecs=configs.min_msecs,
        memory_report=configs.memory_report,
    )
    for line in fp:
        analyzer.analyze_line(line)
    return analyzer.get_data()


def analyze(args):
    # Get custom url rules
    url_rules = []
    if args.url_file:
        url_rules = parse_url_rules(args.url_file)

    logger.info('Analyzing log file "%s"...' % args.filepath.name)
    start_time = time.time()

    data = analyze_log(args.filepath, args, url_rules)
    data = format_data(data, order_field=args.order_field)
    data.update({
        'domain': args.domain,
        'input_filename': args.filepath.name,
        'min_duration': args.min_msecs,
        'memory_report': args.memory_report,
    })

    # Pre-process data
    html_data = render_template('report.html', data)

    args.output.write(smart_str(html_data))
    args.output.close()
    logger.info('Finished in %.2f seconds.' % (time.time() - start_time))


def load_subcommand(subparsers):
    """Load this subcommand"""
    parser_analyze = subparsers.add_parser('analyze', help='Analyze uwsgi log to get report')
    parser_analyze.add_argument('-f', '--filepath', type=argparse.FileType('r'), dest='filepath',
                                help='Path of uwsgi log file', required=True)
    parser_analyze.add_argument('--output', dest="output", type=argparse.FileType('w'), default=sys.stdout,
                                help='HTML report file path')
    parser_analyze.add_argument('--min-msecs', dest="min_msecs", type=int, default=200,
                                help='Request serve time lower than this value will not be counted, default: 200')
    parser_analyze.add_argument('--domain', dest="domain", type=str, required=False,
                                help='Make url in report become a hyper-link by settings a domain')
    parser_analyze.add_argument('--url-file', dest="url_file", type=file, required=False,
                                help='Customized url rules in regular expression')
    parser_analyze.add_argument('--memory-report', dest="memory_report", required=False, default=False,
                                action='store_true',
                                help='UWSGI config have ``memory-report`` option set to True')
    parser_analyze.add_argument('--order-field', dest="order_field", type=str, required=False,
                                default='duration_agr_data',
                                help='Field to order by. E.g.: duration_agr_data, mem_agr_data')
    parser_analyze.set_defaults(func=analyze)
