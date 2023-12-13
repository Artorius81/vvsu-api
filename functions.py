from flask import request
from vvsu_api_endpoint import cache

import requests
from lxml import etree

from parse import get_time_table, get_curriculum, get_group, get_results

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'

CONFIG = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    login = request.json.get('username', 'default')
    return (path + args + login).encode('utf-8')


def validate_remote_login(login, password):
    response = requests.post(REMOTE_API_URL, json={'username': login, 'password': password})
    remote_result = response.json()

    if remote_result.get('success', False):
        return True
    else:
        return False


@cache.cached(timeout=300, key_prefix=make_cache_key)
def time_table(login, password):
    url = 'https://cabinet.vvsu.ru/sign-in'
    headers = {
        'User-Agent': CONFIG['USER_AGENT']
    }

    with requests.Session() as session:
        session.headers = headers
        response = session.get(url)

        tree = etree.fromstring(response.text, etree.HTMLParser())
        challenge = tree.xpath('//input[@name="challenge"]/@value')[0]
        post_url = f'https://www.vvsu.ru/openid/login?/login&login_challenge={challenge}'
        data = {
            'challenge': challenge,
            'login': login,
            'password': password
        }
        response = session.post(post_url, data)

        redirect_url = response.json()['location']
        session.get(redirect_url)

        response = session.get('https://cabinet.vvsu.ru/time-table/')
        time_table_html = response.text

        return get_time_table(time_table_html)


@cache.cached(timeout=300, key_prefix=make_cache_key)
def curriculum(login, password):
    url = 'https://cabinet.vvsu.ru/sign-in'
    headers = {
        'User-Agent': CONFIG['USER_AGENT']
    }

    with requests.Session() as session:
        session.headers = headers
        response = session.get(url)

        tree = etree.fromstring(response.text, etree.HTMLParser())
        challenge = tree.xpath('//input[@name="challenge"]/@value')[0]
        post_url = f'https://www.vvsu.ru/openid/login?/login&login_challenge={challenge}'
        data = {
            'challenge': challenge,
            'login': login,
            'password': password
        }
        response = session.post(post_url, data)

        redirect_url = response.json()['location']
        session.get(redirect_url)

        response = session.get('https://cabinet.vvsu.ru/curriculum/')
        curriculum_html = response.text

        return get_curriculum(curriculum_html)


@cache.cached(timeout=300, key_prefix=make_cache_key)
def my_group(login, password):
    url = 'https://cabinet.vvsu.ru/sign-in'
    headers = {
        'User-Agent': CONFIG['USER_AGENT']
    }

    with requests.Session() as session:
        session.headers = headers
        response = session.get(url)

        tree = etree.fromstring(response.text, etree.HTMLParser())
        challenge = tree.xpath('//input[@name="challenge"]/@value')[0]
        post_url = f'https://www.vvsu.ru/openid/login?/login&login_challenge={challenge}'
        data = {
            'challenge': challenge,
            'login': login,
            'password': password
        }
        response = session.post(post_url, data)

        redirect_url = response.json()['location']
        session.get(redirect_url)

        response = session.get('https://cabinet.vvsu.ru/group/')
        my_group_html = response.text

        return get_group(my_group_html)


@cache.cached(timeout=300, key_prefix=make_cache_key)
def results(login, password):
    url = 'https://cabinet.vvsu.ru/sign-in'
    headers = {
        'User-Agent': CONFIG['USER_AGENT']
    }

    with requests.Session() as session:
        session.headers = headers
        response = session.get(url)

        tree = etree.fromstring(response.text, etree.HTMLParser())
        challenge = tree.xpath('//input[@name="challenge"]/@value')[0]
        post_url = f'https://www.vvsu.ru/openid/login?/login&login_challenge={challenge}'
        data = {
            'challenge': challenge,
            'login': login,
            'password': password
        }
        response = session.post(post_url, data)

        redirect_url = response.json()['location']
        session.get(redirect_url)

        response = session.get('https://cabinet.vvsu.ru/results/')
        results_html = response.text

        return get_results(results_html)
