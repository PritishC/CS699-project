import json
from .initializer_model import InitializerModel, filter_views, filter_subscribers, filter_date
from .. import endpoints

class _Links:
	def __init__(self, text: str, url: str):
		self.url = url
		self.text = text	

class _Statistics:
	def __init__(self, views: str, subscribers: str, media_count: str):
		self.views = filter_views(views)
		self.subscribers = filter_subscribers(subscribers)
		self.media_count = filter_views(media_count)

class Account(InitializerModel):
	def __init__(self, props=None):
		self.identifier = None
		self.title = None
		self.channelUrl = None
		self.description = None
		self.links = None
		self.isFamilySafe = None
		self.rssUrl = None
		self.profile_thumbnail = None
		self.banner_thumbnail = None
		self.created_date = None
		self.is_verified = None
		self.statistics = None
		# self.media_list = None
				
		super(Account, self).__init__(props)

	def _init_properties_custom(self, value, prop, array):

		if prop == 'id':
			self.identifier = value

		standart_properties = [
			'identifier',
			'title',
			'channelUrl',
		]

		if prop in standart_properties:
			self.__setattr__(prop, value)

		if prop == "item":
			if value != None:	
				data = None

				views = None	
				subscribers = None
				media_count = None

				if "videoOwnerRenderer" in value:		# Video Page Owner Object
					data = value["videoOwnerRenderer"]
				if "compactOwnerRenderer" in value:		# Related Video Owner Object
					data = value["compactOwnerRenderer"]		

				if data != None:
					if "title" in data:
						self.title = self._get_simpleText(data["title"])
					if "thumbnail" in data:
						if "thumbnails" in data["thumbnail"]:	
								images = data["thumbnail"]["thumbnails"]
								if len(images) > 0:
									self.profile_thumbnail = self._fullURL(images[-1]["url"])
					if "subscriberCountText" in data:
						subscribers = self._get_simpleText(data["subscriberCountText"])
					if "badges" in data:
						for badge in data["badges"]:
							if "metadataBadgeRenderer" in badge:
								if "tooltip" in badge["metadataBadgeRenderer"]:	
									if badge["metadataBadgeRenderer"]["tooltip"] == "Verified":
										self.is_verified = True
					if "navigationEndpoint" in data:
						if "browseEndpoint" in data["navigationEndpoint"]:
							browseEndpoint = data["navigationEndpoint"]["browseEndpoint"]
							if "browseId" in browseEndpoint:
								self.identifier = browseEndpoint["browseId"]
								if self.identifier != None or self.identifier != "":		
									self.channelUrl = endpoints.get_channel_url(self.identifier)
				if views != None or subscribers != None or media_count != None:
					self.statistics = _Statistics(views, subscribers, media_count)

		if prop == 'data':
			if value != None:
				# f = open('source.html', 'w')
				# f.write(json.dumps(value))
				# f.close()	
				views = None	
				subscribers = None
				media_count = None
				if "metadata" in value:	
					if "channelMetadataRenderer" in value["metadata"]:
						meta = value["metadata"]["channelMetadataRenderer"]
						print("Here?")
						if "externalId" in meta:
							self.identifier = meta["externalId"]
						if "channelUrl" in meta:
							self.channelUrl = meta["channelUrl"]	
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
					print("Here header?")
					if "c4TabbedHeaderRenderer" in value["header"]:
						header = value["header"]["c4TabbedHeaderRenderer"]		
						if "channelId" in header:
							print("Here2?")
							self.identifier = header["channelId"]
							self.channelUrl = 'https://www.youtube.com/channel/' + self.identifier
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
												if "primaryLinks" in channelMeta:
													primaryLinks = channelMeta["primaryLinks"]
													if len(primaryLinks) > 0:
														self.links = []
														for primaryLink in primaryLinks:
															self.links.append(self.get_link(primaryLink))

			if views != None or subscribers != None or media_count != None:
					self.statistics = _Statistics(views, subscribers, media_count)
			print(self.identifier)
					
	def get_link(self, data):
		text = None
		url = None
		if "title" in data:
			text = self._get_simpleText(data["title"])
		if "navigationEndpoint" in data:
			if "urlEndpoint" in data["navigationEndpoint"]:
				if "url" in data["navigationEndpoint"]["urlEndpoint"]:
					url = data["navigationEndpoint"]["urlEndpoint"]["url"]
						
		return _Links(text, url)
