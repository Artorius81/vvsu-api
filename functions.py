from flask import request

import requests

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    login = request.json.get('username', 'default')
    return (path + args + login).encode('utf-8')
