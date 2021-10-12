BOT_NAME = 'youtube'

SPIDER_MODULES = ['youtube.spiders']
NEWSPIDER_MODULE = 'youtube.spiders'

# LOG_LEVEL = 'WARNING'
LOG_FILE = 'error.log'

ROBOTSTXT_OBEY = False

# HTTP_PROXY = 'http://127.0.0.1:8118'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
# DEFAULT_REQUEST_HEADERS = {}

# CONCURRENT_REQUESTS = 16
# DOWNLOAD_DELAY = 2
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# COOKIES_ENABLED = False
# COOKIES_DEBUG = False

PROXY_POOL_ENABLED = False
# PROXY_POOL_TRY_WITH_HOST = False
# PROXY_POOL_PAGE_RETRY_TIMES = 10
# PROXY_POOL_FORCE_REFRESH = True

DOWNLOADER_MIDDLEWARES = {
	# 'youtube.middlewares.ProxyMiddleware': 543,
	# 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
	# 'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
	# 'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
	# 'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
}

ITEM_PIPELINES = {
	'youtube.pipelines.YoutubePipeline': 300,
}

