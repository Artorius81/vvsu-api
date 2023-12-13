from flask import Flask, jsonify, request
from flask_caching import Cache
import logging

from functions import validate_remote_login, time_table, results, curriculum, my_group

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}


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
    app.run(debug=True)
