try: import json
except ImportError: import simplejson as json
import urllib2
import logging

# TODO: Datetime parsing for timestamp
# TODO: LiveStream/TSin100, see multimedia http://www.tagesschau.de/api/multimedia/video/ondemand100.json 

logger = logging.getLogger("plugin.video.tagesschau.api")

class VideoContent(object):
    """Represents a single video or broadcast.

    Attributes:
        title: A String with the video's title
        timestamp: A datetime when this video was broadcast
        imageurls: A dict mapping image variants Strings to their URL Strings
        videourls: A dict mapping video variant Strings to their URL Strings
        duration: An integer representing the length of the video in seconds
        description: A String describing the video content
    """       
    def __init__(self, title, timestamp, videourls=None, imageurls=None, duration=None, description=None):
        """Inits VideoContent with the given values."""
        self.title = title
        # datetime
        self.timestamp = timestamp
        # video/mediadata names mapped to urls
        self._videourls = videourls
        # image variant names mapped to urls
        self._imageurls = imageurls
        # duration in seconds
        self.duration = duration
        # description of content
        self.description = description
        
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
        videourl = _get(self._videourls, "adaptivestreaming")
        if(quality == 'L' or not videourl):
            videourl = _get(self._videourls, "h264l")
        if(quality == 'M' or not videourl):    
            videourl = _get(self._videourls, "h264m")
        if(quality == 'S' or not videourl):    
            videourl = _get(self._videourls, "h264s")
        return videourl

    def image_url(self):
        """Returns the URL String of the image for this video."""
        imageurl = _get(self._imageurls, "gross16x9")
        if(not imageurl):
            # fallback for Wetter
            imageurl = _get(self._imageurls, "grossgalerie16x9")
        return imageurl
        
    def __str__(self):
        """Returns a String representation for development/testing."""
        s = "VideoContent(title='" + self.title + "', timestamp='" + self.timestamp + "', "\
            "duration=" + str(self.duration) + ", videourl=" + str(self.video_url('L')) + ", "\
            "imageurl=" + str(self.image_url()) + ", description=" + str(self.description) + ")"
        return s.encode('utf-8', 'ignore')


class LazyVideoContent(VideoContent):
    """Represents a single video or broadcast that fetches its video urls attributes lazily.

    Attributes:
        title: A String with the video's title
        timestamp: A datetime when this video was broadcast
        imageurls: A dict mapping image variants Strings to their URL Strings
        detailsurl: A String pointing to the detail JSON for this video
        duration: An integer representing the length of the video in seconds
        description: A String describing the video content
    """  
    def __init__(self, title, timestamp, detailsurl, imageurls=None, duration=None, description=None):
        VideoContent.__init__(self, title, timestamp, None, imageurls, duration, description)
        self.detailsurl = detailsurl
        self.detailsfetched = False
      
    def video_url(self, quality):
        """Overwritten to fetch videourls lazily."""
        if(not self.detailsfetched):
            self._fetch_details()
        return VideoContent.video_url(self, quality)    
    
    def _fetch_details(self):
        """Fetches videourls from detailsurl."""
        logger = logging.getLogger("plugin.video.tagesschau.api.LazyVideoContent")
        logger.info("fetching details from " + self.detailsurl)
        handle = urllib2.urlopen(self.detailsurl)
        jsondetails = json.load(handle)
        self._videourls = _parse_video_urls(jsondetails["fullvideo"][0]["mediadata"])       
        self.detailsfetched = True
        logger.info("fetched details")


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
    return VideoContent(title, timestamp, videourls, imageurls, duration)       

def _parse_broadcast(jsonbroadcast):
    """Parses the broadcast JSON into a VideoContent object."""
    title = jsonbroadcast["title"]
    # TODO: parse into datetime
    timestamp = jsonbroadcast["broadcastDate"]
    imageurls = _parse_image_urls(jsonbroadcast["images"][0]["variants"])
    details = jsonbroadcast["details"]
    description = None
    if("topics" in jsonbroadcast):
        description = ", ".join(jsonbroadcast["topics"])
    # return LazyVideoContent that retrieves details JSON lazily
    return LazyVideoContent(title, timestamp, details, imageurls, None, description)

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
    logger.info("retrieving videos")
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/video/ondemand100~_type-video.json")
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
    logger.info("retrieving videos")
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
    logger.info("retrieving videos")    
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json")
    response = json.load(handle)
    for jsonbroadcast in response["latestBroadcastsPerType"]:
        video = _parse_broadcast(jsonbroadcast)
        videos.append(video)
    logger.info("found " + str(len(videos)) + " videos")              
    return videos

def archived_broadcasts():
    """Retrieves the archive broadcast videos.
        
        Returns: 
            A list of VideoContent items.
    """        
    logger.info("retrieving videos")    
    videos = []
    handle = urllib2.urlopen("http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100~_week-true.json")
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
    videos = archived_broadcasts()
    print "Sendungensarchiv"
    for video in videos:
        print video   
    
    
