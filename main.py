# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask_caching import Cache

from lxml import etree
import logging

import json
import asyncio

import requests
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import os
from supabase import create_client, Client
from datetime import datetime

from CONSTANTS import *

from functions import validate_remote_login, make_cache_key
from parse import get_results, get_time_table, get_curriculum, get_group, get_main, get_grants, get_payment, \
    get_dormitory, get_internet_pay, get_traffic, get_projects, get_forms

supabase: Client = create_client(URL, KEY)

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

group_name = 'vvsu_dv'


# GIGA
def giga(text, path, credentials):
    PAYLOAD = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Представь, что ты - копирайтер. Твоя задача вычленить несколько слов из текста (СТРОГО НЕ БОЛЕЕ 8 СЛОВ) и составить из них заголовок, исходя из "
                        "представленного текста.",
            ),
            Messages(
                role=MessagesRole.ASSISTANT,
                content="Как я могу помочь вам?",
            ),
            Messages(
                role=MessagesRole.USER,
                content=f"Вычлени главную информацию и составь привлекательный для аудитории заголовок по тексту. Помни, что заголовок должен быть "
                        f"СТРОГО НЕ БОЛЬШЕ чем 8 слов. Вот текст: {text}",
            ),
        ],
        update_interval=0.1,
    )

    async def main() -> object:
        async with GigaChat(
                credentials=credentials,
                ca_bundle_file=path) as giga:
            async for chunk in giga.astream(PAYLOAD):
                return chunk.choices[0].delta.content

    if __name__ == '__main__':
        result = asyncio.run(main())
        return result


@cache.cached(timeout=43200, key_prefix=make_cache_key)
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


@cache.cached(timeout=43200, key_prefix=make_cache_key)
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


@cache.cached(timeout=43200, key_prefix=make_cache_key)
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


@cache.cached(timeout=43200, key_prefix=make_cache_key)
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


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def grants(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/payment/add/')
        grants_html = response.text

        return get_grants(grants_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def payment(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/payment/')
        payment_html = response.text

        return get_payment(payment_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def dormitory(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/payment/domitory/')
        dormitory_html = response.text

        return get_dormitory(dormitory_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def internet_pay(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/payment/internet/')
        internet_pay_html = response.text

        return get_internet_pay(internet_pay_html)


@cache.cached(timeout=0, key_prefix=make_cache_key)
def my_main(login, password):
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

        response = session.get('https://cabinet.vvsu.ru')
        main_html = response.text

        return get_main(main_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def traffic(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/internet/traffic/')
        traffic_html = response.text

        return get_traffic(traffic_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def projects(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/tasks/choiceproject/')
        projects_html = response.text

        return get_projects(projects_html)


@cache.cached(timeout=43200, key_prefix=make_cache_key)
def forms(login, password):
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

        response = session.get('https://cabinet.vvsu.ru/tasks/anketa/')
        forms_html = response.text

        return get_forms(forms_html)


def vk_parser(group_name):
    url = f'https://api.vk.com/method/wall.get?domain={group_name}&count=15&access_token={TOKEN}&v=5.137'
    req = requests.get(url)
    src = req.json()

    if os.path.exists(f'{group_name}'):
        print(f'Директория группы {group_name} существует.')
    else:
        os.mkdir(group_name)

    with open(f'{group_name}/{group_name}.json', 'w', encoding='utf-8') as file:
        json.dump(src, file, indent=4, ensure_ascii=False)

    existed_posts_file_path = f'{group_name}/existed_posts.txt'

    if os.path.exists(existed_posts_file_path):
        print(f'Файл с id постов группы {group_name} найден.')

        with open(existed_posts_file_path, 'r') as existed_posts_file:
            existed_posts = set(int(line.strip()) for line in existed_posts_file)

        new_posts_id = []
        posts = src['response']['items']

        for new_post_id in posts:
            new_post_id = new_post_id["id"]
            if new_post_id not in existed_posts:
                new_posts_id.append(new_post_id)

        if not new_posts_id:
            return f'Новых постов в группе {group_name} не найдено.'

        print(f'Найдено {len(new_posts_id)} новых постов в группе {group_name}.')

        with open(existed_posts_file_path, 'a') as existed_posts_file:
            for post_id in new_posts_id:
                existed_posts_file.write(str(post_id) + '\n')

        for post_id in new_posts_id:
            # Остальной код для обработки нового поста
            post = next(post for post in posts if post['id'] == post_id)

            post_date = post['date']
            post_date = datetime.fromtimestamp(post_date)
            print(f'Пост с id {post_id}\n')
            print(f'Дата поста {post_date}\n')

            post_text = None
            post_title = None
            post_photos = []
            docs = []
            links = []
            audios = []
            videos = []

            try:
                # если пост это репост с другого поста
                if 'copy_history' in post:
                    repost = post['copy_history'][0]
                    # проверка есть ли текст в посте
                    if 'text' in repost:
                        post_text = repost['text']
                        post_title = giga(post_text, PATH, CREDENTIALS)
                        # print("Post text:", post_text)
                        # print("Post Title:", post_title)

                    #  проверка есть ли прикрепленные файлы в том посте
                    if 'attachments' in repost:
                        for attachment in repost['attachments']:
                            if attachment['type'] == 'photo':
                                if len(attachment) == 1:
                                    sizes = attachment[0]['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])
                                else:
                                    sizes = attachment['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])

                            #  проверка есть ли прикрепленные документы
                            elif attachment['type'] == 'doc':
                                doc_title = attachment['doc']['title']
                                docs.append(doc_title)
                                doc_url = attachment['doc']['url']
                                docs.append(doc_url)

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'link':
                                link_title = attachment['link']['title']
                                links.append(link_title)
                                link_url = attachment['link']['url']
                                links.append(link_url)

                            #  проверка есть ли прикреплённые аудио
                            elif attachment['type'] == 'audio':
                                audio_artist = attachment['audio']['artist']
                                audios.append(audio_artist)
                                audio_title = attachment['audio']['title']
                                audios.append(audio_title)
                                audio_url = attachment['audio']['url']
                                audios.append(audio_url)

                            # проверка есть ли видео в посте
                            elif attachment['type'] == 'video':
                                video_access_key = attachment['video']['access_key']
                                video_post_id = attachment['video']['id']
                                video_owner_id = attachment['video']['owner_id']

                                video_get_url = f'https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={TOKEN}&v=5.137'
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_title = res['response']['items'][0]['title']
                                videos.append(video_title)
                                video_url = res['response']['items'][0]['player']
                                videos.append(video_url)

                                for item in res['response']['items'][0]['image']:
                                    if (item['width'] and item['height']) == (
                                            res['response']['items'][0]['width'] and res['response']['items'][0][
                                        'height']):
                                        video_presplash = item['url']
                                        videos.append(video_presplash)
                                    elif (item['width']) == 720:
                                        video_presplash = item['url']
                                        post_photos.append(video_presplash)
                        # print("Photos:", post_photos)
                        # print("Docs:", docs)
                        # print("Links:", links)
                        # print("Audios:", audios)
                        # print("Videos:", videos)
                    table_data = (supabase.table("vkvvguposts")
                                  .insert(
                        {"created_at": f"{post_date}",
                         "title": f"{post_title}",
                         "text": f"{post_text}",
                         "image": f"{post_photos}",
                         "docs": f"{docs}",
                         "links": f"{links}",
                         "audios": f"{audios}",
                         "videos": f"{videos}",
                         }
                    )
                                  .execute())
                    assert len(table_data.data) > 0
                    print("Всё гуд!")
                # если это просто пост
                else:
                    if 'text' in post:  # проверка есть ли текст в посте
                        post_text = post['text']
                        post_title = giga(post_text, PATH, CREDENTIALS)
                        # print("Post text:", post_text)
                        # print("Post Title:", post_title)
                    # если это не репост другого поста
                    if 'attachments' in post:  # проверка есть ли какие-либо прикреплённые файлы
                        for attachment in post['attachments']:
                            if attachment['type'] == 'photo':
                                if len(attachment) == 1:  # проверяем если одно фото
                                    sizes = attachment[0]['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])
                                else:  # если несколько фото
                                    sizes = attachment['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'doc':
                                doc_title = attachment['doc']['title']
                                docs.append(doc_title)
                                doc_url = attachment['doc']['url']
                                docs.append(doc_url)

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'link':
                                link_title = attachment['link']['title']
                                links.append(link_title)
                                link_url = attachment['link']['url']
                                links.append(link_url)

                            #  проверка есть ли прикреплённые аудио
                            elif attachment['type'] == 'audio':
                                audio_artist = attachment['audio']['artist']
                                audios.append(audio_artist)
                                audio_title = attachment['audio']['title']
                                audios.append(audio_title)
                                audio_url = attachment['audio']['url']
                                audios.append(audio_url)

                            #  проверка есть ли видео в посте
                            elif attachment['type'] == 'video':
                                video_access_key = attachment['video']['access_key']
                                video_post_id = attachment['video']['id']
                                video_owner_id = attachment['video']['owner_id']

                                video_get_url = f'https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={TOKEN}&v=5.137'
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_title = res['response']['items'][0]['title']
                                videos.append(video_title)
                                video_url = res['response']['items'][0]['player']
                                videos.append(video_url)

                                for item in res['response']['items'][0]['image']:
                                    if (item['width'] and item['height']) == (
                                            res['response']['items'][0]['width'] and res['response']['items'][0][
                                        'height']):
                                        video_presplash = item['url']
                                        videos.append(video_presplash)
                                    elif (item['width']) == 720:
                                        video_presplash = item['url']
                                        post_photos.append(video_presplash)
                        # print("Photos:", post_photos)
                        # print("Docs:", docs)
                        # print("Links:", links)
                        # print("Audios:", audios)
                        # print("Videos:", videos)
                    table_data = (supabase.table("vkvvguposts")
                                  .insert(
                        {"created_at": f"{post_date}",
                         "title": f"{post_title}",
                         "text": f"{post_text}",
                         "image": f"{post_photos}",
                         "docs": f"{docs}",
                         "links": f"{links}",
                         "audios": f"{audios}",
                         "videos": f"{videos}",
                         }
                    )
                                  .execute())
                    assert len(table_data.data) > 0
                    print("Всё гуд!")
            except Exception:
                return 'Что-то пошло не так.'
        return "Всё гуд!"
    else:
        print(f'Файла с id постов группы {group_name} не найдено.')
        with open(existed_posts_file_path, 'w') as existed_posts_file:
            for post in src['response']['items']:
                post_id = post["id"]
                existed_posts_file.write(str(post_id) + '\n')

        for post in src['response']['items']:
            post_id = post["id"]
            # Остальной код для обработки нового поста
            post_date = post['date']
            post_date = datetime.fromtimestamp(post_date)
            print(f'Пост с id {post_id}\n')
            print(f'Дата поста {post_date}\n')

            post_text = None
            post_title = None
            post_photos = []
            docs = []
            links = []
            audios = []
            videos = []

            try:
                # если пост это репост с другого поста
                if 'copy_history' in post:
                    repost = post['copy_history'][0]
                    # проверка есть ли текст в посте
                    if 'text' in repost:
                        post_text = repost['text']
                        post_title = giga(post_text, PATH, CREDENTIALS)
                        # print("Post text:", post_text)
                        # print("Post Title:", post_title)

                    #  проверка есть ли прикрепленные файлы в том посте
                    if 'attachments' in repost:
                        for attachment in repost['attachments']:
                            if attachment['type'] == 'photo':
                                if len(attachment) == 1:
                                    sizes = attachment[0]['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])
                                else:
                                    sizes = attachment['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])

                            #  проверка есть ли прикрепленные документы
                            elif attachment['type'] == 'doc':
                                doc_title = attachment['doc']['title']
                                docs.append(doc_title)
                                doc_url = attachment['doc']['url']
                                docs.append(doc_url)

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'link':
                                link_title = attachment['link']['title']
                                links.append(link_title)
                                link_url = attachment['link']['url']
                                links.append(link_url)

                            #  проверка есть ли прикреплённые аудио
                            elif attachment['type'] == 'audio':
                                audio_artist = attachment['audio']['artist']
                                audios.append(audio_artist)
                                audio_title = attachment['audio']['title']
                                audios.append(audio_title)
                                audio_url = attachment['audio']['url']
                                audios.append(audio_url)

                            # проверка есть ли видео в посте
                            elif attachment['type'] == 'video':
                                video_access_key = attachment['video']['access_key']
                                video_post_id = attachment['video']['id']
                                video_owner_id = attachment['video']['owner_id']

                                video_get_url = f'https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={TOKEN}&v=5.137'
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_title = res['response']['items'][0]['title']
                                videos.append(video_title)
                                video_url = res['response']['items'][0]['player']
                                videos.append(video_url)

                                for item in res['response']['items'][0]['image']:
                                    if (item['width'] and item['height']) == (
                                            res['response']['items'][0]['width'] and res['response']['items'][0][
                                        'height']):
                                        video_presplash = item['url']
                                        videos.append(video_presplash)
                                    elif (item['width']) == 720:
                                        video_presplash = item['url']
                                        post_photos.append(video_presplash)
                        # print("Photos:", post_photos)
                        # print("Docs:", docs)
                        # print("Links:", links)
                        # print("Audios:", audios)
                        # print("Videos:", videos)
                    table_data = (supabase.table("vkvvguposts")
                                  .insert(
                        {"created_at": f"{post_date}",
                         "title": f"{post_title}",
                         "text": f"{post_text}",
                         "image": f"{post_photos}",
                         "docs": f"{docs}",
                         "links": f"{links}",
                         "audios": f"{audios}",
                         "videos": f"{videos}",
                         }
                    )
                                  .execute())
                    assert len(table_data.data) > 0
                    print("Всё гуд!")
                # если это просто пост
                else:
                    if 'text' in post:  # проверка есть ли текст в посте
                        post_text = post['text']
                        post_title = giga(post_text, PATH, CREDENTIALS)
                        # print("Post text:", post_text)
                        # print("Post Title:", post_title)
                    # если это не репост другого поста
                    if 'attachments' in post:  # проверка есть ли какие-либо прикреплённые файлы
                        for attachment in post['attachments']:
                            if attachment['type'] == 'photo':
                                if len(attachment) == 1:  # проверяем если одно фото
                                    sizes = attachment[0]['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])
                                else:  # если несколько фото
                                    sizes = attachment['photo']['sizes']
                                    for size in sizes:
                                        if size['type'] == 'r':  # берём лучшее качество
                                            post_photos.append(size['url'])

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'doc':
                                doc_title = attachment['doc']['title']
                                docs.append(doc_title)
                                doc_url = attachment['doc']['url']
                                docs.append(doc_url)

                            #  проверка есть ли прикреплённые ссылки
                            elif attachment['type'] == 'link':
                                link_title = attachment['link']['title']
                                links.append(link_title)
                                link_url = attachment['link']['url']
                                links.append(link_url)

                            #  проверка есть ли прикреплённые аудио
                            elif attachment['type'] == 'audio':
                                audio_artist = attachment['audio']['artist']
                                audios.append(audio_artist)
                                audio_title = attachment['audio']['title']
                                audios.append(audio_title)
                                audio_url = attachment['audio']['url']
                                audios.append(audio_url)

                            #  проверка есть ли видео в посте
                            elif attachment['type'] == 'video':
                                video_access_key = attachment['video']['access_key']
                                video_post_id = attachment['video']['id']
                                video_owner_id = attachment['video']['owner_id']

                                video_get_url = f'https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={TOKEN}&v=5.137'
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_title = res['response']['items'][0]['title']
                                videos.append(video_title)
                                video_url = res['response']['items'][0]['player']
                                videos.append(video_url)

                                for item in res['response']['items'][0]['image']:
                                    if (item['width'] and item['height']) == (
                                            res['response']['items'][0]['width'] and res['response']['items'][0][
                                        'height']):
                                        video_presplash = item['url']
                                        videos.append(video_presplash)
                                    elif (item['width']) == 720:
                                        video_presplash = item['url']
                                        post_photos.append(video_presplash)
                        # print("Photos:", post_photos)
                        # print("Docs:", docs)
                        # print("Links:", links)
                        # print("Audios:", audios)
                        # print("Videos:", videos)
                        table_data = (supabase.table("vkvvguposts")
                                      .insert(
                            {"created_at": f"{post_date}",
                             "title": f"{post_title}",
                             "text": f"{post_text}",
                             "image": f"{post_photos}",
                             "docs": f"{docs}",
                             "links": f"{links}",
                             "audios": f"{audios}",
                             "videos": f"{videos}",
                             }
                        )
                                      .execute())
                        assert len(table_data.data) > 0
                        print("Всё гуд!")
            except Exception:
                return 'Что-то пошло не так.'
        return "Всё гуд!"


@app.route('/api/main_info', methods=['POST'])
def api_main():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        result = my_main(login, password)
    else:
        result = {
            'status': 'error',
            'message': 'Отсутствует логин или пароль в запросе.'
        }

    return jsonify(result)


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


@app.route('/api/payment', methods=['POST'])
def api_payment():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = payment(login, password)
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


@app.route('/api/payment/grants', methods=['POST'])
def api_grants():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = grants(login, password)
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


@app.route('/api/payment/dormitory', methods=['POST'])
def api_dormitory():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = dormitory(login, password)
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


@app.route('/api/payment/internet', methods=['POST'])
def api_internet_pay():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = internet_pay(login, password)
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


@app.route('/api/internet/traffic', methods=['POST'])
def api_internet_traffic():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = traffic(login, password)
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


@app.route('/api/tasks/forms', methods=['POST'])
def api_forms():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = forms(login, password)
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


@app.route('/api/tasks/projects', methods=['POST'])
def api_projects():
    data = request.get_json()

    if 'username' in data and 'password' in data:
        login = data['username']
        password = data['password']

        if validate_remote_login(login, password):
            result = projects(login, password)
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


@app.route('/api/vk_parse', methods=['GET'])
def api_vk_parse():
    return vk_parser(group_name)


if __name__ == '__main__':
    app.run(port=8888)
