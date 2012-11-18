# -*- coding: utf-8 -*-
# Copyright 2011 Jörn Schumacher 
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

import sys

import xbmcplugin, xbmcgui, xbmcaddon

from tagesschau_json_api import VideoContentProvider, JsonSource

# -- Settings -----------------------------------------------
settings = xbmcaddon.Addon(id='plugin.video.tagesschau')
quality_id = settings.getSetting("quality")
quality = ['M', 'L'][int(quality_id)]
# ------------------------------------------------------------

def addVideoContentDirectory(title, videos):
    # TODO: add a new virtual directory, ideally videos are only loaded when directory is accessed
    # not sure what using url = "plugin:// for another virtual directory" does...
    for video in videos:
        addVideoContentItem(video)
    
def addVideoContentItem(videocontent):
    title = videocontent.title
    url = videocontent.video_url('L')
    # TODO: display duration as label2? 
    # TODO: can't get fanart to display while using plugin, also see below
    li = xbmcgui.ListItem(title, iconImage="special://home/plugins/video/plugin.video.tagesschau/fanart.jpg", thumbnailImage=videocontent.image_url())
    # TODO: include duration? where/how is this displayed?
    li.setInfo(type="Video", infoLabels={ "Title": title, "Plot": videocontent.description })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li)
    return ok

# TODO: can't get fanart to display while using plugin, also see above
xbmcplugin.setPluginFanart(int(sys.argv[1]), "special://home/plugins/video/plugin.video.tagesschau/fanart.jpg")
provider = VideoContentProvider(JsonSource())
videos = provider.livestreams();
if(len(videos) == 1):
    addVideoContentItem(videos[0]);
videos = provider.latest_videos();
if(len(videos) > 0):
    addVideoContentDirectory("Aktuelle Videos", videos)
videos = provider.latest_broadcasts();
if(len(videos) > 0):
    addVideoContentDirectory("Aktuelle Sendungen", videos)
videos = provider.dossiers();
if(len(videos) > 0):
    addVideoContentDirectory("Dossier", videos)
# TODO: this takes a while, but might be ok if only loaded when directory is selected
# videos = provider.archived_broadcasts();
# if(len(videos) > 0):
#    addVideoContentDirectory("Sendungsarchiv", videos)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
