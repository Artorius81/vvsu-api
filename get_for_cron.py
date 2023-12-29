import requests


def send_get_request():
    response = requests.get("https://sterling-marmot-naturally.ngrok-free.app/api/vk_parse")
    print(f"Код получен: {response.status_code}")


send_get_request()
