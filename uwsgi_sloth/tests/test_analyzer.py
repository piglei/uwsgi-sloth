# -*- coding: utf-8 -*-
"""Test code for ananlyzer"""
from uwsgi_sloth.analyzer import UWSGILogParser, URLClassifier


class TestUWSGILogParser(object):

    @classmethod
    def setup_class(cls):
        cls.parser = UWSGILogParser()
        cls.invalid_log_line = 'INVALID LOG LINE'
        cls.valid_log_line = ('[pid: 94153|app: 0|req: 51/51] 127.0.0.1 () {40 vars in 880 bytes} '
                              '[Tue Jun 24 22:46:02 2014] GET /trips/hot/?query=3 => generated '
                              '16432 bytes in 55 msecs (HTTP/1.1 200) 4 headers in 285 bytes '
                              '(4 switches on core 0)')

    def test_parse(self):
        valid_result = self.parser.parse(self.valid_log_line)
        assert valid_result['status'] == '200'
        assert valid_result['url'] == '/trips/hot/?query=3'
        assert valid_result['url_path'] == '/trips/hot/'
        assert valid_result['resp_time'] == 55


class TestURLClassifier(object):
    @classmethod
    def setup_class(cls):
        cls.url_classifier = URLClassifier()

    def test_classify_digits(self):
        path = self.url_classifier.classify('/trips/hot/42/foo')
        assert path == '/trips/hot/(\d+)/foo'

    def test_classify_trailing_digits(self):
        path = self.url_classifier.classify('/trips/hot/42')
        assert path == '/trips/hot/(\d+)/'
