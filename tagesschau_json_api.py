try: import json
except ImportError: import simplejson as json
import urllib2

# See bottom for usage example

class VideoContent(object):
    def __init__(self, title, timestamp, duration, videourls, imageurls=None):
        self.title = title
        # datetime
        self.timestamp = timestamp
        # duration in seconds
        self.duration = duration
        # video/mediadata names mapped to urls
        self.videourls = videourls
        # image variant names mapped to urls
        self.imageurls = imageurls
    
    def video_url(self):
        videourl=self.videourls["h264l"]
        return videourl

    def image_url(self):
        try:
            imageurl=self.imageurls["mittel16x9"]
        # fallback for Wetter
        except KeyError:
            imageurl=self.imageurls["grossgalerie16x9"]
        return imageurl
        
    # String representation for testing/development
    def __str__(self):
        return "VideoContent(title='" + self.title + "', timestamp='" + self.timestamp + "', "\
            "duration=" + str(self.duration) + ", videourl=" + str(self.video_url()) + ", "\
            "imageurl=" + str(self.image_url()) + ")"

# converts the video JSON into VideoContent
def parse_video(jsonvideo):
    title = jsonvideo["headline"]
    # TODO: parse into datetime
    timestamp = jsonvideo["broadcastDate"]
    # calculate duration using outMilli and inMilli, duration is not set in JSON
    duration = (jsonvideo["outMilli"] - jsonvideo["inMilli"]) / 1000
    imageurls = parse_image_urls(jsonvideo["images"][0]["variants"])
    videourls = parse_video_urls(jsonvideo["mediadata"])
    video = VideoContent(title, timestamp, duration, videourls, imageurls);       
    return video

# parses the image variants JSON into a dict mapping name to url 
def parse_image_urls(jsonvariants):
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

# parses the video mediadata JSON into a dict mapping name to url
def parse_video_urls(jsonvariants):
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

def latest_videos():
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemand100_type-video.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = parse_video(jsonvideo)
        videos.append(video)    
    return videos

def dossiers():
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemanddossier100.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = parse_video(jsonvideo)
        videos.append(video)    
    return videos


print "Aktuelle Videos"     
videos = latest_videos()
for video in videos:
    print video

print "Dossier"
videos = dossiers()
for video in videos:
    print video

# TODO: Alle/Aktuelle Sendungen, http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json
# TODO: (Sendungs) Archiv, http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100_week-true.json"
# TODO: LiveStream/TSin100, see multimedia http://www.tagesschau.de/api/multimedia/video/ondemand100.json 

    
    
    
