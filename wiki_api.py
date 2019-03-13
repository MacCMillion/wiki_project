import os
import sys
import pickle
import re
import csv

import urllib.request
import pywikibot
from revision import RevisionPywii as Revision


""" Contains several alternative to get revision data from Wikipedia, they are non longer used in the final project since the 'subs.dumps' will be used. 
The methods explored here are:
1) directly accessing the wiki api 
2) use pywiki bot to do the job
"""

def get_revisions_api(page_title):
    url = "https://en.wikipedia.org/w/api.php?action=query&format=xml&prop=revisions&rvlimit=500&titles=" + page_title
    revisions = []  # list of all accumulated revisions
    next = ''  # information for the next request
    while True:
        response = urllib.request.urlopen(url + next).read()  # web request
        revisions += re.findall('<rev [^>]*>', response)  # adds all revisions from the current request to the list

        cont = re.search('<continue rvcontinue="([^"]+)"', response)
        if not cont:  # break the loop if 'continue' element missing
            break

        next = "&rvcontinue=" + cont.group(1)  # gets the revision Id from which to start the next request

    return revisions;


def get_revisions_pywikibot(page_title):
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, page_title)
    revisions = page.revisions(content=True)
    page_id = page.pageid
    return page_id, page_title, revisions


def extract_info(page_id, page_title, revisions):
    length_last = 0
    for revision in revisions:
        d = {'page_id' : page_id,
             'page_title' : page_title,
            'revision_id': revision.revid,
             'author_name': revision.user,
             'length': len(revision.text),
             'd_length': abs(length_last - len(revision.text)),
             'ts': revision.timestamp,
             'revision_hash': revision.sha1,
             'minor': revision.minor}
        length_last = d['length']
        Revision(d)
        print(revision)


def aggregate(revisions):
    authors = set()
    minor_count = 0
    ip_count = 0
    for i, revision in enumerate(revisions):
        authors.add(revision.user)
        if revision.minor:
            minor_count += 1
        if revision.anon:
            ip_count += 1
        if revision.rollbacktoken:
            print(revision.rollbacktoken)

    return i, len(authors), minor_count, ip_count


if __name__ == '__main__':
    article = sys.argv[1]
    with open(f'./data/revisions/page_info.csv', 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=';')
        page_id, page_title, revisions_gen = get_revisions_pywikibot(article)
        page_info = [page_id, page_title]
        page_info.extend(aggregate(revisions_gen))
        csv_writer.writerow(page_info)


