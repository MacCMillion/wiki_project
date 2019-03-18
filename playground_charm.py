import os
import sys
import pickle
import re
import csv


import urllib.request
#import pywikibot
from revision import RevisionPywii as Revision
import numpy as np
import pandas as pd

'''
def get_archives(filename, pattern):
    """ Retrives the links to the monthly FA-Archives"""

    # Extract links from Html document
    with open(filename) as file:
        links_to_archive = []
        for line in file:
            matcher = re.search(pattern, line)
            if matcher:
                links_to_archive.append(matcher.group(1))

    # Remove links to archives from before 2005 and after 2016
    year_list = ['2003', '2004', '2017', '2018']
    links_to_archive = [link for year in year_list for link in links_to_archive if not year in link]
    return links_to_archive


# sucessful nominations
pattern_featured = "(Wikipedia:Featured_article_candidates/Featured_log/.*?)\""
with open('./data/FA_archives.txt', 'w') as f:
    for archive in get_archives('data/FAArchive.html', pattern_featured):
        f.write(archive + '\n')
'''

class SimpleClass:

    def __init__(self, in_file, out_file):
        self._in_file = in_file
        self.out_file = out_file

    def do_smth(self):
        print(self._in_file)

if __name__ == '__main__':
    _, in_file, out_file = sys.argv
    sc = SimpleClass(in_file, out_file)
    sc.do_smth()
