# coding=utf-8

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

    def test_get_author_book(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        books = self.service.get_author_books(authors[1]['path'])

        result = self.service.get_author_book(books[0]['path'])

        print(json.dumps(result, indent=4))

    def test_get_playlist_url(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        books = self.service.get_author_books(authors[1]['path'])

        result = self.service.get_playlist_url(books[0]['path'])

        print result

    def test_get_audio_tracks(self):
        letters = self.service.get_letters()

        authors = self.service.get_authors_by_letter(letters[0]['path'])

        books = self.service.get_author_books(authors[1]['path'])

        playlist_url = self.service.get_playlist_url(books[0]['path'])

        result = self.service.get_audio_tracks(playlist_url)

        print(json.dumps(result, indent=4))

    def test_search(self):
        query = 'пратчетт'

        result = self.service.search(query)

        print(json.dumps(result, indent=4))

if __name__ == '__main__':
    unittest.main()
