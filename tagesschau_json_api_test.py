#
# Copyright 2012 Henning Saul, Joern Schumacher 
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

import unittest
import json
from tagesschau_json_api import VideoContentProvider

class VideoContentProviderTest(unittest.TestCase):

    def setUp(self):
        self.provider = VideoContentProvider(TestJsonSource());

    def testDossiers(self):
        self.assertEqual(len(self.provider.dossiers()), 10)

class TestJsonSource(object):

    def dossiers(self):
        handle = open('resources/test/dossiers.json', 'r');
        return json.loads(handle.read())

if __name__ == "__main__":
    unittest.main()
