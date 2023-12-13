from flask import Flask, jsonify, request
from flask_caching import Cache

import requests

from lxml import etree
import logging

from functions import validate_remote_login, make_cache_key
from parse import get_results, get_time_table, get_curriculum, get_group

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}


@cache.cached(timeout=28800, key_prefix=make_cache_key)
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


@cache.cached(timeout=28800, key_prefix=make_cache_key)
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


@cache.cached(timeout=28800, key_prefix=make_cache_key)
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


@cache.cached(timeout=28800, key_prefix=make_cache_key)
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


@app.route('/api/results', methods=['POST'])
def api_results():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = results(login, password)
        else:
            result = {
                'status': 'error',
                'message': 'Неверный логин или пароль.'
            }
    else:
        result = {
            'status': 'error',
            'message': 'Отсутствует логин или пароль в запросе.'
        }

    return jsonify(result)


@app.route('/api/time_table', methods=['POST'])
def api_time_table():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = time_table(login, password)
        else:
            result = {
                'status': 'error',
                'message': 'Неверный логин или пароль.'
            }
    else:
        result = {
            'status': 'error',
            'message': 'Отсутствует логин или пароль в запросе.'
        }

    return jsonify(result)


@app.route('/api/curriculum', methods=['POST'])
def api_curriculum():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = curriculum(login, password)
        else:
            result = {
                'status': 'error',
                'message': 'Неверный логин или пароль.'
            }
    else:
        result = {
            'status': 'error',
            'message': 'Отсутствует логин или пароль в запросе.'
        }

    return jsonify(result)


@app.route('/api/my_group', methods=['POST'])
def api_my_group():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = my_group(login, password)
        else:
            result = {
                'status': 'error',
                'message': 'Неверный логин или пароль.'
            }
    else:
        result = {
            'status': 'error',
            'message': 'Отсутствует логин или пароль в запросе.'
        }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=False)
