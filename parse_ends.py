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




class MyEndHandler(ContentHandler):
    """
     Default Skript Configuration:
         ./data/FAC_ends.pkl                 (result)
         ./tmp/FAC_ends_prob.pkl            (problematic results)
         ./data/FAChistory.xml              (source)

     """

    def __init__(self, out_file, prob_file):
        """
        :param out_file:
        """
        self._out_file = out_file
        self._prob_file = prob_file

        # create logger with 'spam_application'
        self.logger = logging.getLogger('end_logger')
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('./log/end.log')
        fh.setLevel(logging.DEBUG)
        # add the handlers to the logger
        self.logger.addHandler(fh)

        # Flags
        self.text_flag = False
        self.date_flag = False
        self.skip_flag = False

        # Temps
        self._rev_no = 0
        self._date_no = 0
        self._limit_bool = False
        self._limit = 10
        self.debug_l = []

        self._charBuffer = []
        self._text = ''
        self._ts = ''

        # self._format_dict = {'\* \[{2}(.*?)\]{2}': (None,)}
        # ={2}\* ?\[{2}(.*?)\]{2}":(None,),
        self._format_dict = {'\* \[{2}(.*?)\]{2}': (None,),
                             "Wikipedia:Featured article candidates/(.*)\}{2}": (None,)}

        self._revision_dict = {}  # {ts_revision : [articles]}
        self._problematic = {}  # {ts_revision : [articles]}

    def _get_character_data(self):
        data = ''.join(self._charBuffer).strip()
        self._charBuffer = []
        return data

    def _match_and_return(self, content, format_dict):
        return [match.groups()[0] for regex in format_dict.keys() for match in re.finditer(regex, content)]

    def parse(self, f):
        xml.sax.parse(f, self)

    def characters(self, data):
        self._charBuffer.append(data)

    def startElement(self, name, attrs):
        if name == 'text':
            self._rev_no += 1
            self.text_flag = True
        if name == 'timestamp':
            self._date_no += 1
            self.date_flag = True


    def endElement(self, name):
        if self.date_flag:
            self.logger.debug( f'{self._ts}: (SF:{self.skip_flag}, {self.skip_flag}, {self.date_flag} {self._text[:30]}) \n')
            self._text = self._get_character_data()
            self._ts = datetime.strptime(self._text, '%Y-%m-%dT%H:%M:%SZ')
            # if self._ts >= datetime.strptime('2016-12-31T23:59:59Z', '%Y-%m-%dT%H:%M:%SZ') and \
            #        self._ts <= datetime.strptime('2005-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'):

            if datetime.strptime('2016-12-31T23:59:59Z', '%Y-%m-%dT%H:%M:%SZ') <= self._ts <= datetime.strptime('2005-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'):
                self.skip_flag = True
            else:
                self.skip_flag = False


        if self.text_flag and not self.skip_flag:
            self._text = self._get_character_data()
            articles = self._match_and_return(self._text, self._format_dict)

            if self._ts in self._revision_dict:
                print(f'{self._ts} is already in the dict. \n This schould not have happend! (More than once)')
                self._problematic[self._ts] = articles
            else:
                self._revision_dict[self._ts] = articles
        self.debug_l.append(self.skip_flag)

        self.date_flag = False
        self.text_flag = False
        self._charBuffer = []

    def endDocument(self):
        res = {}
        for i, (ts, articles) in enumerate(self._revision_dict.items()):
            for article in articles:
                if article not in res:
                    res[article] = [ts]
                else:
                    res[article].append(ts)

        with open(self._out_file, 'wb') as file:
            pickle.dump(res, file)
        with open(self._prob_file, 'wb') as file:
            pickle.dump(self._problematic, file)


if __name__ == '__main__':
    logging.basicConfig(filename='./log/log_ends.txt', level=logging.DEBUG)
    _, out_file, in_file, prob_file = sys.argv
    MyEndHandler(out_file, prob_file).parse(in_file)
