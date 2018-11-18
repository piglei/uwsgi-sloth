# -*- coding: utf-8 -*-
"""Data models functions"""
import os
import logging
import pickle

logger = logging.getLogger(__name__)


class SavePoint(object):
    """Model: SavePoint"""
    default_file_name = 'savepoint.pickle'

    def __init__(self, db_dir):
        self.db_file_path = os.path.join(db_dir, self.default_file_name)
        if os.path.exists(self.db_file_path):
            with open(self.db_file_path, 'r') as fp:
                self.data = pickle.load(fp)
        else:
            self.data = {}

    def set_last_datetime(self, datetime):
        self.data['last_datetime'] = datetime

    def get_last_datetime(self):
        return self.data.get('last_datetime')

    def save(self):
        logger.info('SavePoint value change to %s' % self.get_last_datetime())
        with open(self.db_file_path, 'w') as fp:
            pickle.dump(self.data, fp)


class RequestsData(object):
    """Model: RequestsData"""

    def __init__(self, date, db_dir):
        self.date = date
        self.db_file_path = os.path.join(db_dir, '%s.pickle' % date)
        if os.path.exists(self.db_file_path):
            with open(self.db_file_path, 'r') as fp:
                self.data = pickle.load(fp)
        else:
            self.data = {}

    def save(self):
        with open(self.db_file_path, 'w') as fp:
            pickle.dump(self.data, fp)


# Utils for requests data

def merge_urls_data_to(to, food={}):
    """Merge urls data"""
    if not to:
        to.update(food)

    for url, data in food.items():
        if url not in to:
            to[url] = data
        else:
            to[url] = to[url].merge_with(data)


def merge_requests_data_to(to, food={}):
    """Merge a small analyzed result to a big one, this function will modify the 
    original ``to``"""
    if not to:
        to.update(food)

    to['requests_counter']['normal'] += food['requests_counter']['normal']
    to['requests_counter']['slow'] += food['requests_counter']['slow']
    to['total_slow_duration'] += food['total_slow_duration']

    for group_name, urls in food['data_details'].items():
        if group_name not in to['data_details']:
            to['data_details'][group_name] = urls
        else:
            to_urls = to['data_details'][group_name]
            to_urls['duration_agr_data'] = to_urls['duration_agr_data'].merge_with(
                    urls['duration_agr_data'])

            # Merge urls data
            merge_urls_data_to(to_urls['urls'], urls['urls'])

