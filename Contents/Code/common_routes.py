import plex_util
from flow_builder import FlowBuilder

builder = FlowBuilder()

@route(PREFIX + '/queue')
def HandleQueue():
    oc = ObjectContainer(title2=unicode(L('Queue')))

    for media_info in service.queue.data:
        if 'thumb' in media_info:
            thumb = media_info['thumb']
        else:
            thumb = None

        oc.add(DirectoryObject(
            key=Callback(HandleContainer, **media_info),
            title=plex_util.sanitize(media_info['name']),
            thumb=thumb
        ))

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
        for item in sorted(history_object.values(), key=lambda k: k['time'], reverse=True):
            oc.add(DirectoryObject(
                key=Callback(HandleContainer, **item),
                title=unicode(item['name']),
                thumb=item['thumb']
            ))

    return oc

def MediaObjectsForURL(urls, player):
    media_objects = []

    for url, config in urls.iteritems():
        play_callback = Callback(player, url=url)

        media_object = builder.build_media_object(play_callback, config)

        media_objects.append(media_object)

    return media_objects

@route(PREFIX + '/play_audio')
def PlayAudio(url):
    return Redirect(url)
