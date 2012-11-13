try: import json
except ImportError: import simplejson as json
import urllib2
import logging

# TODO: (Sendungs) Archiv, URL correct? http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100_week-true.json"
# TODO: LiveStream/TSin100, see multimedia http://www.tagesschau.de/api/multimedia/video/ondemand100.json 

logger = logging.getLogger(__name__)

class VideoContent(object):
    def __init__(self, title, timestamp, videourls, imageurls=None, duration=None):
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
        # TODO: broadcasts also have "adaptivestreaming"
        videourl = self.videourls["h264l"]
        return videourl

    def image_url(self):
        try:
            imageurl = self.imageurls["mittel16x9"]
        # fallback for Wetter
        except KeyError:
            imageurl = self.imageurls["grossgalerie16x9"]
        return imageurl
        
    # String representation for testing/development
    def __str__(self):
        s = "VideoContent(title='" + self.title + "', timestamp='" + self.timestamp + "', "\
            "duration=" + str(self.duration) + ", videourl=" + str(self.video_url()) + ", "\
            "imageurl=" + str(self.image_url()) + ")"
        return s.encode('utf-8', 'ignore')

# parses the video JSON into VideoContent
def _parse_video(jsonvideo):
    title = jsonvideo["headline"]
    # TODO: parse into datetime
    timestamp = jsonvideo["broadcastDate"]
    imageurls = _parse_image_urls(jsonvideo["images"][0]["variants"])
    videourls = _parse_video_urls(jsonvideo["mediadata"])
    # calculate duration using outMilli and inMilli, duration is not set in JSON
    duration = (jsonvideo["outMilli"] - jsonvideo["inMilli"]) / 1000    
    return VideoContent(title, timestamp, videourls, imageurls, duration);       

# parses the broadcast JSON into VideoContent
def _parse_broadcast(jsonbroadcast):
    title = jsonbroadcast["title"]
    # TODO: parse into datetime
    timestamp = jsonbroadcast["broadcastDate"]
    imageurls = _parse_image_urls(jsonbroadcast["images"][0]["variants"])
    # TODO: fetch and parse details JSON 
    videourls = { "h264l" : "TODO" }
    return VideoContent(title, timestamp, videourls, imageurls);

# parses the image variants JSON into a dict mapping name to url 
def _parse_image_urls(jsonvariants):
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

# parses the video mediadata JSON into a dict mapping name to url
def _parse_video_urls(jsonvariants):
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

def latest_videos():
    logger.info("retrieving videos");
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemand100_type-video.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = _parse_video(jsonvideo)
        videos.append(video) 
    logger.info("found "+str(len(videos))+" videos")
    return videos

def dossiers():
    logger.info("retrieving videos");
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemanddossier100.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = _parse_video(jsonvideo)
        videos.append(video)
    logger.info("found "+str(len(videos))+" videos")            
    return videos

def latest_broadcasts():
    logger.info("retrieving videos");    
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json")
    response = json.load(handle)
    for jsonbroadcast in response["latestBroadcastsPerType"]:
        video = _parse_broadcast(jsonbroadcast)
        videos.append(video)
    logger.info("found "+str(len(videos))+" videos")              
    return videos

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s')
    videos = latest_videos()
    print "Aktuelle Videos"     
    for video in videos:
        print video
    videos = dossiers()
    print "Dossier"
    for video in videos:
        print video
    videos = latest_broadcasts()
    print "Aktuelle Sendungen"
    for video in videos:
        print video
   
    
    
