import json
import time
import re 
from datetime import datetime


def stringToInt(text):
	if text == None:
		return None
	if text == '':
		return text
	
	if 'B' in text:
		text = text.replace(u'M', u'')
		text = float(text)*1000000000
	elif 'M' in text:
		text = text.replace(u'M', u'')
		text = float(text)*1000000
	elif 'K' in text:
		text = text.replace(u'K', u'')
		text = float(text)*1000
	elif '万' in text:
		text = text.replace(u'万', u'')
		text = float(text)*10000
	elif '億' in text:
		text = text.replace(u'億', u'')
		text = float(text)*100000000

	try:
		return int(text)
	except Exception as e:
		print("Error: ", e)		

	return None

def filter_subscribers(text):
	if text == None:
		return None
	else:
		text = text.replace(u'subscribers', u' ')
		text = text.replace(u'subscriber', u' ')
		text = text.replace(u'チャンネル登録者数', u' ')
		text = text.replace(u'人', u' ')
		text = text.replace(u',', u'')
		text = text.replace(u'+', u' ')
		text = text.replace(u'\\n', u' ')
		text = ' '.join(text.split())
	return stringToInt(text)
	
def filter_views(text):
	if text == None:
		return None
	else:
		text = text.replace(u'No views', u'0')
		text = text.replace(u'views', u' ')
		text = text.replace(u'view', u' ')
		text = text.replace(u'回視聴', u' ')
		text = text.replace(u'視聴回数', u' ')
		text = text.replace(u'回', u' ')
		text = text.replace(u'watching', u' ')
		text = text.replace(u'now', u' ')
		text = text.replace(u'人が視聴中', u' ')
		text = text.replace(u'Recommended for you', u' ')
		text = text.replace(u',', u'')
		text = text.replace(u'+', u' ')
		text = text.replace(u'\\n', u' ')
		text = ' '.join(text.split())
	return stringToInt(text)

def filter_date(text):
	if text == None:
		return None
	else:
		text = text.replace(u'Joined', u' ')
		text = text.replace(u'に登録', u' ')
		text = text.replace(u'Premiered', u' ')
		text = text.replace(u'に公開済み', u' ')
		text = text.replace(u'\\n', u' ')
		text = ' '.join(text.split())
	return stringToDate(text)

def stringToDate(text):
	if text == None:
		return None
	elif text == '':
		return text
	else:
		regex = r"[0-9]{4,4}/[0-9]{1,2}/[0-9]{1,2}"	
		match = re.search(regex, text) 
		if match != None:
			tdate = datetime.strptime(match.group(), '%Y/%m/%d')
			return tdate.timestamp()
		else:
			regex2 = r"[A-Za-z]{3,3} [0-9]{1,2}, [0-9]{4,4}"
			match2 = re.search(regex2, text)
			if match != None:
				tdate = datetime.strptime(match.group(), '%b %d, %Y')
				return tdate.timestamp()

	return None


class InitializerModel:

	def __init__(self, props=None):

		self._is_new = True
		self._is_loaded = False
		"""init data was empty"""
		self._is_load_empty = True
		self._modified = None
		"""Array of initialization data"""
		self._data = {}

		self.modified = time.time()
		if len(props) > 0:
			self._init(props)

	def _init(self, props):
		"""
		:param props: props array
		:return: None
		"""
		for key in props.keys():
			try:
				self._init_properties_custom(props[key], key, props)
			except AttributeError:
				# if function does not exist fill help data array
				self._data[key] = props[key]

		self._is_new = False
		self._is_loaded = True
		self._is_load_empty = False

	def __repr__(self):
		return json.dumps(self, default=lambda o: o.__dict__)

	def _fullURL(self, url):
		if url[0:2] == '//':
			return 'https:' + url
		return url	
	
	def _get_simpleText(self, data):
		if "simpleText" in data:
			return self._filter_text(data["simpleText"])
		elif "runs" in data:
			result = ""
			for run in data["runs"]:
				if "text" in run:
					result += run["text"]
			if result != "":
				return self._filter_text(result)
		return data
	
	def _filter_text(self, text):
		if text == None:
			text = ''
		else:
			text = text.replace(u'+', u' ')
			text = text.replace(u'\\n', u' ')
			text = ' '.join(text.split())
		# return ''.join(text).strip()
		return text
