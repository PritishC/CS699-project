import requests
from scrapyd_api import ScrapydAPI
from uuid import uuid4

scrapyd = ScrapydAPI("http://localhost:6800")

def schedule_search(unique_id, project, spider, keyword, order=None, type=None, continuation=None, itct=None):
	if continuation != None and itct != None:
		task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, keyword=keyword, continuation=continuation, itct=itct)
		return task

	task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, keyword=keyword)
	return task	

def schedule_channel_videos(unique_id, project, spider, channelId, continuation=None, itct=None):
	if continuation != None and itct != None:
		task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, channelId=channelId, continuation=continuation, itct=itct)
		return task	
	task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, channelId=channelId)
	return task	

def schedule_channel(unique_id, project, spider, channelId):
	task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, channelId=channelId)
	return task

def schedule_video(unique_id, project, spider, videoId):
	task = scrapyd.schedule(unique_id=unique_id, project=project, spider=spider, videoId=videoId)
	return task	


unique_id = str(uuid4())
# ChannelSpider
task = schedule_channel(unique_id, "youtube", "channel", "UC0C-w0YjGpqDXGB8IHb662A")

# VideoSpider
# task = schedule_video(unique_id, "youtube", "video", "EW4pNzAbVao")

# ChannelVideosSpider
# task = schedule_channel_videos(unique_id, "youtube", "channel_videos", "UCah2QQgUmunTFX4z87uALGQ")
# task = schedule_channel_videos(unique_id, "youtube", "channel_videos", "UCP1iRaFlS5EYjJBryFV9JPw", "", "")

# SearchSpider
# task = schedule_search(unique_id, "youtube", "search", "nogizaka46")
# task = schedule_search(unique_id, "youtube", "search", "nogizaka46", "date", "video", "", "")

print(task)
print(unique_id)