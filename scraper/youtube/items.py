import scrapy


class AccountItem(scrapy.Item):
	unique_id = scrapy.Field()
	account = scrapy.Field()
	error = scrapy.Field()

class ChannelVideoItem(scrapy.Item):
	unique_id = scrapy.Field()
	channel_videos = scrapy.Field()
	error = scrapy.Field()

class MediaItem(scrapy.Item):
	unique_id = scrapy.Field()
	media = scrapy.Field()
	error = scrapy.Field()

class SearchItem(scrapy.Item):
	unique_id = scrapy.Field()
	search = scrapy.Field()
	error = scrapy.Field()
