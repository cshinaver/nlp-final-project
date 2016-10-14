#!/usr/bin/env python
# scraper.py
# Pulls post data from calendar.nd.edu

import argparse
import json
import logging
import multiprocessing
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)

N_PROCESSES = 1


class Post:
    def __init__(self, description=None, link=None, title=None):
        self.description = description
        self.title = title
        self.link = link

    def __repr__(self):
        return str(self.__dict__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generates json of calendar data'
    )
    parser.add_argument(
        '--first-month',
        type=int,
        required=True,
        help='Left bound of month range (1)'
    )
    parser.add_argument(
        '--last-month',
        type=int,
        required=True,
        help='Right bound of month range (12)'
    )
    parser.add_argument(
        '--first-year',
        type=int,
        required=True,
        help='Left bound of year range (2010)'
    )
    parser.add_argument(
        '--last-year',
        type=int,
        required=True,
        help='Right bound of year range (2016)'
    )
    parser.add_argument(
        '--n-processes',
        type=int,
        required=True,
        help='Number of processes to run processing'
    )
    return parser.parse_args()


def get_post_description(link):
    html_doc = requests.get(link).content
    soup = BeautifulSoup(html_doc)
    description_div = soup.find(class_='eventDescription')
    description = description_div.get_text()
    return description


def get_posts_for_month_and_year(month=None, year=None):
    logging.info('Getting posts for month {} year {}'.format(month, year))
    posts = None
    html_doc = requests.get(
        'http://calendar.nd.edu/events/cal/month/{year}{month}01'.format(
            year=year,
            month=month
        )
    ).content

    soup = BeautifulSoup(html_doc)
    event_list_table = soup.find(class_='eventList')
    rows = event_list_table.find_all('tr')
    all_event_rows = rows[2:]
    event_rows_html = [str(row) for row in all_event_rows]
    with multiprocessing.Pool(N_PROCESSES) as p:
        posts = p.map(get_post_object_for_table_row, event_rows_html)

    return posts


def get_post_object_for_table_row(row):
    row = BeautifulSoup(row)
    td_tags_for_row = row.find_all('td')

    # Ignore row if is a date row
    if 'dateRow' in td_tags_for_row[0]['class']:
        return None

    td_description = td_tags_for_row[1]
    links = td_description.find_all('a')
    event_link = links[2]
    title = event_link.get_text()
    description_link = event_link['href']
    full_link = 'http://calendar.nd.edu' + description_link
    description = get_post_description(full_link)

    post = Post(title=title, link=full_link, description=description)
    return post


def posts_for_year_and_month_range(year, month_range):
    """
    Input: ('2016', (1, 10))
    """
    post_objects = []
    for i in range(month_range[0], month_range[1] + 1):
        month = "".join(["0", str(i)])
        posts = filter(
                    lambda x: x is not None,
                    get_posts_for_month_and_year(month=month, year=year),
                )
        for post in posts:
            data = {
                'title': post.title,
                'link': post.link,
                'description': post.description,
            }
            post_objects.append(data)
    return post_objects

if __name__ == '__main__':
    args = parse_args()
    first_month = args.first_month
    last_month = args.last_month
    first_year = args.first_year
    last_year = args.last_year
    N_PROCESSES = args.n_processes

    posts = []
    for year in range(first_year, last_year + 1):
        posts.extend(
            posts_for_year_and_month_range(year, (first_month, last_month))
        )
    with open('train', 'w') as f:
        f.write(json.dumps(posts))
