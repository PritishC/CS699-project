import scrapy

from .. import endpoints
from ..exceptions import ExceptionClass
from ..items import AccountItem, ChannelVideoItem, MediaItem, SearchItem
from ..model.account import Account
from ..model.comment import Comment
from ..model.media import Media
from ..model.search import Search
from ..model.channel_videos import ChannelVideosList
from scraper_api import ScraperAPIClient
from scrapy.exceptions import UsageError
from twisted.python.failure import Failure
from urllib.parse import urlencode

class SearchSpider(scrapy.Spider):
	name = 'search'
	allowed_domains = ['www.youtube.com']
	client = ScraperAPIClient('7cb5caf807e61f97b73f19fc4a0414b1')
	
	_ORDER = {
		"date": "CAI",
		"relevance": "CAA",
		"viewcount": "CAM",
		"rating": "CAE"
	}

	_TYPE = {
		'video': 'SAhAB',
		'movie': 'SAhAE',
		'videoweek': 'SAggD',
		'movieweek': 'SBAgDEAQ='
	}

	def __init__(self, unique_id, order='date', type='video', itct=None, **kwargs):
		self.unique_id = unique_id
		self.order = order
		self.type = type
		self.itct = itct
		super(SearchSpider, self).__init__(**kwargs)
		
	def start_requests(self):
		if hasattr(self, 'keyword'):
			if self.order not in self._ORDER:
				raise UsageError("Invalid --order value, use order=VALUE(str)")
			else:
				self.filters = self._ORDER[self.order]
				if hasattr(self, 'date'):
					if self.date not in ["week"]:
						raise UsageError("Invalid --date value, use date=week(str)")
					self.filters += self._TYPE[self.type+self.date]
				else:	
					if self.type not in self._TYPE:
						raise UsageError("Invalid --type value, use type=VALUE(str)")
					self.filters += self._TYPE[self.type]
					
			if hasattr(self, 'continuation'):
				url = endpoints.get_search_link()
				referer = endpoints.get_search_ajax_referer(self.keyword, self.filters)
				headers = {
					'Referer': referer,
					# 'X-YouTube-Client-Name': '1',
					# 'X-YouTube-Client-Version': '2.20200422.04.00',
					'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
				}
				params = {
					'search_query': self.keyword,
					'sp': self.filters,
					'ctoken': self.continuation,
					'continuation': self.continuation,
					'itct': self.itct
				}
				url = url + '?' + urlencode(params)
				yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_ajax_search, method='GET', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
				# yield scrapy.Request(url=self.client.scrapyGet(url=url), callback=self.parse_ajax_search, method='GET', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
				# yield scrapy.FormRequest(url=url, callback=self.parse_ajax_search, formdata=params, headers=headers, method='POST', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
			else:
				url = endpoints.get_search_link()
				params = {
					'search_query': self.keyword,
					'sp': self.filters,
				}
				headers = {
					'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
					# 'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
				}
				url = url + '?' + urlencode(params)
				yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_search, method='GET', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
				# yield scrapy.Request(url=self.client.scrapyGet(url=url), callback=self.parse_search, method='GET', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
				# yield scrapy.FormRequest(url=url, callback=self.parse_search, formdata=params, method='POST', meta={'unique_id': self.unique_id, 'keyword': self.keyword, 'filters': self.filters}, errback=self.errback_httpbin)
		else:
			raise UsageError("Invalid --keyword value, use keyword=VALUE(str)")

	def parse_search(self, response):
		item = SearchItem()
		data = endpoints.get_data_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		item["search"] = Search({'data': data, 'keyword': response.meta['keyword'], 'filters': response.meta['filters']})
		item["error"] = None
		yield item

	def parse_ajax_search(self, response):
		item = SearchItem()
		data = endpoints.get_data_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		item["search"] = Search({'item': data, 'keyword': response.meta['keyword'], 'filters': response.meta['filters']})
		item["error"] = None
		yield item

	def errback_httpbin(self, failure):
		item = SearchItem()
		item["unique_id"] = self.unique_id
		item["search"] = None
		item["error"] = ExceptionClass.from_errback(failure)
		yield item
		

class ChannelVideosSpider(scrapy.Spider):
	name = 'channel_videos'
	allowed_domains = ['www.youtube.com']
	client = ScraperAPIClient('7cb5caf807e61f97b73f19fc4a0414b1')
	
	def __init__(self, unique_id, **kwargs):
		self.unique_id = unique_id
		super(ChannelVideosSpider, self).__init__(**kwargs)

	def start_requests(self):
		if hasattr(self, 'channelId'):	
			if hasattr(self, 'continuation') and hasattr(self, 'itct'):
				url = endpoints.get_channel_videos_ajax_link()
				referer = endpoints.get_channel_videos_ajax_referer(self.channelId)
				headers = {
					'Referer': referer,
					'X-YouTube-Client-Name': '1',
					'X-YouTube-Client-Version': '2.20200422.04.00',
					'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
					# 'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
				}
				params = {
					'ctoken': self.continuation,
					'continuation': self.continuation,
					'itct': self.itct
				}
				yield scrapy.FormRequest(url=url, callback=self.parse_ajax_search, formdata=params, headers=headers, method='POST', meta={'unique_id': self.unique_id, 'id': self.channelId}, errback=self.errback_httpbin)
			else:
				url = endpoints.get_channel_videos_link(self.channelId)
				headers = {
					'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
				}
				yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_search, method='GET', meta={'unique_id': self.unique_id, 'id': self.channelId}, errback=self.errback_httpbin)
				# yield scrapy.Request(url=url, callback=self.parse_search, method='GET', meta={'unique_id': self.unique_id, 'id': self.channelId}, errback=self.errback_httpbin)
		else:
			raise UsageError("Invalid --channelId value, use channelId=VALUE(str)")

	def parse_search(self, response):
		item = ChannelVideoItem()
		data = endpoints.get_data_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		item["channel_videos"] = ChannelVideosList({'data': data, 'id': response.meta['id']})
		item["error"] = None
		yield item

	def parse_ajax_search(self, response):
		item = ChannelVideoItem()
		data = endpoints.get_ajax_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		item["channel_videos"] = ChannelVideosList({'ajax': data, 'id': response.meta["id"]})
		item["error"] = None
		yield item

	def errback_httpbin(self, failure):
		item = ChannelVideoItem()
		item["unique_id"] = self.unique_id
		item["channel_videos"] = None
		item["error"] = ExceptionClass.from_errback(failure)
		yield item
		

class ChannelSpider(scrapy.Spider):
	name = 'channel'
	allowed_domains = ['www.youtube.com']
	client = ScraperAPIClient('7cb5caf807e61f97b73f19fc4a0414b1')

	def __init__(self, unique_id, **kwargs):
		self.unique_id = unique_id
		super(ChannelSpider, self).__init__(**kwargs)

	def start_requests(self):
		if hasattr(self, 'channelId'):
			url = endpoints.get_channel_info_link(self.channelId)
			headers = {
				'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
			}
			yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_channel, method='GET', meta={'unique_id': self.unique_id, 'id': self.channelId}, errback=self.errback_httpbin)
			# yield scrapy.Request(url=url, callback=self.parse_channel, method='GET', meta={'unique_id': self.unique_id, 'id': self.channelId}, errback=self.errback_httpbin)
		elif hasattr(self, 'userId'):
			url = endpoints.get_channel_info_link2(self.userId)
			headers = {
				'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
			}
			yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_channel, method='GET', meta={'unique_id': self.unique_id, 'id': self.userId}, errback=self.errback_httpbin)
		else:
			raise UsageError("Invalid --channelId value, use channelId=VALUE(str)")

	def parse_channel(self, response):
		item = AccountItem()
		data = endpoints.get_data_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		item["account"] = Account({'id': response.meta['id'], 'data': data})
		item["error"] = None
		yield item

	def errback_httpbin(self, failure):
		item = AccountItem()
		item["unique_id"] = self.unique_id
		item["account"] = None
		item["error"] = ExceptionClass.from_errback(failure)
		yield item
	

class VideoSpider(scrapy.Spider):
	name = 'video'
	allowed_domains = ['www.youtube.com']
	client = ScraperAPIClient('7cb5caf807e61f97b73f19fc4a0414b1')

	def __init__(self, unique_id, **kwargs):
		self.unique_id = unique_id
		super(VideoSpider, self).__init__(**kwargs)

	def start_requests(self):
		if hasattr(self, 'videoId'):
			headers = {
				'accept-language': 'ja,en;q=0.9,en-US;q=0.8,und;q=0.7',
			}
			url = endpoints.get_media_json_link(self.videoId)
			yield scrapy.Request(url=self.client.scrapyGet(url=url, headers=headers), headers=headers, callback=self.parse_media, method='GET', meta={'unique_id': self.unique_id, 'id': self.videoId}, errback=self.errback_httpbin)
		else:
			raise UsageError("Invalid --videoId value, use videoId=VALUE(str)")

	def parse_media(self, response):
		item = MediaItem()
		data = endpoints.get_xml_json(response.body)
		item["unique_id"] = response.meta['unique_id']
		if len(data) > 1:
			item["media"] = Media({'data': data[0], 'id': response.meta['id'], 'xdata': data[1]})
		elif len(data) > 0:
			item["media"] = Media({'data': data[0], 'id': response.meta['id'], 'xdata': None})
		else:
			item["media"] = None
		item["error"] = None
		yield item

	def errback_httpbin(self, failure):
		item = MediaItem()
		item["unique_id"] = self.unique_id
		item["media"] = None
		item["error"] = ExceptionClass.from_errback(failure)
		yield item

