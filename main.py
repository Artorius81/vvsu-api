import logging
import json

import requests
from lxml import etree

from parse import get_time_table, get_results


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


with open('config.json', 'r', encoding='utf-8') as file:
    CONFIG = json.load(file)


if __name__ == '__main__':
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
            'login': CONFIG["LOGIN"],
            'password': CONFIG["PASSWORD"]
        }
        response = session.post(post_url, data)

        redirect_url = response.json()['location']
        session.get(redirect_url)

        response = session.get('https://cabinet.vvsu.ru/time-table/')
        time_table_html = response.text

        response = session.get('https://cabinet.vvsu.ru/results/')
        results_html = response.text

        time_table = get_time_table(time_table_html)
        results = get_results(results_html)
        # with open('time_table.json', 'w', encoding='utf-8') as file:
        #     json.dump(time_table, file, indent=4, ensure_ascii=False)
        # with open('results.json', 'w', encoding='utf-8') as file:
        #     json.dump(results, file, indent=4, ensure_ascii=False)
