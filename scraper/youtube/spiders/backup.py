##### media.py
# class Uploader:
# 	def __init__(self, channel_id: str = None, name: str = None, thumbnail_url: str = None, is_verified: bool = None):
# 		self.channel_id = channel_id
# 		self.name = name
# 		self.thumbnail_url = thumbnail_url
# 		self.is_verified = is_verified

# 	@classmethod
# 	def from_soup(cls, data, channel_id: str):
# 		# Get uploader's name
# 		uploader_div = data.find('div', class_='yt-user-info')
# 		name = uploader_div.a.get_text()
# 		# Is the uploader verified?
# 		verified_span = uploader_div.span
# 		is_verified = verified_span is not None

# 		# Get uploader's thumbnail URL
# 		thumbnail_url = data.find('span', class_='yt-thumb-clip').img['data-thumb']
# 		return cls(channel_id, name, thumbnail_url, is_verified)


# class Statistics:
# 	def __init__(self, views: int, likes: int, dislikes: int):
# 		self.views = views
# 		self.likes = likes
# 		self.dislikes = dislikes

# 	@classmethod
# 	def from_soup(cls, data, views: int):
# 		# Get like count
# 		like_button = data.find('button', class_='like-button-renderer-like-button-unclicked')
# 		likes = int(Media._remove_comma(like_button.span.string))

# 		# Get dislike count
# 		dislike_button = data.find('button', class_='like-button-renderer-dislike-button-unclicked')
# 		dislikes = int(Media._remove_comma(dislike_button.span.string))
# 		return cls(views, likes, dislikes)

# class Media(InitializerModel):
# 	def __init__(self, props=None):
# 		self.identifier = None
# 		self.title = None
# 		self.upload_date = None
# 		self.duration = None
# 		self.description = None
# 		self.thumbnail_url = None
# 		self.genre = None
# 		self.is_paid = None
# 		self.is_unlisted = None
# 		self.is_family_friendly = None
# 		self.uploader = None
# 		self.statistics = None
# 		# self.related_videos = []

# 		super(Media, self).__init__(props)

# 	def _init_properties_custom(self, value, prop, array):

# 		if prop == 'id':
# 			self.identifier = value

# 		standart_properties = [
# 		]

# 		if prop in standart_properties:
# 			self.__setattr__(prop, value)

# 		if prop == 'data':
# 			data = value
# 			if data != None:
# 				# Get data from tags having `itemprop` attribute
# 				for tag in data.find_all(itemprop=True, recursive=False):
# 					key = tag['itemprop']
# 					if key == 'name':
# 						# Get video's title
# 						self.title  = tag['content'] 
# 					elif key == 'datePublished':
# 						# Get video's upload date
# 						self.upload_date = tag['content']
# 					elif key == 'duration':
# 						# Get video's duration
# 						self.duration = tag['content']
# 					elif key == 'genre':
# 						# Get video's genre (category)
# 						self.genre = tag['content']
# 					elif key == 'paid':
# 						# Is the video paid?
# 						self.is_paid = Media._is_true(tag['content'])
# 					elif key == 'unlisted':
# 						# Is the video unlisted?
# 						self.is_unlisted = Media._is_true(tag['content'])
# 					elif key == 'isFamilyFriendly':
# 						# Is the video family friendly?
# 						self.is_family_friendly = Media._is_true(tag['content'])
# 					elif key == 'thumbnailUrl':
# 						# Get video thumbnail URL
# 						self.thumbnail_url = tag['href']
# 					elif key == 'interactionCount':
# 						# Get video's views
# 						views = int(tag['content'])
# 					elif key == 'channelId':
# 						# Get uploader's channel ID
# 						channel_id = tag['content']
# 				# Get video description
# 				description_para = data.find('p', id='eow-description')
# 				for br in description_para.find_all('br'):
# 					br.replace_with('\n')
# 				self.description = description_para.get_text()
				
# 				self.uploader = Uploader.from_soup(data, channel_id)
# 				self.statistics = Statistics.from_soup(data, views)
# 			else:
# 				print("No data!!")

	# @staticmethod	
	# def _is_true(string):
	# 	return string.lower() not in ['false', '0']

	# @staticmethod	
	# def _remove_comma(string):
	# 	return ''.join(string.split(','))
	

############# api.py ### name = 'channel'

	# def parse_channel2(self, response):
	# 	print(response.url)
	# 	channel_id = response.meta['id']
	# 	channel_url = 'https://www.youtube.com/channel/' + channel_id
	# 	title = response.xpath("//meta[@name='title']/@content").extract_first()
	# 	profile_pic_url = response.xpath('//link[@rel="image_src"]/@href').extract_first()
	# 	print("Title: ", title)
	# 	print("Profile pic: ", profile_pic_url)
	# 	subcribers = response.css('div.primary-header-upper-section-block div.primary-header-actions span.channel-header-subscription-button-container span.subscribed::text').extract_first()
	# 	print("Subcribers: ", subcribers)		

	# 	meta_div = response.css('div.about-metadata-container')
	# 	if len(meta_div) > 0:
	# 		description = meta_div[0].css('div.about-description *::text').extract()
	# 		print("Description: ", self.filter_text(('').join(description)))
		
	# 		stats_div = meta_div[0].css('div.about-stats')
	# 		if len(stats_div) > 0:	
	# 			stats = stats_div[0].css('span.about-stat')
	# 			if len(stats) > 0:
	# 				for stat in stats:
	# 					temp = stat.css('::text').extract()
	# 					value = self.filter_text(('').join(temp))
	# 					if 'views' in value:	
	# 						views = self.filter_channel_views(value)
	# 						print("Views: ", views)
	# 					elif 'Joined' in value:
	# 						created_date = self.filter_channel_data(value)		
	# 						print("Created date: ", created_date)

	# def filter_channel_data(self, text):
	# 	if text == None:
	# 		text = ''
	# 	else:
	# 		text = text.replace(u'Joined', u' ')
	# 		text = ' '.join(text.split())

	# 	return text	

	# def filter_channel_views(self, text):
	# 	if text == None:
	# 		text = ''
	# 	else:
	# 		text = text.replace(u'views', u' ')
	# 		text = text.replace(u',', u'')
	# 		text = text.replace(u'•', u' ')
	# 		text = ' '.join(text.split())

	# 	return text	

# Media Spider
# class VideoSpider(scrapy.Spider):
# 	name = 'video'
# 	allowed_domains = ['www.youtube.com']

# 	def start_requests(self):
# 		videoId = 'OQWEVfyJak0'
# 		url = endpoints.get_media_page_link(videoId)
# 		headers = {
# 			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# 			'Accept-Language': 'en',
# 			'USER_AGENT': ''
# 		}
# 		yield scrapy.Request(url=url, callback=self.parse_media, headers=headers, method='GET', meta={'id': videoId}, errback=self.errback_httpbin)

# 	def parse_media(self, response):
# 		print(response.url)
# 		soup = BeautifulSoup(response.body, 'lxml')

# 		data = soup.find(id='watch7-content')
# 		if data != None:    
# 			try:
# 				media = Media({'data': data, 'id': response.meta['id']})
# 			except Exception as e:
# 				print("Error", e)
# 			self.print_media(media)
# 		else:
# 			f = open('source.html', 'w')
# 			f.write(soup.prettify())
# 			f.close()



# Comment Object

# class CommentSpider(scrapy.Spider):
# 	name = 'comment'
# 	allowed_domains = ['www.youtube.com']

# 	def start_requests(self):
# 		videoId = 'OQWEVfyJak0'
# 		url = endpoints.get_media_page_link(videoId)
# 		headers = {
# 			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# 			'Accept-Language': 'en',
# 			# 'USER_AGENT': ''
# 			'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
# 		}
# 		yield scrapy.Request(url=url, callback=self.parse_media, method='GET', meta={'id': videoId}, errback=self.errback_httpbin)

# 	def parse_media(self, response):
# 		html = response.body.decode('utf-8')
# 		f = open('source.html', 'w')
# 		f.write(html)
# 		f.close()
# 		# page_token = self.find_value(html, 'data-token')
# 		# print(page_token)
# 		session_token = self.find_value(html, 'XSRF_TOKEN', 4)
# 		print(session_token)
	
# 		url = endpoints.get_comment_ajax_link()
# 		params = {
# 			"video_id": response.meta["id"],
# 			"session_token": session_token,
# 			"action_load_comments": "1",
# 			"filter": response.meta["id"],
# 			"order_by_time": "True",
# 			"order_menu": "True"
# 		}

# 		yield scrapy.FormRequest(url=url, formdata=params, callback=self.parse_comment, method='POST', errback=self.errback_httpbin)

# 	def parse_comment(self, response):
# 		print(response.url)
# 		html = json.loads(response.body) 
# 		# f = open('source.html', 'w')
# 		# f.write(html['html_content'])
# 		# f.close()
# 		print(self.extract_comments(html['html_content']))

# 	def extract_comments(self, html):
# 		tree = lxml.html.fromstring(html)
# 		item_sel = CSSSelector('.comment-item')
# 		text_sel = CSSSelector('.comment-text-content')
# 		time_sel = CSSSelector('.time')
# 		author_sel = CSSSelector('.user-name')

# 		comments = []
# 		for item in item_sel(tree):
# 			comments.append({
# 				'cid': item.get('data-cid'),
# 				'text': text_sel(item)[0].text_content(),
# 				'time': time_sel(item)[0].text_content().strip(),
# 				'author': author_sel(item)[0].text_content()
# 			})
# 		print("Length: ", len(comments))
# 		return comments

# 	def find_value(self, html, key, num_chars=2):
# 		pos_begin = html.find(key) + len(key) + num_chars
# 		pos_end = html.find('"', pos_begin)
# 		return html[pos_begin: pos_end]

# 	def errback_httpbin(self, failure):
# 		# log all failures
# 		self.logger.error(repr(failure))
# 		# In case you want to do something special for some errors,
# 		# you may need the failure's type:
# 		if failure.check(HttpError):
# 			# These exceptions come from HttpError spider middleware
# 			# you can get the non-200 response
# 			response = failure.value.response
# 			self.logger.error('HttpError on %s', response.url)
# 		elif failure.check(DNSLookupError):
# 			# This is the original request
# 			request = failure.request
# 			self.logger.error('DNSLookupError on %s', request.url)
# 		elif failure.check(TimeoutError, TCPTimedOutError):
# 			request = failure.request
# 			self.logger.error('TimeoutError on %s', request.url)

# headers = {
# 	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# 	'Accept-Language': 'en',
# 	'USER_AGENT': '',
# 	'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
# 	'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
# }


#### Account print
	# def __repr__(self):
	# 	# print("Identifier: ", self.identifier)
	# 	# print("Title: ", self.title)
	# 	# print("ChannelUrl: ", self.channelUrl)
	# 	# print("Description: ", self.description)
	# 	# print("IsFamilySafe: ", self.isFamilySafe)
	# 	# print("RssUrl: ", self.rssUrl)
	# 	# print("Profile_thumbnail: ", self.profile_thumbnail)
	# 	# print("Banner_thumbnail: ", self.banner_thumbnail)
	# 	# print("Created_date: ", self.created_date)
	# 	# print("Is_verified: ", self.is_verified)

	# 	# if self.statistics == None:
	# 	# 	print("Statistics: ", "None")
	# 	# else:
	# 	# 	print("Statistics: ")
	# 	# 	print("\tViews: ", str(self.statistics.views))	
	# 	# 	print("\tSubscribers: ", str(self.statistics.subscribers))	
	# 	# 	print("\tMedia_count: ", str(self.statistics.media_count))	

	# 	string = f"""
	# 	Id: {self.identifier}
	# 	Title: {self.title}
	# 	ChannelUrl: {self.channelUrl}
	# 	Description: {self.description}
	# 	IsFamilySafe: {self.isFamilySafe}
	# 	RssUrl {self.rssUrl}
	# 	Profile Thumbnail: {self.profile_thumbnail}
	# 	Banner Thumbnail: {self.banner_thumbnail}
	# 	Created_date: {self.created_date}
	# 	Is_verified: {self.is_verified}
	# 	Views: {None if self.statistics == None else self.statistics.views}
	# 	Subscribers: {None if self.statistics == None else self.statistics.subscribers}
	# 	Media_count: {None if self.statistics == None else self.statistics.media_count}
	# 	"""

	# 	return textwrap.dedent(string)
