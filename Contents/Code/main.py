# -*- coding: utf-8 -*-

from collections import OrderedDict
import history
import common_routes
from media_info import MediaInfo
from flow_builder import FlowBuilder

@route(PREFIX + '/letters')
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

@route(PREFIX + '/letter_group')
def HandleLetterGroup(path, name):
    oc = ObjectContainer(title2=unicode(L(name)))

    response = service.get_authors_by_letter(path)

    for group_name, authors in response.iteritems():
        oc.add(DirectoryObject(
            key=Callback(HandleLetter, name=group_name, authors=authors),
            title=group_name
        ))

    return oc

@route(PREFIX + '/letter', authors=list)
def HandleLetter(name, authors):
    oc = ObjectContainer(title2=unicode(L(name)))

    for author in authors:
        name = author['name']
        path = author['path']

        oc.add(DirectoryObject(
            key=Callback(HandleAuthor, type='author', id=path, name=name),
            title=name
        ))

    return oc

@route(PREFIX + '/author')
def HandleAuthor(operation=None, **params):
    media_info = MediaInfo(**params)

    service.queue.handle_bookmark_operation(operation, media_info)

    author = params['name']

    oc = ObjectContainer(title2=unicode(L(author)))

    response = service.get_author_books(params['id'])

    for item in response:
        path = item['path']
        full_name = item['name']
        content = item['content']
        rating = item['rating']
        thumb = service.URL + item['thumb']

        full_name_decoded = full_name.decode('utf-8')
        prefix = (author + ' - ').decode('utf-8')

        if full_name_decoded[0:len(prefix)] == prefix:
            book_name = full_name[len(prefix):]
        else:
            book_name = full_name

        params = {
            'type': 'tracks',
            'id' : path,
            'name': book_name,
            'thumb': thumb,
            'artist': author,
            'content': content,
            'rating': rating
        }

        oc.add(DirectoryObject(
            key=Callback(HandleTracksVersions, **params),
            title=book_name,
            thumb=thumb
        ))

    service.queue.append_bookmark_controls(oc, HandleAuthor, media_info)

    return oc

@route(PREFIX + '/tracks_versions')
def HandleTracksVersions(**params):
    playlist_urls = service.get_playlist_urls(params['id'])

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

@route(PREFIX + '/tracks')
def HandleTracks(operation=None, container=False, **params):
    media_info = MediaInfo(**params)

    service.queue.handle_bookmark_operation(operation, media_info)

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

        new_params = {
            'type': 'track',
            'id': path,
            'name': name,
            'thumb': thumb,
            'artist': params['artist'],
            'format': format,
            'bitrate': bitrate,
            'duration': duration
        }

        oc.add(HandleTrack(**new_params))

    if str(container) == 'False':
        history.push_to_history(Data, media_info)
        service.queue.append_bookmark_controls(oc, HandleTracks, media_info)

    return oc

def build_urls_with_metadata(media_info):
    if 'm4a' in media_info['format']:
        format = 'm4a'
    else:
        format = 'mp3'

    config = FlowBuilder.get_plex_config(format)

    config["bitrate"] = media_info['bitrate']
    config["duration"] = media_info['duration']

    url = media_info['id']

    urls_with_metadata = OrderedDict()

    urls_with_metadata[url] = config

    return urls_with_metadata

@route(PREFIX + '/track')
def HandleTrack(container=False, **params):
    media_info = MediaInfo(**params)

    urls = build_urls_with_metadata(media_info)

    metadata_object = FlowBuilder.build_metadata_object(media_type=media_info['type'], title=media_info['name'])

    metadata_object.key = Callback(HandleTrack, container=True, **media_info)
    metadata_object.rating_key = unicode(media_info['name'])
    metadata_object.title = media_info['name']
    metadata_object.artist = media_info['name']
    metadata_object.thumb = media_info['thumb']

    if 'duration' in media_info:
        metadata_object.duration = int(media_info['duration'])

    if 'artist' in media_info:
        metadata_object.artist = media_info['artist']

    metadata_object.items.extend(common_routes.MediaObjectsForURL(urls, common_routes.PlayAudio))

    if container:
        oc = ObjectContainer(title2=unicode(media_info['name']))

        oc.add(metadata_object)

        return oc
    else:
        return metadata_object

@route(PREFIX + '/container')
def HandleContainer(**params):
    type = params['type']

    if type == 'author':
        return HandleAuthor(**params)
    elif type == 'tracks':
        return HandleTracks(**params)

@route(PREFIX + '/search')
def HandleSearch(query=None):
    oc = ObjectContainer(title2=unicode(L('Search')))

    response = service.search(query=query)

    for movie in response:
        name = movie['name']
        path = movie['path']

        oc.add(DirectoryObject(
            key=Callback(HandleContainer, type='tracks', id=path, name=name),
            title=unicode(name)
        ))

    return oc

@route(PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    service.queue.handle_queue_items(oc, HandleContainer, service.queue.data)

    if len(service.queue.data) > 0:
        oc.add(DirectoryObject(
            key=Callback(ClearQueue),
            title=unicode(L("Clear Queue"))
        ))

    return oc

@route(PREFIX + '/clear_queue')
def ClearQueue():
    service.queue.clear()

    return HandleQueue()

@route(PREFIX + '/history')
def HandleHistory():
    history_object = history.load_history(Data)

    oc = ObjectContainer(title2=unicode(L('History')))

    if history_object:
        data = sorted(history_object.values(), key=lambda k: k['time'], reverse=True)

        service.queue.handle_queue_items(oc, HandleContainer, data)

    return oc

