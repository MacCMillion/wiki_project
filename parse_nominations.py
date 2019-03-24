"""
./data/FAC_nomination.csv ./data/FAC.xml
"""


# import standard python moduls
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


class MyNominationHandler(ContentHandler):
    """
    Default Skript Configuration:
    for unsucessful nominations:
        ./res/FAC_nomination.csv    (result)
        ./data/FAC.xml              (source)

    for sucessful nominatiions:
        ./res/FA_nomination.csv     (result)
        ./data/FAC.xml              (source)

    """
    def __init__(self, out_file, prob_file):
        """
        :param out_file:
        """
        self._out_file = out_file
        self._prob_file = prob_file
        self.text_flag = False
        self._charBuffer = []
        self._text = ''
        self._result = []
        self._problematic = []
        self._no_title = []
        self._pos = 0
        self._format_dict_title = {
            "=== ?'{0,2}\[\[(.*)\]\] ?'{0,2}===": (None,)
        }
        self._format_dict = {
            "([\d]{2}:[\d]{2}, [A-Za-z]{3} [\d]{1,2}, [\d]{4}) \(UTC\)": (datetime.strptime, '%H:%M, %b %d, %Y'),
            "([\d]{2}:[\d]{2}, [\d]{1,2} [A-Za-z]{3} [\d]{4}) \(UTC\)": (datetime.strptime, '%H:%M, %d %b %Y'),
            "([\d]{2}:[\d]{2}, [\d]{1,2} [A-Za-z]{4,9} [\d]{4}) \(UTC\)": (datetime.strptime, '%H:%M, %d %B %Y'),
            "([\d]{2}:[\d]{2}, [A-Za-z]{4,8} [\d]{1,2}, [\d]{4}) \(UTC\)": (datetime.strptime, '%H:%M, %B %d, %Y'),
            "([A-Z][a-z]{3,8} [\d]{1,2}, [\d]{4} [\d]{2}:[\d]{2}) \(UTC\)": (datetime.strptime, '%B %d, %Y %H:%M'),
        }

    def _get_character_data(self):
        data = ''.join(self._charBuffer).strip()
        self._charBuffer = []
        return data

    def _my_wrapper(self, func, groups, param):
        if func:
            return func(*groups, *param)
        else:
            if len(groups) == 1:
                return groups[0]
            else:
                return groups

    def _match_and_format(self, content, format_dict, ensure_order=True, select_slices=False, verbose=True):
        """ takes a dictionary with regex as keys and input. These regex will be matched against content.
        The resulting groups will be processed acording to functions stored as vlaues of the dictionary"""
        matches = [(match.start, match, regex) for regex in format_dict.keys()
                   for match in re.finditer(regex, content)]
        if ensure_order:
            matches.sort(key=lambda x: x[0])
        if select_slices:
            a, b, c = select_slices
            matches = matches[a:b:c]

        res = np.array([self._my_wrapper(format_dict[regex_i][0], match_i.groups(), format_dict[regex_i][1:])
                        for _, match_i, regex_i in matches])
        return res

    def _match_and_return(self, content, format_dict):
        return [match.groups(0) for regex in format_dict.keys() for match in re.finditer(regex, content)]

    def parse(self, f):
        xml.sax.parse(f, self)

    def characters(self, data):
        self._charBuffer.append(data)

    def startElement(self, name, attrs):
        if name == 'text':
            self._pos += 1
            self.text_flag = True

    def endElement(self, name):
        if self.text_flag:
            self._text = self._get_character_data()
            try:
                dates = self._match_and_format(self._text, self._format_dict, False, False, False)
                titles = self._match_and_return(self._text, self._format_dict_title)
                if titles:    # check if a non-empty list starting with a title is  returned
                    self._result.append([self._pos, titles, dates])
                else:
                    self._no_title.append([self._pos, dates, self._text])

            except ValueError:
                print(f'Problem parsing date in {self._pos}')
                self._problematic.append(self._text)
        self.text_flag = False
        self._charBuffer = []

    def endDocument(self, ):
        df = pd.DataFrame()
        i=0
        for entry in self._result:
            try:
                #i, title, dates = entry[0], entry[1][0], entry[2:]
                i = entry[0]
                title = entry[1][0][0]
                dates = entry[2]
                #print(f'{i}\n{title}\n{dates}\n\n')
                start, end = np.sort(dates)[[0, -1]]
                df[i] = [i, title, start, end]
            except IndexError as e:
                print(e)
                print(f'Problematic entry in {entry[0]}')
                print('seems like no title was found.')
                self._no_title.append([entry[0], entry[1:]])


        df = df.transpose()
        df.columns = ['idx', 'title', 'date_nomination', 'date_last_comment']
        df.set_index('idx')
        df.to_csv(self._out_file, sep=';', decimal='.')
        with open(self._prob_file, 'wb') as f:
            pickle.dump(self._no_title, f)


if __name__ == '__main__':
    logging.basicConfig(filename='./log/log_fac.txt', level=logging.DEBUG)
    _, out_file, in_file, prob_file = sys.argv
    MyNominationHandler(out_file, prob_file).parse(in_file)
