import time
import json
from .initializer_model import InitializerModel
from .media import Media


class _Pagination:
	def __init__(self, continuation: str, itct: str):
		self.continuation = continuation
		self.itct = itct

class Search(InitializerModel):
	def __init__(self, props=None):
		self.keyword = None
		self.filters = None
		self.videos = None
		self.pagination = None
		super(Search, self).__init__(props)

	def _init_properties_custom(self, value, prop, array):

		standart_properties = [
			'keyword', 'filters'
		]

		if prop in standart_properties:
			self.__setattr__(prop, value)

		if prop == 'data':		# Search Page Parsing
			if value != None:
				if "contents" in value:
					if "twoColumnSearchResultsRenderer" in value["contents"]:
						if "primaryContents" in value["contents"]["twoColumnSearchResultsRenderer"]:
							primaryContents = value["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]
							if "sectionListRenderer" in primaryContents:
								if "contents" in primaryContents["sectionListRenderer"]:
									tcontents = primaryContents["sectionListRenderer"]["contents"]
									if len(tcontents) > 0:
										for ttcontents in tcontents:
											if "itemSectionRenderer" in ttcontents:	
												if "contents" in ttcontents["itemSectionRenderer"]:
													contents = ttcontents["itemSectionRenderer"]["contents"]
													if len(contents) > 0:
														self.videos = []
														for content in contents:
															if "videoRenderer" in content:
																self.videos.append(Media({"item": content}))
												if "continuations" in ttcontents["itemSectionRenderer"]:
													continuation, itct = self.get_pagination_token(ttcontents["itemSectionRenderer"]["continuations"])
													if continuation != None or itct != None:
														self.pagination = _Pagination(continuation, itct)
											if "continuationItemRenderer" in ttcontents:
												continuation, itct = self.get_pagination_token(ttcontents["continuationItemRenderer"])
												if continuation != None:
													self.pagination = _Pagination(continuation, itct)
		if prop == 'item':		# Search Page Parsing
			if value != None:
				if "continuationContents" in value:
					if "itemSectionContinuation" in value["continuationContents"]:
						if "contents" in value["continuationContents"]["itemSectionContinuation"]:
							contents = value["continuationContents"]["itemSectionContinuation"]["contents"]
							if len(contents) > 0:
								self.videos = []
								for content in contents:
									if "videoRenderer" in content:
										self.videos.append(Media({"item": content}))
						if "continuations" in value["continuationContents"]["itemSectionContinuation"]:
							continuation, itct = self.get_pagination_token(value["continuationContents"]["itemSectionContinuation"]["continuations"])
							if continuation != None or itct != None:
								self.pagination = _Pagination(continuation, itct)

					if "sectionListContinuation" in value["continuationContents"]:
						if "contents" in value["continuationContents"]["sectionListContinuation"]:
							tcontents = value["continuationContents"]["sectionListContinuation"]["contents"]
							if len(tcontents) > 0:
								for ttcontents in tcontents:
									if "itemSectionRenderer" in ttcontents:	
										if "contents" in ttcontents["itemSectionRenderer"]:
											contents = ttcontents["itemSectionRenderer"]["contents"]
											if len(contents) > 0:
												self.videos = []
												for content in contents:
													if "videoRenderer" in content:
														self.videos.append(Media({"item": content}))
										if "continuations" in ttcontents["itemSectionRenderer"]:
											continuation, itct = self.get_pagination_token(ttcontents["itemSectionRenderer"]["continuations"])
											if continuation != None or itct != None:
												self.pagination = _Pagination(continuation, itct)
									if "continuationItemRenderer" in ttcontents:
										continuation, itct = self.get_pagination_token(ttcontents["continuationItemRenderer"])
										if continuation != None:
											self.pagination = _Pagination(continuation, itct)			
				
				if "onResponseReceivedCommands" in value:
					response_command = value["onResponseReceivedCommands"]						
					if len(response_command) > 0:
						for command in response_command:
							if "appendContinuationItemsAction" in command:
								if "continuationItems" in command["appendContinuationItemsAction"]:
									tcontents = command["appendContinuationItemsAction"]["continuationItems"]
									if len(tcontents) > 0:
										for ttcontents in tcontents:
											if "itemSectionRenderer" in ttcontents:	
												if "contents" in ttcontents["itemSectionRenderer"]:
													contents = ttcontents["itemSectionRenderer"]["contents"]
													if len(contents) > 0:
														self.videos = []
														for content in contents:
															if "videoRenderer" in content:
																self.videos.append(Media({"item": content}))
												if "continuations" in ttcontents["itemSectionRenderer"]:
													continuation, itct = self.get_pagination_token(ttcontents["itemSectionRenderer"]["continuations"])
													if continuation != None or itct != None:
														self.pagination = _Pagination(continuation, itct)
											if "continuationItemRenderer" in ttcontents:
												continuation, itct = self.get_pagination_token(ttcontents["continuationItemRenderer"])
												if continuation != None:
													self.pagination = _Pagination(continuation, itct)	
	def get_pagination_token(self, continuations):
		continuation = None
		itct = None
		if "continuationEndpoint" in continuations:
			if "continuationCommand" in continuations["continuationEndpoint"]:
				if "token" in continuations["continuationEndpoint"]["continuationCommand"]:
					continuation = continuations["continuationEndpoint"]["continuationCommand"]["token"]
					return continuation, itct
		else:	
			if len(continuations) > 0:
				for arr in continuations:
					if "nextContinuationData" in arr: 
						if "continuation" in arr["nextContinuationData"]:
							continuation = arr["nextContinuationData"]["continuation"]
						if "clickTrackingParams" in arr["nextContinuationData"]:
							itct = arr["nextContinuationData"]["clickTrackingParams"]
						return continuation, itct
		return continuation, itct
