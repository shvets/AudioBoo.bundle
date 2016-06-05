# -*- coding: utf-8 -*-

import test_helper

import unittest
import json

from audioboo_service import AudiobooService

class AudioBooServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = AudiobooService()

    def test_get_letters(self):
        result = self.service.get_letters()

        print(json.dumps(result, indent=4))

    def test_get_authors_by_letter(self):
        letters = self.service.get_letters()

        result = self.service.get_authors_by_letter(letters[0]['path'])

        print(json.dumps(result, indent=4))

    def test_get_author_books(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        result = self.service.get_author_books(authors[1]['path'])

        print(json.dumps(result, indent=4))

    # def test_get_author_book(self):
    #     letters = self.service.get_letters()
    #
    #     authors = self.service.get_authors_by_letter(letters[0]['path'])
    #
    #     group = self.get_author_group_by_index(authors, 1)
    #
    #     books = self.service.get_author_books(group[0]['path'])
    #
    #     result = self.service.get_audio_tracks(books[0]['path'])
    #
    #     print(json.dumps(result, indent=4))

    def test_get_playlist_urls(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        group = self.get_author_group_by_index(authors, 1)

        books = self.service.get_author_books(group[0]['path'])

        result = self.service.get_playlist_urls(books[0]['path'])

        url = 'http://audioboo.ru/geimannil/1009-geyman-nil-koralina.html'

        playlist_urls = self.service.get_playlist_urls(url)

        print playlist_urls

    def test_get_audio_tracks(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        group = self.get_author_group_by_index(authors, 1)

        books = self.service.get_author_books(group[0]['path'])

        playlist_urls = self.service.get_playlist_urls(books[0]['path'])

        result = self.service.get_audio_tracks(playlist_urls[0])

        print(json.dumps(result, indent=4))

    def test_search(self):
        query = 'пратчетт'

        result = self.service.search(query)

        print(json.dumps(result, indent=4))

    def test_convert_track_duration(self):
        s = "14:46"

        result = self.service.convert_track_duration(s)

        print(result)

    def get_author_group_by_index(self, authors, index):
        i = 0
        for key, value in authors.iteritems():
            if i == index:
                return value

            i += 1

if __name__ == '__main__':
    unittest.main()
