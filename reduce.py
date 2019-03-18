# import standard python moduls
from pprint import pprint
import re
import sys
import os
from datetime import datetime
import logging
import pickle

# import xml utilies
from xml.sax.handler import ContentHandler
import xml.sax

#import data science utils
import pandas as pd
import numpy as np



class MyReducer(ContentHandler):
    def __init__(self, out_file):
        self._rev_no = 0
        self._date_no = 0
        self.lines_written = 0

        self.date_flag = False
        self.text_flag = False
        self.skip_flag = False
        self.out_file = out_file

        self._ts = ''
        self._text = ''
        self._charBuffer = []

    def _get_character_data(self):
        data = ''.join(self._charBuffer).strip()
        self._charBuffer = []
        return data

    def parse(self, f):
        xml.sax.parse(f, self)

    def characters(self, data):
        self._charBuffer.append(data)

    def startDocument(self):
        with open(self.out_file, 'w') as f:
            f.write('')

    def startElement(self, name, attrs):
        if name == 'text':
            self._rev_no += 1
            self.text_flag = True
        if name == 'timestamp':
            self._date_no += 1
            self.date_flag = True

    def endElement(self, name):
        if self.date_flag:
            self._text = self._get_character_data()
            self._ts = datetime.strptime(self._text, '%Y-%m-%dT%H:%M:%SZ')
            if datetime.strptime('2008-02-28T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ') <= self._ts <= \
                    datetime.strptime('2009-12-31T23:59:59Z', '%Y-%m-%dT%H:%M:%SZ'):
                self.skip_flag = False
            else:
                self.skip_flag = True

        if self.text_flag and not self.skip_flag:
            self._text = self._get_character_data()
            with open(self.out_file, 'a') as f:
                f.write(str(self._ts))
                f.write(self._text)

        self.date_flag = False
        self.text_flag = False
        self._charBuffer = []

    def endDocument(self):
        print(self._ts)

if __name__ == '__main__':
    _, out_file, in_file = sys.argv
    MyReducer(out_file).parse(in_file)

