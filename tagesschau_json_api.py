try: import json
except ImportError: import simplejson as json
import urllib2
import logging

# TODO: (Sendungs) Archiv, URL correct? http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100_week-true.json"
# TODO: LiveStream/TSin100, see multimedia http://www.tagesschau.de/api/multimedia/video/ondemand100.json 

logger = logging.getLogger(__name__)

class VideoContent(object):
    """Represents a single video or broadcast.

    Attributes:
        title: A String with the video's title
        timestamp: A datetime when this video was broadcast
        videourls: A dict mapping video variant Strings to their URL Strings
        imageurls: A dict mapping image variants Strings to their URL Strings
        duration: An integer representing the length of the video in seconds
    """    
    
    def __init__(self, title, timestamp, videourls, imageurls=None, duration=None):
        """Inits VideoContent with the given values."""
        self.title = title
        # datetime
        self.timestamp = timestamp
        # duration in seconds
        self.duration = duration
        # video/mediadata names mapped to urls
        self.videourls = videourls
        # image variant names mapped to urls
        self.imageurls = imageurls
    
    def video_url(self, quality):
        """Returns the video URL String for the given quality.
        
        Falls back to lower qualities if no corresponding video is found.
        
        Args:
            quality: One of 'S', 'M' or 'L'

        Returns:
            A URL String for the given quality or None if no URL could be found.

        Raises:
            ValueError: If the given quality is invalid
        """
        if (not quality in ['S', 'M', 'L']):
            raise ValueError("quality must be one of 'S', 'M', 'L'")
        # TODO: use adaptivestreaming if available?
        videourl = _get(self.videourls, "adaptivestreaming")
        if(quality == 'L' or not videourl):
            videourl = _get(self.videourls, "h264l")
        if(quality == 'M' or not videourl):    
            videourl = _get(self.videourls, "h264m")
        if(quality == 'S' or not videourl):    
            videourl = _get(self.videourls, "h264s")
        return videourl

    def image_url(self):
        """Returns the URL String of the image for this video."""
        imageurl = _get(self.imageurls, "gross16x9")
        if(not imageurl):
            # fallback for Wetter
            imageurl = _get(self.imageurls, "grossgalerie16x9")
        return imageurl
        
    def __str__(self):
        """Returns a String representation for development/testing."""
        s = "VideoContent(title='" + self.title + "', timestamp='" + self.timestamp + "', "\
            "duration=" + str(self.duration) + ", videourl=" + str(self.video_url('L')) + ", "\
            "imageurl=" + str(self.image_url()) + ")"
        return s.encode('utf-8', 'ignore')

# 
def _get(dic, key):
    """Helper method that returns None if key is not found."""
    if key in dic:
        return dic[key]
    else:
        return None
    

def _parse_video(jsonvideo):
    """Parses the video JSON into a VideoContent object."""
    title = jsonvideo["headline"]
    # TODO: parse into datetime
    timestamp = jsonvideo["broadcastDate"]
    imageurls = _parse_image_urls(jsonvideo["images"][0]["variants"])
    videourls = _parse_video_urls(jsonvideo["mediadata"])
    # calculate duration using outMilli and inMilli, duration is not set in JSON
    duration = (jsonvideo["outMilli"] - jsonvideo["inMilli"]) / 1000    
    return VideoContent(title, timestamp, videourls, imageurls, duration);       

def _parse_broadcast(jsonbroadcast):
    """Parses the broadcast JSON into a VideoContent object."""
    title = jsonbroadcast["title"]
    # TODO: parse into datetime
    timestamp = jsonbroadcast["broadcastDate"]
    imageurls = _parse_image_urls(jsonbroadcast["images"][0]["variants"])
    # TODO: fetch and parse details JSON 
    videourls = { "h264l" : "TODO" }
    return VideoContent(title, timestamp, videourls, imageurls);

def _parse_image_urls(jsonvariants):
    """Parses the image variants JSON into a dict mapping variant name to URL.""" 
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

def _parse_video_urls(jsonvariants):
    """Parses the video mediadata JSON into a dict mapping variant name to URL."""
    variants = {}
    for jsonvariant in jsonvariants:
        for name, url in jsonvariant.iteritems():
            variants[name] = url
    return variants

def latest_videos():
    """Retrieves the latest videos.
        
        Returns: 
            A list of VideoContent items.
    """
    logger.info("retrieving videos");
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemand100_type-video.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = _parse_video(jsonvideo)
        videos.append(video) 
    logger.info("found " + str(len(videos)) + " videos")
    return videos

def dossiers():
    """Retrieves the latest dossier videos.
        
        Returns: 
            A list of VideoContent items.
    """    
    logger.info("retrieving videos");
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemanddossier100.json")
    response = json.load(handle)
    for jsonvideo in response["videos"]:
        video = _parse_video(jsonvideo)
        videos.append(video)
    logger.info("found " + str(len(videos)) + " videos")            
    return videos

def latest_broadcasts():
    """Retrieves the latest broadcast videos.
        
        Returns: 
            A list of VideoContent items.
    """        
    logger.info("retrieving videos");    
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json")
    response = json.load(handle)
    for jsonbroadcast in response["latestBroadcastsPerType"]:
        video = _parse_broadcast(jsonbroadcast)
        videos.append(video)
    logger.info("found " + str(len(videos)) + " videos")              
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
   
    
    
