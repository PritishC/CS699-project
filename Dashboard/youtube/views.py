import sys;sys.path.append('../')
import json
from datetime import datetime, timedelta, time
import csv
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI

from .models import User, Media, Request, Condition, RelatedVideos
from .tasks import youtube_initial, youtube_daily

import requests
import codecs
import os
import math

@csrf_exempt
def save_keywords(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        input = request_body["input"]
        with open("/home/ubuntu/cron_tasks/youtube_keywords.json","w") as f:
            f.write(input)
        with open("dummy_save_log.txt","a") as f:
            f.write("New Youtube Save Request Received at %s. Input :{'input': %s} \n" %(datetime.now(), input))
        return JsonResponse({"message": "Job parameters saved successfully", "response": "200"})
    except Exception as e:
        print("Error",e)
        with open("dummy_save_log.txt","a") as f:
            f.write("New Youtube Request Received at %s. Request has exception %s \n" %(datetime.now(), e))
        return JsonResponse({"message": "Improper Request", "response": "500"}, status=500)

def get_keywords(request):
    try:
        with open("/home/ubuntu/cron_tasks/youtube_keywords.json","r") as f:
            input = f.read()
        return JsonResponse({"message": "Get Success", "input": input}, status=200)
    except Exception as e:
        print("Error",e)
        with open("dummy_save_log.txt","a") as f:
            f.write("New Youtube Get Request Received at %s. Request has exception %s \n" %(datetime.now(), e))
        return JsonResponse({"message": "Improper Request", "response": "500"}, status=500)

@csrf_exempt
def initial(request):
    request_body = json.loads(request.body.decode('utf-8'))
    keyword = request_body["keyword"]
    #keyword = "乃木坂46"
    filters = {"upload_date": None, "type": None, "duration": None, "features": None, "sort_by": None}
    c = Condition(search_text=keyword, **filters)
    c.save()
    r = Request(condition=c)
    r.save()

    youtube_initial.delay(r.id)
    return JsonResponse(data={"message": "We have scheduled your request"})


@csrf_exempt
def daily(request):
    r = Request(condition=None, is_scheduled=True, time_received=datetime.now())
    r.save()
    youtube_daily.delay(r.id)
    data = {}
    data['message'] = "We have scheduled your request"
    return JsonResponse(data=data)


@csrf_exempt
def register(request):
    data = {}
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        channel_id = request_body["channel_id"]
        if 'channel_type' in request_body:
            type = request_body['channel_type']
        else:
            type = 1
        if 'keyword' in request_body:
            keyword = Condition(search_text=request_body['keyword'])
            keyword.save()
        else:
            keyword = None
        try:
            if type == 1:
                channel = User.objects.get(channel_id=channel_id)
            elif type == 2:
                channel = User.objects.get(username=channel_id)
            elif type==3:
                channel = User.objects.get(channel_name= channel_id)
            if keyword is not None:
                channel.condition = keyword
            channel.register_type = type
            channel.save()
            channel.register()
            data['message'] = "Channel Registered Successfully"
        except ObjectDoesNotExist:
            if type==1:
                channel = User(channel_id=channel_id, register_type=1)
            elif type==2:
                channel = User(channel_id=channel_id, username = channel_id, register_type=2)
            elif type==3:
                channel = User(channel_id=channel_id, channel_name = channel_id, register_type=3)
            if keyword is not None:
                channel.condition = keyword
            channel.save()
            channel.register()
            data['message'] = "New Channel Inserted and Registered"
    except Exception as e:
        data['message'] = str(e)
    logger.info("channel_id: {}, result: {}".format(channel_id, data))
    return JsonResponse(data=data)

@csrf_exempt
def de_register(request):
    data = {}
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        channel_id = request_body["channel_id"]
        if 'channel_type' in request_body:
            type = request_body['channel_type']
        else:
            type = 1
        try:
            if type==1:
                channel = User.objects.get(channel_id=channel_id)
            elif type==2:
                channel = User.objects.get(username=channel_id)
            elif type==3:
                channel = User.objects.get(channel_name=channel_id)
            channel.de_register()
            data['message'] = "Channel DeRegistered Successfully"
        except ObjectDoesNotExist:
            data['message'] = "Channel doesn't exsit."
    except Exception as e:
        data['message'] = str(e)
    logger.info("channel_id: {}, result: {}".format(channel_id, data))
    return JsonResponse(data=data)
    

def default(o):
    if isinstance(o, datetime):
        return o.isoformat()


def create_file(a, header, filename, rename=None):
    df = pd.DataFrame.from_records(a)
    df.columns = header
    if rename is not None:
        df.rename(columns=rename, inplace=True)
    df.to_csv("location"+filename, index=False)



def create_file_csv(a, header, filename, rename={}):
    filename = open("location"+filename, mode='w')
    csv_analysis = csv.writer(filename, quoting=csv.QUOTE_ALL)
    for i in range(len(header)):
        if header[i] in rename:
            header[i]=rename[header[i]]
    csv_analysis.writerow(header)
    for item in a:
        csv_analysis.writerow(item)
