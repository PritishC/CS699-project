import csv
import json
import mysql.connector
from .items import AccountItem, ChannelVideoItem, MediaItem, SearchItem


class YoutubePipeline(object):
	def open_spider(self, spider):
		self.db = mysql.connector.connect(
			host="host",
			user="user",
			passwd="password",
			database="database_name",
			use_unicode=True, 
			charset="utf8"
		)
		self.cursor = self.db.cursor()

	def close_spider(self, spider):
		self.cursor.close()
		self.db.close()

	def add_item_toDB(self, unique_id, data, error):
		query = "INSERT INTO output_scrapyitem (unique_id, data, error) VALUES (%s, %s, %s)"
		try:
			self.cursor.execute(query, tuple([unique_id, data, error]))
			self.db.commit()
		except mysql.connector.Error as e:
			print("MySQL Error: ", e, query)

	def process_item(self, item, spider):
		# print(item)
		# data = json.dumps(item['search'], default=lambda o: o.__dict__)
		# with open('data.json', 'w') as outfile:
		# 	json.dump(json.loads(data), outfile)
		json_error = json.dumps(item["error"], default=lambda o: o.__dict__)
		if isinstance(item, AccountItem):
			json_data = json.dumps(item["account"], default=lambda o: o.__dict__)
			self.add_item_toDB(item["unique_id"], json_data, json_error)
		elif isinstance(item, ChannelVideoItem):
			json_data = json.dumps(item["channel_videos"], default=lambda o: o.__dict__)
			self.add_item_toDB(item["unique_id"], json_data, json_error)	
		elif isinstance(item, MediaItem):
			json_data = json.dumps(item["media"], default=lambda o: o.__dict__)
			self.add_item_toDB(item["unique_id"], json_data, json_error)
		elif isinstance(item, SearchItem):
			json_data = json.dumps(item["search"], default=lambda o: o.__dict__)
			self.add_item_toDB(item["unique_id"], json_data, json_error)

		return item
