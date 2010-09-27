import urllib2, re

import xbmcplugin, xbmcgui

# urls
# these urls refer to rss feeds
urls = dict()
urls['ts100s'] = 'http://www.tagesschau.de/export/video-podcast/tagesschau-in-100-sekunden/'
urls['ts20h'] = 'http://www.tagesschau.de/export/video-podcast/webl/tagesschau/'

# regular expressions
# Since the urls refer to rss-feeds, it might be better to 
# do some real xml-parsing, but it works for now.
regexp = dict()
regexp['ts100s'] = dict()
regexp['ts100s']['date'] = r'<title>(.*) - .*</title>'
regexp['ts100s']['url'] = r'<enclosure url="(.*)"\slength.*'


regexp['ts20h'] = dict()
regexp['ts20h']['date'] = r'<title>tagesschau (.*)</title>'
regexp['ts20h']['url'] = r'<enclosure url="(.*)"\slength.*'


def video_file(name):
    s = urllib2.urlopen(urls[name]).read()

    # the _first_ item group
    item = re.compile(r'<item>(?:.*\s)*</item>').findall(s)[0]

    # date
    date = re.compile(regexp[name]['date']).findall(item)[0]
    if name == 'ts100s':
        date = re.split('\s',date, 1)
        date[0],date[1] = date[1],date[0]
        date = ', '.join(date)

    # url
    url = re.compile(regexp[name]['url']).findall(item)[0]
 
    return date, url

def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

items = []

date, url = video_file('ts20h')
addLink('Tagesschau ('+date+')', url, 'http://www.tagesschau.de/image/podcast/ts-140.jpg')

date, url = video_file('ts100s')
addLink('Tagesschau in 100sek ('+date+')', url, 'http://www.tagesschau.de/image/podcast/ts100s-140.jpg')


xbmcplugin.endOfDirectory(int(sys.argv[1]))
