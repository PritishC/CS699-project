from .media import Media
from .account import Account
from .. import endpoints
from .initializer_model import filter_views, filter_subscribers, filter_date

class _Statistics:
	def __init__(self, views: int, subscribers: int, media_count: int):
		self.views = filter_views(views)
		self.subscribers = filter_subscribers(subscribers)
		self.media_count = filter_views(media_count)

class _Pagination:
	def __init__(self, continuation: str, itct: str):
		self.continuation = continuation
		self.itct = itct

class ChannelVideosList(Account):
	def __init__(self, props=None):
		self.media_list = None
		self.pagination = None
		super(ChannelVideosList, self).__init__(props)

	def _init_properties_custom(self, value, prop, array):

		if prop == 'id':
			self.identifier = value

		standart_properties = [
		]

		if prop in standart_properties:
			self.__setattr__(prop, value)

		if prop == 'data':
			if value != None:
				
				views = None	
				subscribers = None
				media_count = None
				if "metadata" in value:	
					if "channelMetadataRenderer" in value["metadata"]:
						meta = value["metadata"]["channelMetadataRenderer"]
						if "title" in meta:
							self.title = meta["title"]
						if "channelUrl" in meta:
							self.channelUrl = meta["channelUrl"]
						if "description" in meta:
							self.description = meta["description"]
						if "isFamilySafe" in meta:
							self.isFamilySafe = meta["isFamilySafe"]
						if "rssUrl" in meta:	
							self.rssUrl = meta["rssUrl"]
						if "avatar" in meta:	
							if "thumbnails" in meta["avatar"]:	
								images = meta["avatar"]["thumbnails"]
								if len(images) > 0:
									self.profile_thumbnail = self._fullURL(images[-1]["url"])

				if "header" in value:	
					if "c4TabbedHeaderRenderer" in value["header"]:
						header = value["header"]["c4TabbedHeaderRenderer"]		
						if "banner" in header:
							if "thumbnails" in header["banner"]:	
								images = header["banner"]["thumbnails"]
								if len(images) > 0:
									self.banner_thumbnail = self._fullURL(images[-1]["url"])	
						if "subscriberCountText" in header:
							subscribers = self._get_simpleText(header["subscriberCountText"])	
						if "badges" in header:
							for badge in header["badges"]:
								if "metadataBadgeRenderer" in badge:
									if "tooltip" in badge["metadataBadgeRenderer"]:	
										if badge["metadataBadgeRenderer"]["tooltip"] == "Verified":
											self.is_verified = True	

				if "contents" in value:
					if "twoColumnBrowseResultsRenderer" in value["contents"]:
						if "tabs" in value["contents"]["twoColumnBrowseResultsRenderer"]:
							tabs = value["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
							if len(tabs) > 0:
								for tab in tabs:
									if "tabRenderer" in tab:
										if tab["tabRenderer"]["title"] == 'About' or tab["tabRenderer"]["title"] == '概要':
											content = []
											try:	
												content = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
											except:
												pass
											if len(content) > 0:
												channelMeta = content[0]["channelAboutFullMetadataRenderer"]
												if "viewCountText" in channelMeta:
													views = self._get_simpleText(channelMeta["viewCountText"])
												if "joinedDateText" in channelMeta:
													self.created_date = filter_date(self._get_simpleText(channelMeta["joinedDateText"]))
										if tab["tabRenderer"]["title"] == "Videos" or tab["tabRenderer"]["title"] == "動画":
											gridRenderer = {}
											try:	
												gridRenderer = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["gridRenderer"]
											except:
												pass
											if "items" in gridRenderer:
												items = gridRenderer["items"]
												if len(items) > 0:
													self.media_list = []
													for item in items:
														self.media_list.append(Media({'item': item}))
											if "continuations" in gridRenderer:
												continuation, itct = self.get_pagination_token(gridRenderer["continuations"])		
												if continuation != None or itct != None:
													self.pagination = _Pagination(continuation, itct)

			if views != None or subscribers != None or media_count != None:
					self.statistics = _Statistics(views, subscribers, media_count)
		
		if prop == 'ajax':
			if value != None:
				if "response" in value:
					data = value["response"]
					if "continuationContents" in data:
						continuationContents = data["continuationContents"]
						if "gridContinuation" in continuationContents:
							gridContinuation = continuationContents["gridContinuation"]
							if "items" in gridContinuation:
								if len(gridContinuation["items"]) > 0:
									self.media_list = []
									for item in gridContinuation["items"]:	
										media = Media({'item': item})
										self.media_list.append(media)
							if "continuations" in gridContinuation:
								continuation, itct = self.get_pagination_token(gridContinuation["continuations"])
								if continuation != None or itct != None:
									self.pagination = _Pagination(continuation, itct)

	def get_pagination_token(self, continuations):
		continuation = None
		itct = None
		if len(continuations) > 0:
			for arr in continuations:
				if "nextContinuationData" in arr: 
					if "continuation" in arr["nextContinuationData"] and "clickTrackingParams" in arr["nextContinuationData"]:
						continuation = arr["nextContinuationData"]["continuation"]
						itct = arr["nextContinuationData"]["clickTrackingParams"]
					return continuation, itct

