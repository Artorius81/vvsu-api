import requests

REMOTE_API_URL = 'https://api.vvsu.ru/services/api/restlogin'
LOCAL_API_URL = 'http://127.0.0.1:5000/api/results'

# Замените 'ваш_логин' и 'ваш_пароль' на фактические значения
login = '_MalCanita_'
password = 'LOLkeK1687mmm'

# Отправка POST-запроса на удаленный сервер
remote_response = requests.post(REMOTE_API_URL, json={'username': login, 'password': password})
remote_result = remote_response.json()

print(f'Remote Status Code: {remote_response.status_code}')
print('Remote Result:', remote_result)

# Проверка успешности входа на удаленном сервере
if remote_result.get('success', False):
    # Если вход успешен, отправляем данные на локальный сервер
    local_response = requests.post(LOCAL_API_URL, json={'username': login, 'password': password})
    local_result = local_response.json()

    print(f'Local Status Code: {local_response.status_code}')
    print('Local Result:', local_result)
else:
    print('Remote login failed. Skipping local request.')
