#!/usr/bin/python3

import sys
import re
import argparse
import logging
import urllib.request
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

def check_has_next_page(soup):
    if not soup.find_all('a', {'class': 'next_page'}):
        return False

    return not soup.find_all('a', {'class': 'next_page disabled'})

def find_subpage_repos(params):
    repos = []
    uri_params = list(map(lambda key: f'{quote(key)}={quote(params[key])}', params))
    prefix_url = 'https://github.com'
    url = urljoin(prefix_url, f'search?{"&".join(uri_params)}')

    with urllib.request.urlopen(url) as github_content:
        soup = BeautifulSoup(github_content.read(), 'html.parser')

        for repo_node in soup.find_all('a', attrs={'href': re.compile(r'^\/[^\/]+\/[^?^&^\/]+$')}):
            href = repo_node.get('href')

            if re.match(r'^\/(topics|features)\/', href):
                continue

            repo_url = urljoin(prefix_url, href)
            repos.append(repo_url)

        return (check_has_next_page(soup), repos)

def find_repos():
    try:
        logging.basicConfig(encoding='utf-8', level=logging.INFO)

        parser = argparse.ArgumentParser()
        parser.add_argument('reponame', type=str, nargs=1)
        parser.add_argument('lang', type=str, nargs='?')
        parser.add_argument('-c', help='max subpages count', type=int, nargs='?', default=1, choices=range(1, 10))
        args = parser.parse_args()

        params = {'q': args.reponame[0], 'type': 'Repositories'}

        if args.lang:
            params['l'] = args.lang

        page_number = 1

        while True:
            (has_next_page, repos) = find_subpage_repos(params)
            print('\n'.join(repos))

            if not has_next_page:
                break

            if args.c == page_number:
                break

            page_number += 1
            params['p'] = str(page_number)

    except (SystemExit, argparse.ArgumentError):
        pass
    except BaseException as ex:
        logging.critical(ex)

find_repos()
