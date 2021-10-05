from datetime import datetime

from django.db import models

from output.models import ScrapyItem


class ScrapyRequest(models.Model):
    task_id = models.CharField(max_length=256)
    unique_id = models.CharField(max_length=256)
    project = models.CharField(max_length=256)
    spider = models.CharField(max_length=256)
    parameters = models.TextField(default="{}")
    time_started = models.DateTimeField(default=datetime.now)
    time_ended = models.DateTimeField(default=None, null=True, blank=True)
    status = models.TextField(default="Scraping")
    # output = models.ForeignKey(ScrapyItem, default=None, null=True, on_delete=models.SET_NULL)

    def update_status(self, status):
        self.status = status
        self.time_ended = datetime.now()
        self.save()
