import pandas as pd
import numpy as np
import pickle

from collections import defaultdict
from itertools import chain
import re
# './data/FAC_nomination.csv'

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
    year_list = ['2003', '2004', '2017', '2018', '2019']
    res = []
    for link in links_to_archive:
        if not any([year in link for year in year_list]):
            res.append(link)
    return res


def merge(file_nominations, file_ends):
    # Load results of parsing monthly archives
    df_FAC = pd.read_csv(file_nominations, sep=';', index_col=0, parse_dates=['date_nomination', 'date_last_comment'])
    df_FAC = df_FAC[(np.datetime64('2005') <= df_FAC.date_nomination) & (df_FAC.date_nomination <= np.datetime64('2016'))]

    # Load results of parsing revision history
    with open(file_ends, 'rb') as file:
        ends_dict = pickle.load(file)

    # convert revision history from dictionary to pd.DataFrame
    df_ends = [[i, article, dates] for i, (article, dates) in enumerate(ends_dict.items())]
    df_ends = pd.DataFrame(df_ends, columns=['idx', 'title', 'dates'])

    # clean article names
    df_FAC['title'] = df_FAC.title.str.replace('/archive\d', '')  # These are actually unique nominations
    df_ends['title'] = df_ends.title.str.replace('/archive\d', '')  # These likely not

    # Append all dates
    # This will produce duplicates,
    df_ends = df_ends.groupby('title').agg({'dates': 'sum'})

    n_FAC = len(df_FAC)
    n_ends = len(df_ends)

    # We only keep the first nomination (simplification)
    df_FAC['has_duplicate'] = df_FAC.duplicated(subset='title', keep=False)
    print(f'multiple nominations: {sum(df_FAC.has_duplicate)}')
    df_FAC = df_FAC.loc[~df_FAC.sort_values('date_nomination').duplicated(subset='title', keep='first'),]

    # merge
    df_merge = pd.merge(df_FAC, df_ends, on='title')
    n_FAC_nd = len(df_FAC)
    print(f'number of nominations: {n_FAC:>20} \nartilcles in ends: {n_ends:>20}'
          f'\nunique articles in nominations: {n_FAC_nd:10} '
          f'\narticles in merged data Frame: {len(df_merge):15}')

    return df_merge


def decide_end(df_merge):
    with open('./data/FAC_ends.pkl', 'rb') as file:
        ends_dict = pickle.load(file)

    res = defaultdict(list)
    for article, dates in ends_dict.items():
        article = re.sub('/archive\d', '', article)
        dates = np.array([np.datetime64(date) for date in dates])
        res[article].append(dates)
    ends_dict = res

    # convert pd.DataFrame to dict
    FAC_dict = {k: np.datetime64(v) for k, v in df_merge[['title', 'date_last_comment']].values}
    print(len(FAC_dict), len(ends_dict))

    new_dict = {}
    for article, last_date in FAC_dict.items():
        two_weeks_later = last_date + np.timedelta64(2, 'W')
        dates = list(chain.from_iterable(ends_dict[article]))  # ensure list is faltened
        dates = [date for date in dates if date < two_weeks_later]
        dates.append(last_date)
        if dates:
            new_date = max(dates)
        else:
            new_date = last_date
            print(f'No date (< 2W) found for article: {article}')
        new_dict[article] = max(new_date, last_date)

    df_new = pd.DataFrame({'title': list(new_dict.keys()), 'end_date': list(new_dict.values())})
    df_merge = pd.merge(df_merge, df_new, on='title')
    df_merge['start_date'] = df_merge['date_nomination'] - np.timedelta64(2, 'W')
    return df_merge
