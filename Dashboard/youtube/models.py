from datetime import datetime

from django.db import models


class Condition(models.Model):
    search_text = models.TextField(default="", blank=True)
    upload_date = models.TextField(null=True)
    type = models.TextField(null=True)
    duration = models.TextField(null=True)
    features = models.TextField(null=True)
    sort_by = models.TextField(null=True)


class Request(models.Model):
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, null=True)
    is_scheduled = models.BooleanField(default=False)
    time_received = models.DateTimeField(default=datetime.now)
    time_start_scraping = models.DateTimeField(default=None, null=True)
    time_end_scraping = models.DateTimeField(default=None, null=True)
    time_end = models.DateTimeField(default=None, null=True)
    time_last_updated = models.DateTimeField(default=datetime.now)
    status = models.TextField(default="Request Received")
    api_calls = models.PositiveIntegerField(default=0)

    def update_status(self, status):
        self.status = status
        self.time_last_updated = datetime.now()
        self.save()

    def add_error(self, error, code="-", severity=0):
        RequestError(request=self, description=error, severity=severity, code=code).save()


class User(models.Model):
    title = models.TextField(default=None, blank=True, null=True)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, null=True)
    description = models.TextField(default=None, blank=True, null=True)
    subscriber_count = models.BigIntegerField(default=-1, null=True)
    thumbnail_url = models.TextField(default=None, null=True, blank=True)
    banner_url = models.TextField(default=None, null=True, blank=True)
    view_count = models.BigIntegerField(default=-1, null=True)
    channel_id = models.CharField(max_length=150, primary_key=True)
    username = models.CharField(max_length=150,null=True, default=None)
    channel_name = models.CharField(max_length=150, null=True, default=None)
    register_type = models.IntegerField(default=1, null=True)
    published_at = models.DateField(default=None, null=True)
    is_registered = models.BooleanField(default=False, null=True)
    registered_on = models.DateTimeField(default=None, null=True)
    last_updated = models.DateTimeField(default=datetime.today)
    links = models.TextField(default=None, null=True)
    user_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    full_info = models.BooleanField(default=False)
    
    is_deleted = models.BooleanField(default=False, null=True)
    deleted_on = models.DateTimeField(default=None, null=True)

    def de_register(self):
        self.is_deleted = True
        self.deleted_on = datetime.now()
        self.is_registered = False
        self.save()

    def register(self):
        self.is_registered = True
        self.registered_on = datetime.now()
        self.is_deleted = False
        self.save()


class Media(models.Model):
    channel = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=150, primary_key=True)
    title = models.TextField(default=None, blank=True, null=True)
    description = models.TextField(default=None, blank=True, null=True)
    published_at = models.DateTimeField(default=None, null=True)
    view_count = models.BigIntegerField(default=-1, null=True)
    likes = models.BigIntegerField(default=-1, null=True)
    dislikes = models.BigIntegerField(default=-1, null=True)
    tags = models.TextField(default=None, blank=True, null=True)
    thumbnail_url = models.TextField(default=None, null=True, blank=True)
    last_updated = models.DateTimeField(default=datetime.today)
    full_info = models.BooleanField(default=False)
    content_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    content_media_url = models.TextField(default=None, null=True, blank=True)
    related_videos = models.ManyToManyField('self', through='RelatedVideos',
                                            symmetrical=False)


class RelatedVideos(models.Model):
    from_media = models.ForeignKey('Media', related_name='from_media', on_delete=models.CASCADE)
    to_media = models.ForeignKey('Media', related_name='to_media', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('from_media', 'to_media')


class RequestError(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.IntegerField(default=0, null=True, blank=True)
    code = models.CharField(max_length=256, default="-")
