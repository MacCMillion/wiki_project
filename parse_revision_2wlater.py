# import standard python moduls
import re
import sys
import os
import ciso8601
import logging
import pickle
import gzip

# import xml utilies
from xml.sax.handler import ContentHandler
import xml.sax
from revision import RevisionXML

#import data science utils
import pandas as pd
import numpy as np
import config


class MyRevisionsHandler(ContentHandler):
    """
    Default Skript Configuration:
        out_file: path to .csv for storing output
        in_file: wikipedia revision history (stubs.meta.history)
        control_file: path to .csv file with nomination period
    """
    def __init__(self, out_file, control_file, new = False):
        """
        :param out_file:
        """
        self._out_file = out_file

        self.df_nominations = pd.read_csv(control_file, sep=';', index_col='title',
                                          parse_dates=['end_date', 'date_2w_later'])
        self.articles_to_parse = set(self.df_nominations.index)

        if new:
            with open(self._out_file, 'w') as file:
                file.write('title;edits_2w_later;authors_2w_later;\n')
        else:
            self.articles_to_parse - self.get_already_parsed(out_file)

        self.flag_newpage = False
        self.flag_revision = False
        self.flag_contributor = False
        self.flag_skip_article = True

        self.end_date = np.datetime64('1900')
        self.date_2wlater = np.datetime64('2100')

        self.article_id = 0
        self.revision_id = 0
        self.article_name = ''
        self.author_id = 0
        self.ts = 0.0

        self.edits_2wlater = 0
        self.uniq_authors_2wlater = set()


        self._char_buffer = []
        self._text = ''

        # debug
        self._name = ''
        self._rev_count = 0
        self.i =0


    def get_already_parsed(self, file_parsed):
        df = pd.read_csv(out_file, sep=';')
        res = set(df['title'])
        return res

    def _get_character_data(self):
        data = ''.join(self._char_buffer).strip()
        self._char_buffer = []
        return data

    def parse(self, f):
        xml.sax.parse(f, self)

    def characters(self, content):
        self._char_buffer.append(content)

    def log_status(self):
        return vars(self)

    def log_status(self):
        m = f'Element: {self._name} article_id: {self.article_id},NP: {self.flag_newpage} REV: {self.flag_newpage}, ' \
            f'CONT: {self.flag_contributor} \n{self._text}'
        return m

    def startElement(self, name, attrs):
        self._name = name
        if name == 'page':
            self.flag_newpage = True
            self.flag_skip_article = False

        if name == 'contributor':
            self.flag_contributor = True
            self.flag_revision = False

        if name == 'revision':
            self.flag_revision = True
            self.flag_newpage = False

    def endElement(self, name):
        if not self.flag_skip_article:
            self._name = name

            if name == 'page':
                with open(self._out_file, 'a') as file:
                    file.write(f'{self.article_name};{self.edits_2wlater};{len(self.uniq_authors_2wlater)};\n')
                self.edits_2wlater = 0
                self.uniq_authors_2wlater = set()

            if name == 'title':
                self.article_name = self._get_character_data()
                if self.article_name not in self.articles_to_parse:
                    self.flag_skip_article = True
                else:
                    self.end_date = self.df_nominations.at[self.article_name, 'end_date']
                    self.date_2wlater = self.df_nominations.at[self.article_name, 'date_2w_later']
                    self.i += 1
                    #print(self.start_date, self.end_date, self.ts)


            if name == 'id':
                if self.flag_newpage:
                    self._text = self._get_character_data()
                    self.article_id = int(self._text)
                elif self.flag_contributor:
                    self._text = self._get_character_data()
                    self.author_id = int(self._text)
                elif self.flag_revision:
                    self._text = self._get_character_data()
                    self.revision_id = int(self._text)

            if name == 'revision' and (self.end_date <= self.ts <= self.date_2wlater):
                self.edits_2wlater +=1
                self.uniq_authors_2wlater.add(self.author_id)
                self.flag_revision = False
                self._rev_count += 1

            if name == 'contributor':
                self.flag_contributor = False

            if name == 'timestamp':
                self.ts = np.datetime64(ciso8601.parse_datetime(self._get_character_data()))
        self._char_buffer = []


if __name__ == '__main__':
    with open('./log/log_revisions.log', 'w') as log_file:
        log_file.write('')
    logging.basicConfig(filename='./log/log_revisions.log', level=logging.DEBUG)
    _, out_file, in_file, control_file = sys.argv
    with gzip.open(in_file) as input_file:
        MyRevisionsHandler(out_file, control_file, True).parse(input_file)









