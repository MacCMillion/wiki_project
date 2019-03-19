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
        ./res/FAC_nomination.csv    (result)
        ./data/FAC.xml              (source)
    """
    def __init__(self, out_file, control_file):
        """
        :param out_file:
        """
        self.df_nominations = pd.read_csv(control_file, **config.pandas_import)
        self.articles_to_parse = set(self.df_nominations['title'])

        self._out_file = out_file

        self.flag_newpage = False
        self.flag_revision = False
        self.flag_contributor = False
        self.flag_skip_article = True
        self.start = 0.0
        self.end = np.inf

        self.revision = None

        self.article_id = 0
        self.revision_id = 0
        self.article_name = ''
        self.author_id = 0
        self.author_name = ''
        self.registered = False
        self.ts = 0.0
        self.length = 0
        self.minor = False
        self.comment = ''
        self.revision_hash = ''
        self.revert = False


        self._char_buffer = []
        self._text = ''
        self._result = []
        self._problematic = []

        # debug
        self._name = ''
        self._rev_count = 0
        self.i =0

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
            # print(self._name, self._text)
            if name == 'id':
                # logging.debug(self.log_status())
                if self.flag_newpage:
                    self._text = self._get_character_data()
                    # print('page_id: ', self._text)
                    self.article_id = int(self._text)
                elif self.flag_contributor:
                    self._text = self._get_character_data()
                    self.author_id = int(self._text)
                    # print('author_id: ', self._text)
                elif self.flag_revision:
                    self._text = self._get_character_data()
                    self.revision_id = int(self._text)
                    # print('revision_id: ', self.revision_id)
                else:
                    logging.debug('ERROR: ID couldn\'t be assigned to any element')
                    print('What have you done?? You should never end up here!')
                    print(self._text)
                logging.debug(f'{self._text}   newpage: {self.flag_newpage}      revision: {self.flag_revision}    contributer {self.flag_contributor}')

            if name == 'revision' and (self.start <= self.ts <= self.end):
                print('got here')
                revision = RevisionXML(page_title=self.article_name, page_id=self.article_id,
                                       revision_id=self.revision_id, author_id=self.author_id,
                                       author_name=self.author_name, ts=self.ts, revision_hash=self.revision_hash)
                self._result.append(revision)
                self.flag_revision = False
                self._rev_count += 1

            if name == 'contributor':
                self.flag_contributor = False

            if name == 'title':
                self.article_name = self._get_character_data()
                if self.article_name not in self.articles_to_parse:
                    self.flag_skip_article = True
                else:
                    self.start = self.df_nominations.loc[self.df_nominations['title'] == self.article_name, 'nomination'].item()
                    self.end = self.df_nominations.loc[self.df_nominations['title'] == self.article_name, 'end_date'].item()
                    self.i += 1
                    print('worked')

            if name == 'timestamp':
                self.ts = ciso8601.parse_datetime(self._get_character_data()).timestamp()


        self._char_buffer = []

        #print(self.flag_skip_article)

    def endDocument(self):
        with open('./res/revision_dict.pkl', 'wb') as f:
            pickle.dump(self._result, f)



if __name__ == '__main__':
    with open('./log/log_revisions.log', 'w') as log_file:
        log_file.write('')
    logging.basicConfig(filename='./log/log_revisions.log', level=logging.DEBUG)
    _, out_file, in_file, control_file = sys.argv
    with gzip.open(in_file) as input_file:
        MyRevisionsHandler(out_file, control_file).parse(input_file)









