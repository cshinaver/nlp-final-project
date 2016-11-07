#!/usr/bin/env python
# scraper.py
# Pulls post data from calendar.nd.edu

import argparse
import json
import logging
import multiprocessing
import os
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)

N_PROCESSES = 1


class Post:
    def __init__(
        self,
        description=None,
        link=None,
        title=None,
        category=None,
    ):
        self.description = description
        self.title = title
        self.link = link
        self.category = category

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
    parser.add_argument(
        '--category-url-file',
        type=str,
        required=True
    )
    parser.add_argument(
        '--out-file',
        type=str,
        required=True
    )
    # parser.add_argument(
    #     '--category-name',
    #     type=str,
    #     required=True
    # )
    return parser.parse_args()


def get_post_description(link):
    html_doc = requests.get(link).content
    soup = BeautifulSoup(html_doc)
    description_div = soup.find(class_='eventDescription')
    if description_div:
        description = description_div.get_text()
        return description
    return None


def get_posts_for_month_and_year(
    month=None,
    year=None,
    category_name=None,
    category_link=None,
):
    logging.info('Getting posts for month {} year {}'.format(month, year))
    posts = None
    link = 'http://calendar.nd.edu/events/cal/month/{year}{month}01/'.format(
        year=year,
        month=month
    )
    link += category_link
    html_doc = requests.get(
        link
    ).content

    soup = BeautifulSoup(html_doc)
    event_list_table = soup.find(class_='eventList')
    rows = event_list_table.find_all('tr')
    all_event_rows = rows[2:]
    event_rows_html = [str(row) for row in all_event_rows]
    with multiprocessing.Pool(N_PROCESSES) as p:
        posts = p.map(get_post_object_for_table_row, event_rows_html)

    for post in posts:
        if post:
            post.category = category_name
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


def posts_for_year_and_month_range(
    year,
    month_range,
    category_name,
    category_link,
):
    """
    Input: ('2016', (1, 10))
    """
    post_objects = []
    for i in range(month_range[0], month_range[1] + 1):
        month = "".join(["0", str(i)])
        posts = filter(
                    lambda x: x is not None,
                    get_posts_for_month_and_year(
                        month=month,
                        year=year,
                        category_name=category_name,
                        category_link=category_link,
                        ),
                )
        for post in posts:
            data = {
                'title': post.title,
                'link': post.link,
                'description': post.description,
                'category': post.category,
            }
            post_objects.append(data)
    return post_objects

if __name__ == '__main__':
    args = parse_args()
    first_month = args.first_month
    last_month = args.last_month
    first_year = args.first_year
    last_year = args.last_year
    # category_name = args.category_name
    category_file = args.category_url_file
    out_file = args.out_file
    N_PROCESSES = args.n_processes

    posts = []

    url_file = open(category_file,"r")
    for category_url in url_file.readlines(): 
        category_link = category_url.rstrip()
        category_name = category_url.rstrip()
        for year in range(first_year, last_year + 1):
            posts.extend(
                posts_for_year_and_month_range(
                    year,
                    (first_month, last_month),
                    category_name,
                    category_link
                )
            )
        current_posts = []
        if os.path.isfile(out_file):
            with open(out_file, 'r') as f:
                current_posts = json.loads(f.read())
        current_posts.extend(posts)

        with open(out_file, 'w') as f:
            f.write(json.dumps(current_posts))