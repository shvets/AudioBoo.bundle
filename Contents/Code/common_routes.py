from flow_builder import FlowBuilder

def MediaObjectsForURL(urls, player):
    media_objects = []

    for url, config in urls.iteritems():
        play_callback = Callback(player, url=url)

        media_object = FlowBuilder.build_media_object(play_callback, config)

        media_objects.append(media_object)

    return media_objects

@route(PREFIX + '/play_audio')
def PlayAudio(url):
    return Redirect(url)
