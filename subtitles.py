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

import os, urllib2, xml.sax

# https://vimeosrtplayer.googlecode.com/svn-history/r5/VimeoSrtPlayer/bin/srt/example.srt

class SubtitlesContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self._result = ""
        self._count = 0
        self._line = False
 
    def startElement(self, name, attrs):
        if name == "tt:p":
            self._startEntry(attrs.get("begin"), attrs.get("end"))
        elif name == "tt:span":
            self._startLine()

    def endElement(self, name):
        if name == "tt:p":
            self._endEntry()
        elif name == "tt:span":
            self._endLine()    
        elif name == "tt:br":
            self._newLine()    
             
    def characters(self, content):
        if(self._line):
            self._result += content

    # 00:00:00.000
    def _startEntry(self, begin, end):
        self._count = self._count + 1
        self._result += str(self._count)
        self._result += "\n"
        self._result += begin.replace('.', ',')
        self._result += " --> "
        self._result += end.replace('.', ',')
        self._result += "\n"
    
    def _endEntry(self):
        self._result += "\n\n"        
    
    def _startLine(self):
        self._line = True
        
    def _endLine(self):
        self._line = False
   
    def _newLine(self):
        self._result += "\n"
                 
    def result(self):
        return self._result 

def download_subtitles(url, subtitles_dir):
    # Download and Convert the TTAF format to srt

    print "downloading subtitles from " + url

    if not os.path.exists(subtitles_dir):
        os.makedirs(subtitles_dir)

    outfile = os.path.join(subtitles_dir, 'tagesschau.de.srt')

    if (os.path.exists(outfile)):
        os.remove(outfile)

    if not url:
        return None
    
    # try to download TTAF subtitles
    # TODO: error handling...
    response = urllib2.urlopen(url)
    source = response.read()
    xml.sax.parse(source, SubtitlesContentHandler())
    
    return outfile