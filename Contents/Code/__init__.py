# -*- coding: utf-8 -*-

PREFIX = '/video/audioboo'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

import library_bridge

library_bridge.bridge.export_object('L', L)
library_bridge.bridge.export_object('R', R)
library_bridge.bridge.export_object('Log', Log)
library_bridge.bridge.export_object('Resource', Resource)
library_bridge.bridge.export_object('Datetime', Datetime)
library_bridge.bridge.export_object('Core', Core)
library_bridge.bridge.export_object('Prefs', Prefs)
library_bridge.bridge.export_object('Locale', Locale)
library_bridge.bridge.export_object('Callback', Callback)
library_bridge.bridge.export_object('AudioCodec', AudioCodec)
library_bridge.bridge.export_object('AudioStreamObject', AudioStreamObject)
library_bridge.bridge.export_object('VideoStreamObject', VideoStreamObject)
library_bridge.bridge.export_object('DirectoryObject', DirectoryObject)
library_bridge.bridge.export_object('PartObject', PartObject)
library_bridge.bridge.export_object('MediaObject', MediaObject)
library_bridge.bridge.export_object('EpisodeObject', EpisodeObject)
library_bridge.bridge.export_object('TVShowObject', TVShowObject)
library_bridge.bridge.export_object('MovieObject', MovieObject)
library_bridge.bridge.export_object('TrackObject', TrackObject)
library_bridge.bridge.export_object('VideoClipObject', VideoClipObject)
library_bridge.bridge.export_object('MessageContainer', MessageContainer)

import plex_util
import common_routes

from audioboo_plex_service import AudiobooPlexService

service = AudiobooPlexService()

import main

def Start():
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')
    Plugin.AddViewGroup('MediaPreview', viewMode='MediaPreview', mediaType='items')

    DirectoryObject.art = R(ART)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR

    plex_util.validate_prefs()

@handler(PREFIX, 'AudioBoo', R(ART), R(ICON))
def MainMenu():
    if not service.available():
        return MessageContainer(L('Error'), L('Service not avaliable'))

    oc = ObjectContainer(title2=unicode(L('Title')), no_cache=True)

    oc.add(DirectoryObject(key=Callback(main.HandleLetters), title=unicode(L('Authors'))))
    oc.add(DirectoryObject(key=Callback(common_routes.HandleHistory), title=unicode(L('History'))))
    oc.add(DirectoryObject(key=Callback(common_routes.HandleQueue), title=unicode(L('Queue'))))

    oc.add(InputDirectoryObject(
        key=Callback(main.HandleSearch),
        title=unicode(L('Search')), prompt=unicode(L('Search on AudioBoo.ru'))
    ))

    return oc
