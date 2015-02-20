# -*- coding: utf-8 -*-
"""Analyzer for uwsgi log"""
import re
import copy
import datetime
from uwsgi_sloth.utils import total_seconds
from uwsgi_sloth.structures import ValuesAggregation
from uwsgi_sloth.settings import FILTER_METHODS, FILTER_STATUS, LIMIT_URL_GROUPS, \
                                 LIMIT_PER_URL_GROUP, ROOT, REALTIME_UPDATE_INTERVAL


class UWSGILogParser(object):
    """Parser for uwsgi log file, support only default log format:

    log format: "[pid: 27011|app: 0|req: 16858/537445] 58.251.73.227 () {40 vars in 1030 bytes} \
                 [Tue Apr 29 00:13:10 2014] POST /trips/2387949771/add_waypoint/ => \
                 generated 1053 bytes in 2767 msecs (HTTP/1.1 200) 4 headers in 282 bytes \
                 (1 switches on core 0)"

    Returns:
    ~~~~~~~~

    An dict of parsed log result.
    """
    DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'

    def __init__(self, memory_report=False):
        common_re_part = r'''}\ \[(?P<datetime>.*?)\]\ (?P<request_method>POST|GET|DELETE|PUT)\s
        (?P<request_uri>[^ ]*?)\ =>\ generated\ (?:.*?)\ in\ (?P<resp_msecs>\d+)\ msecs\s
        \(HTTP/[\d.]+\ (?P<resp_status>\d+)\)'''
        if memory_report:
            self.RE_LOG_LINE = re.compile(
                r'''{address\ space\ usage:\ (?P<address_space_usage>\d+)\ bytes.*}\s
                {rss\ usage:\ (?P<rss_usage>\d+)\ bytes.*}\s.*'''
                + common_re_part, re.VERBOSE)
        else:
            self.RE_LOG_LINE = re.compile(common_re_part, re.VERBOSE)
        self.memory_report = memory_report

    def parse(self, line):
        matched = self.RE_LOG_LINE.search(line)
        if matched:
            matched_dict = matched.groupdict()
            method = matched_dict['request_method']
            status = matched_dict['resp_status']
            if not method in FILTER_METHODS or status not in FILTER_STATUS:
                return

            url = matched_dict['request_uri'].replace('//', '/')
            url_path = url.split('?')[0]
            resp_time = int(matched_dict['resp_msecs'])
            request_datetime = datetime.datetime.strptime(matched_dict['datetime'],
                                                          self.DATETIME_FORMAT)
            results = {
                'method': method,
                'url': url,
                'url_path': url_path,
                'resp_time': resp_time,
                'status': status,
                'request_datetime': request_datetime,
            }
            if self.memory_report:
                address_space_usage = int(matched_dict['address_space_usage'] or 0) / (1024**2)
                rss_usage = int(matched_dict['rss_usage'] or 0) / (1024**2)
                total_mem_usage = address_space_usage + rss_usage
                results.update({
                    'address_space_usage': address_space_usage,
                    'rss_usage': rss_usage,
                    'total_mem_usage': total_mem_usage,
                })
            return results
        return


class URLClassifier(object):
    """A simple url classifier, current rules:

    - replacing sequential digits part by '(\d+)'
    """

    RE_SIMPLIFY_URL = re.compile(r'(?<=/)\d+[/$]')

    def __init__(self, user_defined_rules=[]):
        self.user_defined_rules = user_defined_rules

    def classify(self, url_path):
        """Classify an url"""
        for dict_api_url in self.user_defined_rules:
            api_url = dict_api_url['str']
            re_api_url = dict_api_url['re']
            if re_api_url.match(url_path[1:]):
                return api_url

        return self.RE_SIMPLIFY_URL.sub('(\d+)/', url_path)


class LogAnalyzer(object):
    """Log analyzer"""

    def __init__(
            self, url_classifier=None, min_msecs=200, start_from_datetime=None,
            memory_report=False):
        self.data = {}
        self.requests_counter = {'normal': 0, 'slow': 0}
        self.total_slow_duration = 0

        self.min_msecs = min_msecs
        self.start_from_datetime = start_from_datetime
        self.datetime_range = [None, None]

        self.url_classifier = url_classifier or URLClassifier()
        self.log_parser = UWSGILogParser(memory_report=memory_report)
        self.memory_report = memory_report

    def analyze_line(self, line):
        line = line.strip()
        result = self.log_parser.parse(line)
        # Ignore invalid log
        if not result:
            return
        if self.start_from_datetime and result['request_datetime'] <= self.start_from_datetime:
            return

        self.requests_counter['normal'] += 1

        if not self.datetime_range[0]:
            self.datetime_range[0] = result['request_datetime']
        self.datetime_range[1] = result['request_datetime']
        if result['resp_time'] < self.min_msecs:
            return

        resp_time = result['resp_time']
        mem_usage = result['total_mem_usage']

        # Use url_classifier to classify url
        matched_url_rule = self.url_classifier.classify(result['url_path'])

        default_dict = {
            'urls': {},
            'duration_agr_data': ValuesAggregation(),
        }

        if self.memory_report:
            default_dict.update({
                'mem_agr_data': ValuesAggregation(),
            })
        big_d = self.data.setdefault((result['method'], matched_url_rule), default_dict)

        big_d['duration_agr_data'].add_value(resp_time)
        if self.memory_report:
            big_d['mem_agr_data'].add_value(mem_usage)
        big_d['urls'].setdefault(result['url'], ValuesAggregation()).add_value(resp_time)

        self.requests_counter['slow'] += 1
        self.total_slow_duration += resp_time

    def get_data(self):
        return {
            'requests_counter': self.requests_counter,
            'total_slow_duration': self.total_slow_duration,
            'datetime_range': self.datetime_range,
            'data_details': self.data
        }


class RealtimeLogAnalyzer(object):
    """Log analyzer for realtime support"""

    default_data = {
        'requests_counter': {'normal': 0, 'slow': 0},
        'total_slow_duration': 0,
        'data_details': {}
    }

    def __init__(
            self, url_classifier=None, min_msecs=200, start_from_datetime=None,
            memory_report=False):
        self.data = {}
        self.min_msecs = min_msecs
        self.start_from_datetime = start_from_datetime
        self.last_analyzed_datetime = None

        self.url_classifier = url_classifier or URLClassifier()
        self.log_parser = UWSGILogParser(memory_report=memory_report)
        self.memory_report = memory_report

    def analyze_line(self, line):
        line = line.strip()
        result = self.log_parser.parse(line)
        # Ignore invalid log
        if not result:
            return
        if self.start_from_datetime and result['request_datetime'] <= self.start_from_datetime:
            return
        request_datetime = result['request_datetime']
        self.last_analyzed_datetime = request_datetime
        groups = self.get_result_group_names(request_datetime)
        if not groups:
            return

        for group in groups:
            if group not in self.data:
                self.data[group] = copy.deepcopy(self.default_data)

        for group in groups:
            self.data[group]['requests_counter']['normal'] += 1
        if result['resp_time'] < self.min_msecs:
            return

        resp_time = result['resp_time']
        if self.memory_report:
            mem_usage = result['total_mem_usage']

        # Use url_classifier to classify url
        matched_url_rule = self.url_classifier.classify(result['url_path'])

        for group in groups:
            default_dict = {
                'urls': {},
                'duration_agr_data': ValuesAggregation(),
            }
            if self.memory_report:
                default_dict.update({
                    'mem_agr_data': ValuesAggregation(),
                })
            big_d = self.data[group]['data_details'].setdefault((result['method'], matched_url_rule), default_dict)

            big_d['duration_agr_data'].add_value(resp_time)
            if self.memory_report:
                big_d['mem_agr_data'].add_value(mem_usage)
            big_d['urls'].setdefault(result['url'], ValuesAggregation()).add_value(resp_time)

            self.data[group]['requests_counter']['slow'] += 1
            self.data[group]['total_slow_duration'] += resp_time

    def get_result_group_names(self, request_datetime):
        """Only today/yesterday/last interval are valid datetime"""
        request_date = request_datetime.date()
        today = datetime.date.today()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        result = []
        if total_seconds(datetime.datetime.now() - request_datetime) < REALTIME_UPDATE_INTERVAL:
            result.append('last_interval')
        if request_date == today:
            result.append(today.isoformat())
        elif request_date == yesterday:
            result.append(yesterday.isoformat())
        return result

    def get_data(self, key=None):
        if key:
            return self.data.get(key, self.default_data)
        return self.data

    def clean_data_by_key(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass


def format_data(raw_data, order_field="duration_agr_data"):
    """Fomat data from LogAnalyzer for render purpose"""
    data = copy.deepcopy(raw_data)
    for k, v in data['data_details'].items():
        # Only reserve first ``LIMIT_PER_URL_GROUP`` items
        v['urls'] = sorted(v['urls'].iteritems(), key=lambda (k, v): v.total,
                           reverse=True)[:LIMIT_PER_URL_GROUP]

    data_details = sorted(data['data_details'].iteritems(),
                          key=lambda (k, v): v[order_field].total,
                          reverse=True)[:LIMIT_URL_GROUPS]

    if data['requests_counter']['normal']:
        slow_rate = format(data['requests_counter']['slow'] / \
                           float(data['requests_counter']['normal']), '.2%')
    else:
        slow_rate = '-'
    data.update({
        'slow_rate': slow_rate,
        'data_details': data_details,
    })
    return data


