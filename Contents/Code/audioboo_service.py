# -*- coding: utf-8 -*-

import json
import re
from collections import OrderedDict
from http_service import HttpService

class AudiobooService(HttpService):
    URL = 'http://audioboo.ru'

    def available(self):
        return True

    def get_letters(self):
        list = []

        document = self.fetch_document(self.URL)

        items = document.xpath('//div[@class="content"]/div/div/a[@class="alfavit"]')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content().upper()

            list.append({'path': href, 'name': name})

        return list

    def get_authors_by_letter(self, path):
        groups = OrderedDict()

        document = self.fetch_document(self.URL + path)

        items = document.xpath('//div[@class="full-news-content"]/div/a')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content()

            group_name = name[0:3].upper()

            if group_name not in groups.keys():
                group = []

                groups[group_name] = group

            groups[group_name].append({'path': href, 'name': name})

        return groups

    def get_author_books(self, url):
        list = []

        document = self.fetch_document(url)

        items = document.xpath('//div[@class="biography-main"]')

        for item in items:
            name = item.find('div/[@class="biography-title"]/h2/a').text
            href = item.find('div/div/[@class="biography-image"]/a').get("href")
            thumb = item.find('div/div/[@class="biography-image"]/a/img').get("src")
            content = item.find('div/[@class="biography-content"]/div').text
            rating = item.find('div[@class="biography-content"]/div/div[@class="rating"]/ul/li').text

            list.append({'path': href, 'name': name, 'thumb': thumb, 'content': content, 'rating': rating})

        return list

    def get_playlist_url(self, url):
        document = self.fetch_document(url)

        return document.xpath('//object')[0].get("data")

    def get_audio_tracks(self, url):
        document = self.fetch_document(url)

        scripts = document.xpath('//script')

        script = scripts[len(scripts)-1].text_content()

        index1 = script.find("Play('jw6',")
        index2 = script.find('{"start":0,')

        content = script[index1 + 10:index2-1].strip()

        content = content[2:len(content)-1].strip()

        return json.loads(content)

    def search(self, query, page=1):
        url = self.URL + "/engine/ajax/search.php"

        headers = {'X-Requested-With': 'XMLHttpRequest'}

        content = self.http_request(url, headers=headers, data={'query': query}, method='POST').read()

        document = self.to_document(content)

        list = []

        items = document.xpath('a')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content().upper()

            list.append({'path': href, 'name': name})

        return list

    def convert_track_duration(self, s):
        tokens = str(s).split('.')

        result = []

        for token in tokens:
            data = re.search('(\d+)', token)

            if data:
                result.append(data.group(0))

        minutes = int(result[0])

        if len(result) > 1:
            seconds = int(result[1])
        else:
            seconds = 0

        return minutes * 60 + seconds