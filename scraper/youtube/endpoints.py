import urllib.parse
import json
import re
import codecs

BASE_URL = 'https://www.youtube.com'

SEARCH_URL = 'https://www.youtube.com/results'
SEARCH_AJAX_REFERER = 'https://www.youtube.com/results?search_query=%s&sp=%s'

MEDIA_URL = 'https://www.youtube.com/watch?v=%s'
MEDIA_JSON_URL = 'https://youtube.com/get_video_info?html5=1&video_id=%s'

COMMENT_URL = 'https://www.youtube.com/all_comments?v=%s'
COMMENTS_AJAX_URL = 'https://www.youtube.com/comment_ajax'

CHANNEL_URL = 'https://www.youtube.com/channel/%s'
CHANNEL_INFO_URL = 'https://www.youtube.com/channel/%s/about'
CHANNEL_VIDEOS_URL = 'https://www.youtube.com/channel/%s/videos?view=0&sort=dd&flow=grid'

CHANNEL_URL2 = 'https://www.youtube.com/user/%s'
CHANNEL_INFO_URL2 = 'https://www.youtube.com/user/%s/about'
CHANNEL_VIDEOS_URL2 = 'https://www.youtube.com/user/%s/videos'


# CHANNEL_VIDEOS_AJAX_URL = 'https://www.youtube.com/channel/%s/videos?view=0&sort=dd&flow=grid'
CHANNEL_VIDEOS_AJAX_URL = 'https://www.youtube.com/browse_ajax'
CHANNEL_VIDEOS_AJAX_REFERER = 'https://www.youtube.com/channel/%s/videos?view=0&sort=dd&flow=grid'


def get_media_page_link(videoId: str):
	return MEDIA_URL % urllib.parse.quote_plus(videoId)

def get_media_json_link(videoId: str):
	return MEDIA_JSON_URL % urllib.parse.quote_plus(videoId)


def get_comment_page_link(videoId: str):
	return COMMENT_URL % urllib.parse.quote_plus(videoId)

def get_comment_ajax_link():
	return COMMENTS_AJAX_URL

def get_channel_url(channelId: str):
	return CHANNEL_URL % urllib.parse.quote_plus(channelId)

def get_channel_info_link(channelId: str):
	return CHANNEL_INFO_URL % urllib.parse.quote_plus(channelId)

def get_channel_info_link2(userId: str):
	return CHANNEL_INFO_URL2 % urllib.parse.quote_plus(userId)

def get_channel_videos_link(channelId: str):
	return CHANNEL_VIDEOS_URL % urllib.parse.quote_plus(channelId)

def get_channel_videos_ajax_link():
	return CHANNEL_VIDEOS_AJAX_URL

def get_channel_videos_ajax_referer(channelId: str):
	return CHANNEL_VIDEOS_AJAX_REFERER % urllib.parse.quote_plus(channelId)

def get_search_link():
	return SEARCH_URL

def get_search_ajax_referer(keyword: str, filters: str):
	return SEARCH_AJAX_REFERER % (urllib.parse.quote_plus(keyword), urllib.parse.quote_plus(filters))

def get_data_json(response_body):
	html = codecs.decode(response_body, encoding='utf-8', errors='ignore')
	data_regex = re.compile(r'window\[\"ytInitialData\"\] = (.*);')
	data = data_regex.findall(html)
	if len(data) > 0:
		return json.loads(data[0])
	else:
		data_regex = re.compile(r'var ytInitialData = (.*);\s*</script>')
		data = data_regex.findall(html)
		if len(data) > 0:
			value = data[0].split(';</script>')
			return json.loads(value[0])	
	return None

def get_data_json2(response_body):
	html = codecs.decode(response_body, encoding='utf-8', errors='ignore')
	data_regex = re.compile(r'var ytInitialPlayerResponse = (.*);var')
	data = data_regex.findall(html)
	if len(data) > 0:
		return json.loads(data[0])
	return None


def get_ajax_json(response_body):
	data = codecs.decode(response_body, encoding='utf-8', errors='ignore')
	data = json.loads(data)
	# with open('source.html', 'w') as file:
	# 	json.dump(data, file)
	if len(data) > 0:
		for value in data:
			if "response" in value:
				return value
	return None

def get_watch_next_response(html):
	data_regex = re.compile(r'&watch_next_response=({.*}}}}}}})&')
	data = data_regex.findall(html)

	if len(data) > 0:
		return json.loads(data[0])	
	return None	

def get_player_response(html):
	data_regex = re.compile(r'&player_response=({.*]})&')
	data = data_regex.findall(html)

	if len(data) > 0:
		return json.loads(data[0])	
	return None
	
def get_xml_json(response_body):
	html = codecs.decode(response_body, encoding='utf-8', errors='ignore')
	data1 = None
	data2 = None

	html = html.split('&')
	for data in html:
		if data.startswith('player_response='):
			data1 = data[16:]
			data1 = json.loads(urllib.parse.unquote(data1))
		elif data.startswith('watch_next_response='):
			data2 = data[20:]
			data2 = json.loads(urllib.parse.unquote(data2))		
	
	# with open('source.html', 'w') as file:
	# 	json.dump(data2, file)			
		
	# html = urllib.parse.unquote(html)
	# data1 = get_watch_next_response(html)
	# data2 = get_player_response(html)

	return [data1, data2]	

