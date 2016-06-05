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
        data = []

        document = self.fetch_document(self.URL)

        items = document.xpath('//div[@class="content"]/div/div/a[@class="alfavit"]')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content().upper()

            data.append({'path': href, 'name': name})

        return data

    def get_authors_by_letter(self, path):
        groups = OrderedDict()

        document = self.fetch_document(self.URL + path)

        items = document.xpath('//div[@class="full-news-content"]/div/a')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content()

            if name[0:5] == 'ALIAS':
                continue

            group_name = name[0:3].upper()

            if group_name not in groups.keys():
                group = []

                groups[group_name] = group

            groups[group_name].append({'path': href, 'name': name})

        # sum = 0
        # for name in groups:
        #     print name + ": " + str(len(groups[name]))
        #     sum += len(groups[name])
        #
        # print sum

        return self.merge_small_groups(groups)

        # sum = 0
        # for new_group in new_groups:
        #     print new_group
        #     sum2 = 0
        #     for name in new_group:
        #         print name + ": " + str(len(groups[name]))
        #         sum += len(groups[name])
        #         sum2 += len(groups[name])
        #
        #     print sum2
        #
        # print sum

        # for new_group in new_groups:
        #     print(len(new_group))

    def merge_small_groups(self, groups):
        # merge groups into bigger groups with size ~ 20 records

        classifier = []

        group_size = 0
        classifier.append([])
        index = 0

        for group_name in groups:
            group_weight = len(groups[group_name])
            group_size += group_weight

            if group_size > 20:
                group_size = 0
                classifier.append([])
                index = index+1

            classifier[index].append(group_name)

        # flatten records from different group within same classification
        # assign new name in format first_name-last_name, e.g. ABC-AZZ

        new_groups = OrderedDict()

        for group_names in classifier:
            key = group_names[0] + "-" + group_names[len(group_names)-1]
            new_groups[key] = []

            for group_name in group_names:
                for item in groups[group_name]:
                    new_groups[key].append(item)

        return new_groups

    def get_author_books(self, url):
        data = []

        document = self.fetch_document(url)

        items = document.xpath('//div[@class="biography-main"]')

        for item in items:
            name = item.find('div/[@class="biography-title"]/h2/a').text
            href = item.find('div/div/[@class="biography-image"]/a').get("href")
            thumb = item.find('div/div/[@class="biography-image"]/a/img').get("src")
            content = item.find('div/[@class="biography-content"]/div').text
            rating_node = item.find('div[@class="biography-content"]/div/div[@class="rating"]/ul/li')

            if rating_node:
                rating = rating_node.text
            else:
                rating = ''

            data.append({'path': href, 'name': name, 'thumb': thumb, 'content': content, 'rating': rating})

        return data

    def get_playlist_urls(self, url):
        data = []

        document = self.fetch_document(url)

        result = document.xpath('//object')

        for item in result:
            data.append(item.get("data"))

        return data

    def get_audio_tracks(self, url):
        data = []

        document = self.fetch_document(url)

        scripts = document.xpath('//script')

        for script in scripts:
            text = script.text_content()

            index1 = text.find("Play('jw6',")
            index2 = text.find('{"start":0,')

            if index1 >= 0 and index2 >= 0:
                content = text[index1 + 10:index2 - 1].strip()

                content = content[2:len(content) - 1].strip()

                data.append(json.loads(content))

        return data[0]

    def search(self, query):
        url = self.URL + "/engine/ajax/search.php"

        headers = {'X-Requested-With': 'XMLHttpRequest'}

        content = self.http_request(url, headers=headers, data={'query': query}, method='POST').read()

        document = self.to_document(content)

        data = []

        items = document.xpath('a')

        for item in items:
            href = item.xpath('@href')[0]
            name = item.text_content().upper()

            data.append({'path': href, 'name': name})

        return data

    def convert_track_duration(self, s):
        tokens = str(s).split(':')

        result = []

        for token in tokens:
            data = re.search('(\d+)', token)

            if data:
                result.append(data.group(0))

        hours = 0
        minutes = 0

        if len(result) > 2:
            hours = int(result[0])
            minutes = int(result[1])
            seconds = int(result[2])
        elif len(result) > 1:
            minutes = int(result[0])
            seconds = int(result[1])
        else:
            seconds = int(result[0])

        return (hours * 60 * 60 + minutes * 60 + seconds) * 1000