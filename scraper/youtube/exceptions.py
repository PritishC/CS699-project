import logging
import json
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from twisted.python.failure import Failure


class ExceptionClass:
	def __init__(self, url, code, _type, traceback):
		super(ExceptionClass, self).__init__()
		self.url = url
		self.code = code
		self._type = _type
		self.traceback = traceback

	@classmethod
	def from_errback(cls, failure):
		url = None
		code = None
		_type = None
		if failure.check(HttpError):
			response = failure.value.response
			url = response.url
			code = response.status
			_type = "HttpError"
		elif failure.check(DNSLookupError):
			request = failure.request
			url = request.url
			code = 523
			_type = "DNSLookupError"
		elif failure.check(TimeoutError, TCPTimedOutError):
			request = failure.request
			url = request.url
			code = 504
			_type = "TimeoutError"

		c = cls(url, code, _type, repr(failure))
		return c	

	@classmethod
	def from_custom(cls, url, code, _type, traceback):
		c = cls(url, code, _type, traceback)
		return c

	def __repr__(self):
		return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)
