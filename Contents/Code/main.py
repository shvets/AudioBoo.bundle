# -*- coding: utf-8 -*-

import json
import constants
import util
import pagination
import history
from flow_builder import FlowBuilder
from media_info import MediaInfo

builder = FlowBuilder()

@route(constants.PREFIX + '/letters')
def HandleLetters():
    oc = ObjectContainer(title2=unicode(L("Letters")))

    response = service.get_letters()

    for item in response:
        name = item['name']
        path = item['path']

        oc.add(DirectoryObject(
            key=Callback(HandleLetter, path=path, name=name),
            title=name
        ))

    return oc

@route(constants.PREFIX + '/letter')
def HandleLetter(path, name):
    oc = ObjectContainer(title2=unicode(L(name)))

    response = service.get_authors_by_letter(path)

    for item in response:
        name = item['name']
        path = item['path']

        oc.add(DirectoryObject(
            key=Callback(HandleAuthor, type='author', path=path, name=name),
            title=name
        ))

    return oc

@route(constants.PREFIX + '/author')
def HandleAuthor(type, path, name, thumb=None):
    oc = ObjectContainer(title2=unicode(L(name)))

    response = service.get_author_books(path)

    for item in response:
        path = item['path']
        book_name = item['name']
        content = item['content']
        rating = item['rating']
        thumb = service.URL + item['thumb']

        oc.add(DirectoryObject(
            key=Callback(HandleTracks, type='book', path=path, name=book_name, thumb=thumb,
                         artist=name, content=content, rating=rating),
            title=book_name,
            thumb=thumb
        ))

    return oc

@route(constants.PREFIX + '/tracks')
def HandleTracks(type, path, name, thumb, artist, content, rating, operation=None, container=False):
    oc = ObjectContainer(title2=unicode(L(name)))

    media_info = MediaInfo(type=type, path=path, name=name, thumb=thumb, artist=artist, content=content, rating=rating)

    if operation == 'add':
        service.queue.add(media_info)
    elif operation == 'remove':
        service.queue.remove(media_info)

    playlist_url = service.get_playlist_url(path)

    response = service.get_audio_tracks(playlist_url)

    for item in response:
        name = item['title']
        duration = service.convert_track_duration(item['duration'])
        sources = item['sources']
        thumb = service.URL + item['image']
        path = "https://archive.org" + sources[0]['file']
        format = 'mp3'
        bitrate = 0
        media_type = 'track'

        Log(thumb)

        oc.add(GetAudioTrack(type=type, media_type=media_type, path=path, name=name, thumb=thumb,
                             artist=artist, format=format,
                             bitrate=bitrate, duration=duration))

    if str(container) == 'False':
        history.push_to_history(media_info)
        service.queue.append_controls(oc, HandleTracks, media_info)

    return oc

@route(constants.PREFIX + '/audio_track')
def GetAudioTrack(type, media_type, path, name, thumb, artist, format, bitrate, duration, container=False):
    if 'm4a' in format:
        audio_container = Container.MP4
        audio_codec = AudioCodec.AAC
    else:
        audio_container = Container.MP3
        audio_codec = AudioCodec.MP3

    url_items = [
        {
            "url": path,
            "config": {
                "container": audio_container,
                "audio_codec": audio_codec,
                "bitrate": bitrate,
                "duration": duration
            }
        }
    ]

    media_info = MediaInfo(
        media_type=media_type,
        path=path,
        name=name,
        thumb=thumb,
        artist=artist,
        format=format,
        bitrate=bitrate,
        duration=duration
    )

    track = AudioMetadataObjectForURL(media_info, url_items=url_items, player=PlayAudio)

    if container:
        oc = ObjectContainer(title2=unicode(name))

        oc.add(track)

        return oc
    else:
        return track

def AudioMetadataObjectForURL(media_info, url_items, player):
    metadata_object = builder.build_metadata_object(media_type=media_info['media_type'], title=media_info['name'])

    metadata_object.key = Callback(GetAudioTrack, container=True, **media_info)
    metadata_object.rating_key = unicode(media_info['name'])
    metadata_object.duration = int(media_info['duration']) * 1000
    metadata_object.thumb = media_info['thumb']
    metadata_object.artist = media_info['artist']

    metadata_object.items.extend(MediaObjectsForURL(url_items, player))

    return metadata_object

@route(constants.PREFIX + '/search')
def HandleSearch(query=None):
    oc = ObjectContainer(title2=unicode(L('Search')))

    response = service.search(query=query)

    for movie in response:
        name = movie['name']
        path = movie['path']

        oc.add(DirectoryObject(
            key=Callback(HandleContainer, type='book', path=path, name=name, thumb='thumb'),
            title=unicode(name),
            thumb='thumb'
        ))

    return oc

@route(constants.PREFIX + '/container')
def HandleContainer(type, path, name, thumb=None):
    if type == 'author':
        return HandleAuthor(type=type, path=path, name=name, thumb=thumb)
    elif type == 'book':
        return HandleBook(type=type, path=path, name=name, thumb=thumb)

@route(constants.PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    for media_info in service.queue.data:
        type = media_info['type']

        oc.add(DirectoryObject(
            key=Callback(HandleContainer, type=type, **media_info),
            title=util.sanitize(media_info['name']),
            thumb=media_info['thumb']
        ))

    return oc

@route(constants.PREFIX + '/history')
def HandleHistory():
    history_object = history.load_history()

    oc = ObjectContainer(title2=unicode(L('History')))

    if history_object:
        for item in sorted(history_object.values(), key=lambda k: k['time'], reverse=True):
            type = item['type']
            path = item['path']
            name = item['name']

            if item['thumb']:
                thumb = service.get_thumb(item['thumb'])
            else:
                thumb = None

            oc.add(DirectoryObject(
                key=Callback(HandleContainer, type=type, path=path, name=name, thumb=thumb),
                title=unicode(name),
                thumb=thumb
            ))

    return oc

def MediaObjectsForURL(url_items, player):
    media_objects = []

    for item in url_items:
        url = item['url']
        config = item['config']

        play_callback = Callback(player, url=url)

        media_object = builder.build_media_object(play_callback, config)

        media_objects.append(media_object)

    return media_objects

@route(constants.PREFIX + '/play_audio')
def PlayAudio(url):
    return Redirect(url)