#!/usr/bin/env python
# scraper.py
# Pulls post data from calendar.nd.edu

import json
import requests
from bs4 import BeautifulSoup


class Post:
    def __init__(self, description=None, link=None, title=None):
        self.description = description
        self.title = title
        self.link = link


def get_post_description(link):
    pass


def get_posts_for_month_and_year(month=None, year=None):
    posts = []
    html_doc = requests.get(
        'http://calendar.nd.edu/events/cal/month/{year}{month}01/35_All+Events/'.format(
            year=year,
            month=month
        )
    ).content

    soup = BeautifulSoup(html_doc)
    event_list_table = soup.find(class_='eventList')
    rows = event_list_table.find_all('tr')
    all_event_rows = rows[2:]

    for row in all_event_rows:
        td_tags_for_row = row.find_all('td')

        # Ignore row if is a date row
        if 'dateRow' in td_tags_for_row[0]['class']:
            continue

        td_description = td_tags_for_row[1]
        links = td_description.find_all('a')
        event_link = links[2]
        title = event_link.get_text()
        description_link = event_link['href']
        full_link = 'https://calendar.nd.edu' + description_link
        get_post_description(full_link) #TODO Make post description not null

        post = Post(title=title, link=full_link)
        posts.append(post)
    return posts


def posts_for_year_and_month_range(year, month_range):
    """
    Input: ('2016', (1, 10))
    """
    post_objects = []
    for i in range(month_range[0], month_range[1] + 1):
        month = "".join(["0", str(i)])
        posts = get_posts_for_month_and_year(month=month, year=year)
        for post in posts:
            data = {
                'title': post.title,
                'link': post.link,
                'description': post.description,
            }
            post_objects.append(data)
    return post_objects

if __name__ == '__main__':
    print(json.dumps(posts_for_year_and_month_range(2015, (1, 12))))
