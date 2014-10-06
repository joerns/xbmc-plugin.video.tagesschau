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

import os, re, urllib2

# TODO: see http://www.tagesschau.de/multimedia/video/video-29351~subtitle.html
re_subtitles = re.compile('^\s*<p.*?begin=\"(.*?)\.([0-9]+)\"\s+.*?end=\"(.*?)\.([0-9]+)\".*?>(.*?)</p>')

def download_subtitles(url, subtitles_dir):
    # Download and Convert the TTAF format to srt

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
    txt = response.read()
    
    fw = open(outfile, 'w')

    i=0
    prev = None

    # convert line by line
    for line in txt.split('\n'):
        entry = None
        m = re_subtitles.match(line)
        if m:
            
            start_mil = "%s000" % m.group(2) # pad out to ensure 3 digits
            end_mil   = "%s000" % m.group(4)

            ma = {'start'     : m.group(1),
                  'start_mil' : start_mil[:3],
                  'end'       : m.group(3),
                  'end_mil'   : end_mil[:3],
                  'text'      : m.group(5)}

            ma['text'] = ma['text'].replace('&amp;', '&')
            ma['text'] = ma['text'].replace('&gt;', '>')
            ma['text'] = ma['text'].replace('&lt;', '<')
            ma['text'] = ma['text'].replace('<br />', '\n')
            ma['text'] = ma['text'].replace('<br/>', '\n')
            ma['text'] = re.sub('<.*?>', '', ma['text'])
            ma['text'] = re.sub('&#[0-9]+;', '', ma['text'])

            if not prev:
                # first match - do nothing wait till next line
                prev = ma
                continue

            if prev['text'] == ma['text']:
                # current line = previous line then start a sequence to be collapsed
                prev['end'] = ma['end']
                prev['end_mil'] = ma['end_mil']
            else:
                i += 1
                entry = "%d\n%s,%s --> %s,%s\n%s\n\n" % (i, prev['start'], prev['start_mil'], prev['end'], prev['end_mil'], prev['text'])
                prev = ma
        elif prev:
            i += 1
            entry = "%d\n%s,%s --> %s,%s\n%s\n\n" % (i, prev['start'], prev['start_mil'], prev['end'], prev['end_mil'], prev['text'])
        if entry: fw.write(entry)
    fw.close()
    return outfile