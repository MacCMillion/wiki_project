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
from revision import RevisionXML

#import data science utils
import pandas as pd
import numpy as np


class MyRevisionsHandler(ContentHandler):
    """
    Default Skript Configuration:
        ./res/FAC_nomination.csv    (result)
        ./data/FAC.xml              (source)
    """
    def __init__(self, out_file):
        """
        :param out_file:
        """
        self.flag_newpage = False
        self.flag_revision = False
        self.flag_contributer = False

        self.revision = None

        self.article_id = 0
        self.revision_id = 0
        self.article_name = ''
        self.author_id = 0
        self.author_name = ''
        self.registered = False
        self.ts = 0
        self.length = 0
        self.minor = False
        self.commment = ''
        self.revision_hash = ''
        self.revert = False


        self._charBuffer = []
        self._text = ''
        self._result = []
        self._problematic = []

        # debug
        self._name = ''

    def _get_character_data(self):
        data = ''.join(self._charBuffer).strip()
        self._charBuffer = []
        return data

    def parse(self, f):
        xml.sax.parse(f, self)

    def characters(self, content):
        self._charBuffer.append(content)

    def log_status(self):
        return vars(self)

    def log_status(self):
        m = f'Element: {self._name} article_id: {self.article_id},NP: {self.flag_newpage} REV: {self.flag_newpage}, ' \
            f'CONT: {self.flag_contributer} \n{self._text}'
        return m

    def startElement(self, name, attrs):
        self._name = name
        if name == 'page':
            self.flag_newpage = True

        if name == 'contributor':
            self.flag_contributer = True
            self.flag_revision = False

        if name == 'text':
            self.length = attrs['bytes']

        if name == 'revision':
            self.flag_revision = True
            self.flag_newpage = False

    def endElement(self, name):
        self._name = name
        # print(self._name, self._text)
        if name == 'id':
            # logging.debug(self.log_status())
            if self.flag_newpage:
                self._text = self._get_character_data()
                # print('page_id: ', self._text)
                self.article_id = int(self._text)
            elif self.flag_contributer:
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
            logging.debug(f'{self._text}   newpage: {self.flag_newpage}      revision: {self.flag_revision}    contributer {self.flag_contributer}')

        if name == 'revision':
            revision = RevisionXML(page_title=self.article_name, page_id=self.article_id,
                                   revision_id=self.revision_id, author_id=self.author_id,
                                   author_name=self.author_name)
            self._result.append(revision)
            self.flag_revision = False

        if name == 'contributor':
            self.flag_contributer = False

        if name == 'title':
            self.article_name = self._get_character_data()

        if name == 'ip':
            self.author_name = self._get_character_data()

        if name == 'username':
            self.author_name = self._get_character_data()

        if name == 'timestanmp':
            datetime.strptime(self._get_character_data(), '%Y-%m-%dT%H:%M:%SZ')

        if name == 'minor':
            self.minor = True

        if name == 'comment':
            self.commment = True

        if name == 'sha1':
            self.revision_hash = self._get_character_data()
        self._charBuffer = []

    def endDocument(self):
        with open('./res/revision_dict.pkl', 'wb') as f:
            pickle.dump(self._result, f)



if __name__ == '__main__':
    with open('./log/log_revisions.log', 'w') as f:
        f.write('')
    logging.basicConfig(filename='./log/log_revisions.log', level=logging.DEBUG)
    _, out_file, in_file = sys.argv
    MyRevisionsHandler(out_file).parse(in_file)









