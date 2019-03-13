import os
import sys
import pickle
import re
import csv


import urllib.request
import pywikibot
from revision import RevisionPywii as Revision
import numpy as np
import pandas as pd


# Load results of parsing monthly archives
df_FAC = pd.read_csv('./data/FAC_nomination.csv', sep=';', index_col=0, parse_dates=['nomination', 'last_comment'])
print(len(df_FAC))
df_FAC = df_FAC[(np.datetime64('2005')<=df_FAC.nomination) & (df_FAC.nomination<=np.datetime64('2016'))]
print(len(df_FAC))


# Load results of parsing revision history
with open('./res/article_dict.pkl', 'rb') as file:
    ends_dict = pickle.load(file)

df_ends_min = [[i, article, max(dates), min(dates)] for i, (article, dates) in enumerate(ends_dict.items())]
df_ends_min = pd.DataFrame(df_ends_min, columns=['idx', 'title', 'first', 'last'])

# clean article names
df_FAC['title'] = df_FAC.title.str.replace('/archive\d', '')
df_ends_min['title'] = df_ends_min.title.str.replace('/archive\d', '')

# This will produce duplicates, so we have to chose the max and min of these
agg_funcs = {'first': 'min',
             'last' : 'max'}
df_ends_min = df_ends_min.groupby('title').agg(agg_funcs)
df_ends_min.reset_index(inplace=True)

n_FAC = len(df_FAC)
n_ends = len(df_ends_min)

# We only keep the first nomination (simplification)
df_FAC['has_duplicate'] = df_FAC.duplicated(subset='title', keep=False)
print('duplicates:')
print(f'multiple nominations: {sum(df_FAC.has_duplicate)}')
df_FAC = df_FAC.loc[~df_FAC.sort_values('nomination').duplicated(subset='title', keep='first'),]

# Remove articles from FAC that are not in ends
df_merge = pd.merge(df_FAC, df_ends_min, on='title')
n_FAC_nd = len(df_FAC)
print(f'number of nominations: {n_FAC:>20} \nartilcles in ends: {n_ends:>20}'
      f'\nunique articles in nominations: {n_FAC_nd:20} '
      f'\narticles in merged data Frame: {len(df_merge):20}')