from datetime import datetime, timedelta, date, time
import datetime as dt

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
import random
from dashboard.models import ScrapyRequest
from youtube.models import RequestError, User, Condition, Request
import pandas as pd

def home(request):
    pass

def get_requests():
    month_start=datetime.now().replace(day=1)
    filters = {'project': 'youtube', 'time_started__gt': month_start}
    requests_info = list(ScrapyRequest.objects.filter(**filters).values("status", "project", "time_started"))
    df = pd.DataFrame(requests_info)

    if df.empty:
        data = []
        success_data = []
        error_data = []
    else:
        df['time_started'] = df['time_started'].dt.date
        groups = df.groupby('time_started')
        cum_sum_series = groups.count()['project'].cumsum()
        data = convert_tup_list(list(zip(cum_sum_series.index.map(conversion), cum_sum_series)))

        success_df = df[df['status'] == 'Scraping Success']
        error_df = df[df['status'] != 'Scraping Success']


        if success_df.empty:
            success_data = []
        else:
            success_groups = success_df.groupby('time_started')
            success_cum_sum_series = success_groups.count()['project'].cumsum()
            success_data = convert_tup_list(list(zip(success_cum_sum_series.index.map(conversion), success_cum_sum_series)))

        
        if error_df.empty:
            error_data = []
        else:
            error_groups = error_df.groupby('time_started')
            error_cum_sum_series = error_groups.count()['project'].cumsum()
            error_data = convert_tup_list(list(zip(error_cum_sum_series.index.map(conversion), error_cum_sum_series)))
    
    total = {"label": "Total", "data": data, 'color': "#0088CC"}
    success = {"label": "Success", "data": success_data, 'color': "#0088CC"}
    failure = {"label": "Failure", "data": error_data, 'color': "#0088CC"}

    return [total, success, failure]

def conversion(x):
    return x.strftime('%m/%d/%Y')

def convert_tup_list(data):
    for index, val in enumerate(data):
        data[index] = list(val)

    return data