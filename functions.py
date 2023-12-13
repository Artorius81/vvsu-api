from flask import request

import requests

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'


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
