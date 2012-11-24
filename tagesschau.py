# -*- coding: utf-8 -*-
# Copyright 2011 Jörn Schumacher, Henning Saul 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, urllib, urlparse

import xbmc, xbmcplugin, xbmcgui, xbmcaddon

from tagesschau_json_api import VideoContentProvider, JsonSource

# -- Constants ----------------------------------------------
ADDON_ID = 'plugin.video.tagesschau'
FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
FEED_PARAM = 'feed'
ACTION_PARAM = 'action'
URL_PARAM = 'url'
DEFAULT_IMAGE_URL = 'http://miss.tagesschau.de/image/sendung/ard_portal_vorspann_ts.jpg'

# -- Settings -----------------------------------------------
settings = xbmcaddon.Addon(id=ADDON_ID)
quality_id = settings.getSetting("quality")
quality = ['M', 'L'][int(quality_id)]

# -- I18n ---------------------------------------------------
language = xbmcaddon.Addon(id='plugin.video.tagesschau').getLocalizedString
strings = { 'latest_videos': language(30100),
            'latest_broadcasts': language(30101),
            'dossiers': language(30102),
            'archived_broadcasts': language(30103)
}

# ------------------------------------------------------------


def addVideoContentDirectory(title, method):
    url_data = { ACTION_PARAM: 'list_feed', 
                 FEED_PARAM: method  }
    url = 'plugin://' + ADDON_ID + '/?' + urllib.urlencode(url_data)
    # TODO: display a standard tagesschau logo for a directory?
    li = xbmcgui.ListItem(title)
    li.setProperty('Fanart_Image', FANART)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)    
    
def addVideoContentItem(videocontent):
    title = videocontent.title
    url = videocontent.video_url(quality)
    url_data = { ACTION_PARAM: 'play_video',
                 URL_PARAM: urllib.quote(url) }
    url = 'plugin://' + ADDON_ID + '?' + urllib.urlencode(url_data)
    image_url=videocontent.image_url()
    if(not image_url):
        image_url = DEFAULT_IMAGE_URL
    li = xbmcgui.ListItem(title, thumbnailImage=image_url)
    li.setProperty('Fanart_Image', FANART)
    li.setProperty('IsPlayable', 'true')
    li.setInfo(type="Video", infoLabels={ "Title": title,
                                          "Plot": videocontent.description,
                                          "Duration": str((videocontent.duration or 0)/60) })
    # li.select(True)
    ok = xbmcplugin.addDirectoryItem(int(sys.argv[1]), url=url, listitem=li, isFolder=False)
    return ok

def get_params():
    paramstring = sys.argv[2]
    params = urlparse.parse_qs(urlparse.urlparse(paramstring).query)
    
    for key in params:
        params[key] = params[key][0]
    return params
    
# TODO: can't figure out how to set fanart for root/back folder of plugin
# http://trac.xbmc.org/ticket/8228? 
xbmcplugin.setPluginFanart(int(sys.argv[1]), 'special://home/addons/' + ADDON_ID + '/fanart.jpg')

params = get_params()
provider = VideoContentProvider(JsonSource())

if params.get(ACTION_PARAM) == 'play_video':
    url = urllib.unquote(params[URL_PARAM])
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

elif params.get(ACTION_PARAM) == 'list_feed':
    # list video for a directory
    videos_method = getattr(provider, params[FEED_PARAM])
    videos = videos_method()
    for video in videos:
        addVideoContentItem(video)

else:
    # populate root directory
    # check whether there is a livestream
    videos = provider.livestreams()
    if(len(videos) == 1):
        addVideoContentItem(videos[0])

    # add directories for other feeds        
    add_named_directory = lambda x: addVideoContentDirectory(strings[x], x)
    add_named_directory('latest_videos')
    add_named_directory('latest_broadcasts')
    add_named_directory('dossiers')
    add_named_directory('archived_broadcasts')   
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))


