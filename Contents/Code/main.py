# -*- coding: utf-8 -*-

import json

import constants
import util
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
            key=Callback(HandleLetterGroup, path=path, name=name),
            title=name
        ))

    return oc

@route(constants.PREFIX + '/letter_group')
def HandleLetterGroup(path, name):
    oc = ObjectContainer(title2=unicode(L(name)))

    response = service.get_authors_by_letter(path)

    for group_name, authors in response.iteritems():
        oc.add(DirectoryObject(
            key=Callback(HandleLetter, name=group_name, authors=json.dumps(authors)),
            title=group_name
        ))

    return oc

@route(constants.PREFIX + '/letter')
def HandleLetter(name, authors):
    oc = ObjectContainer(title2=unicode(L(name)))

    for author in json.loads(authors):
        name = author['name']
        path = author['path']

        oc.add(DirectoryObject(
            key=Callback(HandleAuthor, type='author', path=path, name=name),
            title=name
        ))

    return oc

@route(constants.PREFIX + '/author')
def HandleAuthor(operation=None, **params):
    media_info = MediaInfo(**params)

    if operation == 'add':
        service.queue.add(media_info)
    elif operation == 'remove':
        service.queue.remove(media_info)

    oc = ObjectContainer(title2=unicode(L(params['name'])))

    response = service.get_author_books(params['path'])

    for item in response:
        path = item['path']
        book_name = item['name']
        content = item['content']
        rating = item['rating']
        thumb = service.URL + item['thumb']

        params = {
            'type': 'tracks',
            'path' :path,
            'name': book_name,
            'thumb': thumb,
            'artist': params['name'],
            'content': content,
            'rating': rating
        }

        oc.add(DirectoryObject(
            key=Callback(HandleTracksVersions, **params),
            title=book_name,
            thumb=thumb
        ))

    service.queue.append_controls(oc, HandleAuthor, media_info)

    return oc

@route(constants.PREFIX + '/tracks_versions')
def HandleTracksVersions(**params):
    playlist_urls = service.get_playlist_urls(params['path'])

    if len(playlist_urls) == 1:
        return HandleTracks(playlist_url=playlist_urls[0], **params)
    else:
        oc = ObjectContainer(title2=unicode(L(params['name'])))

        for index, playlist_url in enumerate(playlist_urls):
            oc.add(DirectoryObject(
                key=Callback(HandleTracks, playlist_url=playlist_url, **params),
                title="Version " + str(index+1),
            ))

        return oc

@route(constants.PREFIX + '/tracks')
def HandleTracks(operation=None, container=False, **params):
    Log(params['playlist_url'])

    media_info = MediaInfo(**params)

    if operation == 'add':
        service.queue.add(media_info)
    elif operation == 'remove':
        service.queue.remove(media_info)

    oc = ObjectContainer(title2=unicode(L(params['name'])))

    response = service.get_audio_tracks(params['playlist_url'])

    for item in response:
        name = item['title']
        duration = service.convert_track_duration(item['duration'])
        sources = item['sources']
        thumb = service.URL + item['image']
        path = "https://archive.org" + sources[0]['file']
        format = 'mp3'
        bitrate = 0

        # Log(thumb)

        new_params = {
            'type': 'track',
            'path': path,
            'name': name,
            'thumb': thumb,
            'format': format,
            'bitrate': bitrate,
            'duration': duration
        }

        if 'artist' in params:
            new_params['artist'] = media_info['artist']

        oc.add(HandleTrack(**new_params))

    if str(container) == 'False':
        history.push_to_history(media_info)
        service.queue.append_controls(oc, HandleTracks, media_info)

    return oc

@route(constants.PREFIX + '/track')
def HandleTrack(container=False, **params):
    media_info = MediaInfo(**params)

    if 'm4a' in media_info['format']:
        audio_container = Container.MP4
        audio_codec = AudioCodec.AAC
    else:
        audio_container = Container.MP3
        audio_codec = AudioCodec.MP3

    url_items = [
        {
            "url": media_info['path'],
            "config": {
                "container": audio_container,
                "audio_codec": audio_codec,
                "bitrate": media_info['bitrate'],
                "duration": media_info['duration']
            }
        }
    ]

    track = AudioMetadataObjectForURL(media_info, url_items=url_items, player=PlayAudio)

    if container:
        oc = ObjectContainer(title2=unicode(media_info['name']))

        oc.add(track)

        return oc
    else:
        return track

def AudioMetadataObjectForURL(media_info, url_items, player):
    metadata_object = builder.build_metadata_object(media_type=media_info['type'], title=media_info['name'])

    metadata_object.key = Callback(HandleTrack, container=True, **media_info)
    metadata_object.rating_key = unicode(media_info['name'])
    metadata_object.duration = int(media_info['duration']) * 1000
    metadata_object.thumb = media_info['thumb']

    if 'artist' in media_info:
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
            key=Callback(HandleContainer, type='tracks', path=path, name=name),
            title=unicode(name)
        ))

    return oc

@route(constants.PREFIX + '/container')
def HandleContainer(**params):
    type = params['type']

    if type == 'author':
        return HandleAuthor(**params)
    elif type == 'tracks':
        return HandleTracks(**params)

@route(constants.PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    for media_info in service.queue.data:
        if 'thumb' in media_info:
            thumb = media_info['thumb']
        else:
            thumb = None

        oc.add(DirectoryObject(
            key=Callback(HandleContainer, **media_info),
            title=util.sanitize(media_info['name']),
            thumb=thumb
        ))

    if len(service.queue.data) > 0:
        oc.add(DirectoryObject(
            key=Callback(ClearQueue),
            title=unicode(L("Clear Queue"))
        ))

    return oc

@route(constants.PREFIX + '/clear_queue')
def ClearQueue():
    service.queue.clear()

    return HandleQueue()

@route(constants.PREFIX + '/history')
def HandleHistory():
    history_object = history.load_history()

    oc = ObjectContainer(title2=unicode(L('History')))

    if history_object:
        for item in sorted(history_object.values(), key=lambda k: k['time'], reverse=True):
            oc.add(DirectoryObject(
                key=Callback(HandleContainer, **item),
                title=unicode(item['name']),
                thumb=item['thumb']
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