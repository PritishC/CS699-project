from .initializer_model import InitializerModel, filter_views, filter_date
from .account import Account
from .comment import Comment

class _Statistics:
	def __init__(self, views: str, likes: str, dislikes: str):
		self.views = filter_views(views)
		self.likes = filter_views(likes)
		self.dislikes = filter_views(dislikes)

class Media(InitializerModel):
	def __init__(self, props=None):
		self.identifier = None
		self.title = None
		self.upload_date = None
		self.duration = None
		self.description = None
		self.thumbnail_url = None
		self.genre = None
		# self.is_paid = None
		# self.is_unlisted = None
		# self.is_family_friendly = None
		self.statistics = None
		self.related_videos = None
		# Account Object
		self.owner = None
		super(Media, self).__init__(props)

	def _init_properties_custom(self, value, prop, array):

		if prop == 'id':
			self.identifier = value

		standart_properties = [
		]

		if prop in standart_properties:
			self.__setattr__(prop, value)

		if prop == 'item':		# Video Object Data Parsing
			if value != None:
				data = None
				if "videoRenderer" in value:				# Search videos list
					data = value["videoRenderer"]
				elif "gridVideoRenderer" in value:			# Channel videos list
					data = value["gridVideoRenderer"]
				elif "compactVideoRenderer" in value:		# Related videos list
					data = value["compactVideoRenderer"]
				# elif "endScreenVideoRenderer" in value:		# After video play Suggestions 
				# 	data = value["endScreenVideoRenderer"]
				if data != None:	
					if "videoId" in data:
						self.identifier = data["videoId"]
					if "title" in data:
						self.title = self._get_simpleText(data["title"])
					if "descriptionSnippet" in data:
						self.description = self._get_simpleText(data["descriptionSnippet"])
					if "publishedTimeText" in data:
						self.upload_date = filter_date(self._get_simpleText(data["publishedTimeText"]))
					if "lengthText" in data:
						self.duration = self._get_simpleText(data["lengthText"])
					elif "thumbnailOverlays" in data:
						thumbnailOverlays = data["thumbnailOverlays"]
						if len(thumbnailOverlays) > 0:
							for thumbnailOverlay in thumbnailOverlays:
								if "thumbnailOverlayTimeStatusRenderer" in thumbnailOverlay:
									if "text" in thumbnailOverlay["thumbnailOverlayTimeStatusRenderer"]:
										self.duration = self._get_simpleText(thumbnailOverlay["thumbnailOverlayTimeStatusRenderer"]["text"])
										break
					if "thumbnail" in data:
						thumbnail = data["thumbnail"]
						if "thumbnails" in thumbnail:
							images = thumbnail["thumbnails"]
							if len(images) > 0:
								self.thumbnail_url = self._fullURL(images[-1]["url"])
					views = None
					likes = None
					dislikes = None
					if "viewCountText" in data:
						views = self._get_simpleText(data["viewCountText"])
					if views != None or likes != None or dislikes != None:
						self.statistics = _Statistics(views, likes, dislikes)
					
					if "gridVideoRenderer" not in value:
						# Channel Info from Related Videos Object 	
						channelItem = {'compactOwnerRenderer': {}}
						channelId = None
						if "channelId" in data:
							channelId = data["channelId"]
						if "longBylineText" in data:
							channelItem["compactOwnerRenderer"]["title"] = data["longBylineText"]
						elif "shortBylineText" in data:
							channelItem["compactOwnerRenderer"]["title"] = data["shortBylineText"]
						if "title" in channelItem["compactOwnerRenderer"] and channelItem["compactOwnerRenderer"]["title"]:
							if "runs" in channelItem["compactOwnerRenderer"]["title"]:
								runs = channelItem["compactOwnerRenderer"]["title"]["runs"]
								for run in runs:
									if "navigationEndpoint" in run:
										channelItem["compactOwnerRenderer"]["navigationEndpoint"] = run["navigationEndpoint"]
										break
						if "channelThumbnail" in data:
							channelItem["compactOwnerRenderer"]["thumbnail"] = data["channelThumbnail"]
						elif "channelThumbnailSupportedRenderers" in data:
							if "channelThumbnailWithLinkRenderer" in data["channelThumbnailSupportedRenderers"]:
								if "thumbnail" in data["channelThumbnailSupportedRenderers"]["channelThumbnailWithLinkRenderer"]:
									channelItem["compactOwnerRenderer"]["thumbnail"] = data["channelThumbnailSupportedRenderers"]["channelThumbnailWithLinkRenderer"]["thumbnail"]
						if "ownerBadges" in data:
							if len(data["ownerBadges"]) > 0:
								channelItem["compactOwnerRenderer"]["badges"] = data["ownerBadges"]
						self.owner = Account({'id': channelId, 'item': channelItem})
		
		if prop == 'data' or prop == 'xdata':		# Video Page Parsing 
			if value != None:
				views = None
				likes = None
				dislikes = None

				# owner_title = None
				# owner_channelUrl = None
				# owner_identifier = None

				# if "videoDetails" in value:
				# 	if "videoId" in value["videoDetails"]:
				# 		self.identifier = value["videoDetails"]["videoId"]	
				# 	if "title" in value["videoDetails"]:
				# 		self.title = self._get_simpleText(value["videoDetails"]["title"])
				# 	if "lengthSeconds" in value["videoDetails"]:	
				# 		self.duration = self._get_simpleText(value["videoDetails"]["lengthSeconds"])
				# 	if "shortDescription" in value["videoDetails"]:
				# 		self.description = self._get_simpleText(value["videoDetails"]["shortDescription"])
				# 	if "viewCount" in value["videoDetails"]:
				# 		views = self._get_simpleText(value["videoDetails"]["viewCount"])
				# 	if "thumbnail" in value["videoDetails"]:
				# 		thumbnail = value["videoDetails"]["thumbnail"]
				# 		if "thumbnails" in thumbnail:
				# 			images = thumbnail["thumbnails"]
				# 			if len(images) > 0:
				# 				self.thumbnail_url = self._fullURL(images[-1]["url"])

				# if "microformat" in value:
				# 	if "playerMicroformatRenderer" in value["microformat"]:
				# 		microformat = value["microformat"]["playerMicroformatRenderer"]		
				# 		if "thumbnail" in microformat:
				# 			thumbnail = microformat["thumbnail"]
				# 			if "thumbnails" in thumbnail:
				# 				images = thumbnail["thumbnails"]
				# 				if len(images) > 0:
				# 					self.thumbnail_url = self._fullURL(images[-1]["url"])

				# 		if "title" in microformat:
				# 			self.title = self._get_simpleText(microformat["title"])
				# 		if "description" in microformat:
				# 			self.description = self._get_simpleText(microformat["description"])
				# 		if "lengthSeconds" in microformat:
				# 			self.duration = self._get_simpleText(microformat["lengthSeconds"])
				# 		if "viewCount" in microformat:
				# 			views = self._get_simpleText(microformat["viewCount"])
				# 		if "uploadDate" in microformat:
				# 			self.upload_date = filter_date(self._get_simpleText(microformat["uploadDate"]))
				# 		if "category" in microformat:
				# 			self.genre = self._get_simpleText(microformat["category"])

				# 		if "ownerChannelName" in microformat:
				# 			owner_title = self._get_simpleText(microformat["ownerChannelName"])	
				# 		if "ownerProfileUrl" in microformat:
				# 			owner_channelUrl = self._get_simpleText(microformat["ownerProfileUrl"])	
				# 		if "externalChannelId" in microformat:
				# 			owner_identifier = self._get_simpleText(microformat["externalChannelId"])	
				
				# if self.owner == None:
				# 	self.owner = Account({"identifier": owner_identifier, "title": owner_title, "channelUrl": owner_channelUrl})
				

				if "contents" in value:
					if "twoColumnWatchNextResults" in value["contents"]:
						if "results" in value["contents"]["twoColumnWatchNextResults"]:
							results = value["contents"]["twoColumnWatchNextResults"]["results"]
							if "results" in results:
								if "contents" in results["results"]:
									contents = results["results"]["contents"]
									for content in contents:
										if "videoPrimaryInfoRenderer" in content:
											if "title" in content["videoPrimaryInfoRenderer"]:
												self.title = self._get_simpleText(content["videoPrimaryInfoRenderer"]["title"])
											
											if "viewCount" in content["videoPrimaryInfoRenderer"]:
												viewObj = content["videoPrimaryInfoRenderer"]["viewCount"]
												if "videoViewCountRenderer" in viewObj:
													if "viewCount" in viewObj["videoViewCountRenderer"]:
														views = self._get_simpleText(viewObj["videoViewCountRenderer"]["viewCount"])

											if "dateText" in content["videoPrimaryInfoRenderer"]:
												self.upload_date = filter_date(self._get_simpleText(content["videoPrimaryInfoRenderer"]["dateText"]))

											if "sentimentBar" in content["videoPrimaryInfoRenderer"]:
												if "sentimentBarRenderer" in content["videoPrimaryInfoRenderer"]["sentimentBar"]:
													if "tooltip" in content["videoPrimaryInfoRenderer"]["sentimentBar"]["sentimentBarRenderer"]:
														tooltip = content["videoPrimaryInfoRenderer"]["sentimentBar"]["sentimentBarRenderer"]["tooltip"]
														if "/" in tooltip:
															likes, dislikes = tooltip.split("/")

										if "videoSecondaryInfoRenderer" in content:
											if "description" in content["videoSecondaryInfoRenderer"]:
												self.description = self._get_simpleText(content["videoSecondaryInfoRenderer"]["description"])

											if "owner" in content["videoSecondaryInfoRenderer"]:
												self.owner = Account({"item": content["videoSecondaryInfoRenderer"]["owner"]})
										
											if "metadataRowContainer" in content["videoSecondaryInfoRenderer"]:
												if "metadataRowContainerRenderer" in content["videoSecondaryInfoRenderer"]["metadataRowContainer"]:
													if "rows" in content["videoSecondaryInfoRenderer"]["metadataRowContainer"]["metadataRowContainerRenderer"]:
														rows = content["videoSecondaryInfoRenderer"]["metadataRowContainer"]["metadataRowContainerRenderer"]["rows"]
														for row in rows:
															if "metadataRowRenderer" in row:
																if "contents" in row["metadataRowRenderer"]:
																	contents = row["metadataRowRenderer"]["contents"]
																	if len(contents) > 0:
																		self.genre = self._get_simpleText(contents[0])
																		break

						if "secondaryResults" in value["contents"]["twoColumnWatchNextResults"]:
							secondaryResults = value["contents"]["twoColumnWatchNextResults"]["secondaryResults"]	
							if "secondaryResults" in secondaryResults:
								if "results" in secondaryResults["secondaryResults"]:
									results = secondaryResults["secondaryResults"]["results"]
									if len(results) > 0:	
										self.related_videos = []
										for result in results:
											if "compactVideoRenderer" in result:
												self.related_videos.append(Media({'item': result}))
											elif "compactAutoplayRenderer" in result: 
												if "contents" in result["compactAutoplayRenderer"]:
													autoplayContents = result["compactAutoplayRenderer"]["contents"]
													if len(autoplayContents) > 0:
														for autoplayContent in autoplayContents:
															if "compactVideoRenderer" in autoplayContent:
																self.related_videos.append(Media({'item': autoplayContent}))
				if views != None or likes != None or dislikes != None:												
					self.statistics = _Statistics(views, likes, dislikes)
				
				if "videoDetails" in value:
					if "lengthSeconds" in value["videoDetails"]:
						self.duration = self.convert_duration(value["videoDetails"]["lengthSeconds"])

					if "thumbnail" in value["videoDetails"]:
							thumbnail = value["videoDetails"]["thumbnail"]
							if "thumbnails" in thumbnail:
								images = thumbnail["thumbnails"]
								if len(images) > 0:
									self.thumbnail_url = self._fullURL(images[-1]["url"])
				if "microformat" in value:
					if "playerMicroformatRenderer" in value["microformat"]:
						microformat = value["microformat"]["playerMicroformatRenderer"]
						if "category" in microformat:
							if self.genre == None:
								self.genre = self._get_simpleText(microformat["category"])					

		if prop == 'data2':
			if value != None:
				if "videoDetails" in value:
					if "lengthSeconds" in value["videoDetails"]:
						self.duration = self.convert_duration(value["videoDetails"]["lengthSeconds"])

					if "thumbnail" in value["videoDetails"]:
							thumbnail = value["videoDetails"]["thumbnail"]
							if "thumbnails" in thumbnail:
								images = thumbnail["thumbnails"]
								if len(images) > 0:
									self.thumbnail_url = self._fullURL(images[-1]["url"])
				if "microformat" in value:
					if "playerMicroformatRenderer" in value["microformat"]:
						microformat = value["microformat"]["playerMicroformatRenderer"]
						if "category" in microformat:
							if self.genre == None:
								self.genre = self._get_simpleText(microformat["category"])					


	def convert_duration(self, seconds):
		if isinstance(seconds, str):
			seconds = int(seconds)
		minutes = seconds // 60
		seconds = seconds % 60
		return "%d:%d" % (minutes, seconds)