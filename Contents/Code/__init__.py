# -*- coding: utf-8 -*-

import library_bridge

library_bridge.bridge.export_object('R', R)
library_bridge.bridge.export_object('Log', Log)
library_bridge.bridge.export_object('Datetime', Datetime)
library_bridge.bridge.export_object('Core', Core)
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

import util
import constants
from audioboo_plex_service import AudiobooPlexService

service = AudiobooPlexService()

import main

def Start():
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')
    Plugin.AddViewGroup('MediaPreview', viewMode='MediaPreview', mediaType='items')

    DirectoryObject.art = R(constants.ART)
    VideoClipObject.art = R(constants.ART)

    HTTP.CacheTime = CACHE_1HOUR

    util.validate_prefs()

@handler(constants.PREFIX, 'AudioBoo', R(constants.ART), R(constants.ICON))
def MainMenu():
    if not service.available():
        return MessageContainer(L('Error'), L('Service not avaliable'))

    oc = ObjectContainer(title2=unicode(L('Title')), no_cache=True)

    oc.add(DirectoryObject(key=Callback(main.HandleLetters), title=unicode(L('Authors'))))
    oc.add(DirectoryObject(key=Callback(main.HandleHistory), title=unicode(L('History'))))
    oc.add(DirectoryObject(key=Callback(main.HandleQueue), title=unicode(L('Queue'))))

    oc.add(InputDirectoryObject(
        key=Callback(main.HandleSearch),
        title=unicode(L('Search')), prompt=unicode(L('Search on AudioBoo.ru'))
    ))

    return oc
