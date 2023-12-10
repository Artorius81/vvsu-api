from flask import Flask, request, jsonify
import requests
import logging
import json

import requests
from lxml import etree

from parse import get_results, get_time_table

app = Flask(__name__)

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

with open('config.json', 'r', encoding='utf-8') as file:
    CONFIG = json.load(file)


def time_table(login, password):
    # Выполнение вашего кода на основе логина и пароля
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


def results(login, password):
    # Выполнение вашего кода на основе логина и пароля
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


def validate_remote_login(login, password):
    # Отправляем запрос на удаленный сервер
    response = requests.post(REMOTE_API_URL, json={'username': login, 'password': password})
    remote_result = response.json()

    # Проверяем, успешен ли вход на удаленном сервере
    if remote_result.get('success', False):
        return True
    else:
        return False


@app.route('/api/results', methods=['POST'])
def api_results():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        # Валидация логина и пароля на удаленном сервере
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

        # Валидация логина и пароля на удаленном сервере
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


if __name__ == '__main__':
    app.run(debug=True)
