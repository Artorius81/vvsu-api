# -*- coding: utf-8 -*-
import json
import asyncio

import requests
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import os
from supabase import create_client, Client
from datetime import datetime

from CONSTANTS import *

supabase: Client = create_client(URL, KEY)


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


def get_wall_posts(group_name):
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
            print(f'Новых постов в группе {group_name} не найдено.')
            return

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
                print('Что-то пошло не так.')
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
                print('Что-то пошло не так.')
