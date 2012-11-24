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

import sys, urlparse

import xbmc, xbmcplugin, xbmcgui, xbmcaddon

from tagesschau_json_api import VideoContentProvider, JsonSource

# -- Constants ----------------------------------------------
ADDON_ID = 'plugin.video.tagesschau'
FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
FEED_PARAM = 'feed'

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
    url = 'plugin://' + ADDON_ID + '/?' + FEED_PARAM + '=' + method;
    # TODO: display a standard tagesschau logo for a directory?
    li = xbmcgui.ListItem(title)
    li.setProperty('Fanart_Image', FANART)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)    
    
def addVideoContentItem(videocontent):
    title = videocontent.title
    # TODO: support for lazy loading, by using a url pointing to the plugin and passing the video id as parameter
    # should also speed up display for non lazy video content, see http://forum.xbmc.org/showthread.php?tid=118083
    url = videocontent.video_url(quality)
    # TODO: display duration as label2? where/how is this displayed?
    li = xbmcgui.ListItem(title, thumbnailImage=videocontent.image_url())
    li.setProperty('Fanart_Image', FANART)
    li.setInfo(type="Video", infoLabels={ "Title": title, "Plot": videocontent.description })
    # li.select(True)
    ok = xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)
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

if(FEED_PARAM not in params):
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
else:
    # list video for a directory
    videos_method = getattr(provider, params[FEED_PARAM])
    videos = videos_method()
    for video in videos:
        addVideoContentItem(video)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))


