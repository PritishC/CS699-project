import json
import random
from datetime import datetime, timedelta, date, time
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from dashboard.models import ScrapyRequest
from accounts.forms import User
from django.db.models import Count


@login_required
def index(request):
    user = User.objects.get(pk=request.user.id)
    today = datetime.today()
    today = datetime.combine(today, time.min) 
    requests_info = list(ScrapyRequest.objects.filter(time_started__range=(today, today+timedelta(days=1))).values('project').annotate(dcount=Count('project')))
    requests_data = []
    for item in requests_info:
    	temp_dict = dict()
    	temp_dict['label'] = item.get('project')
    	temp_dict['value'] = item.get('dcount')
    	requests_data.append(temp_dict)
    context = {
        "user": user,
        "requests_data":requests_data
    }
    return render(request, 'index.html', context)


def twitter_home(request):
    registered_user = get_registered_user(["Twitter"])
    context = {"registered_user": registered_user, "Errors": get_errors(), "requests_info": get_requests()}
    print(context)
    return render(request, 'twitter_home.html', context)


def twitter_daily(request):
    keywords_status = get_keyword_status(["Corona", "Politics", "Football", "Donald Trump", "Japan", "Tourism"])
    context = {"Keywords_Status": keywords_status, "Errors": get_errors()}
    return render(request, 'twitter_daily.html', context)


def get_registered_user(websites):
    data = []
    for website in websites:
        data.append(get_user_data(website))
    return data


def get_user_data(website):
    colors = ["#0088cc", "#2baab1", "#734ba9", "#C0C0C0", "#808080", "#FF0000", "#000000", "#800000", "#FFFF00"]
    data = [[0, 0]]
    for i in range(10):
        data.append([i+1, data[i][1]+random.randint(a=0, b=20)])
    user_data = {"label": website, "data": data, "color": colors[random.randint(0, len(colors)-1)]}
    return user_data


def get_errors():
    errors = []
    error_des = {101: "Server Not responding", 102: "Api not Responding", 103: "Too few posts", 104: "Scraping Error", 105: "Unknown Error"}
    status = ["Solved", "Working", "Pending"]
    for i in range(5):
        error_code = random.randint(101, 105)
        error = {"id": i+1, "Code": error_code, "Description": error_des[error_code], "Status": status[random.randint(0,2)]}
        errors.append(error)
    return errors


def get_keyword_status(keywords):
    keywords_status = []
    status = ["Solved", "Working", "Pending"]
    for i in range(len(keywords)):
        keyword_status = {"id": i+1, "Keyword": keywords[i], "Users": status[random.randint(0, 2)],
                          "Posts": status[random.randint(0, 2)], "User_Data": status[random.randint(0, 2)],
                          "Posts_data": status[random.randint(0, 2)], "DB": status[random.randint(0, 2)],
                          "Verified": status[random.randint(0, 2)]}
        keywords_status.append(keyword_status)
    return keywords_status


def get_requests():
    success = get_user_data("Success")
    failure = get_user_data("Failure")
    total = get_user_data("Total")
    for i in range(len(total["data"])):
        total["data"][i][1] = success["data"][i][1]+failure["data"][i][1]
    return [total, success, failure]


# Create HTML
def generate_html(request):
    context = {}

    print("HTML GENERATED")
    directory     = request.path.split('/')[-2]
    filename      = request.path.split('/')[-1]
    load_template = "{}/{}".format(directory, filename)
    template      = loader.get_template(load_template)
    return HttpResponse(template.render(context, request))


def send_email_view(request):
    send_mail(subject="TEST", message="TEST EMAIL. DO NOT REPLY", recipient_list=["rahul.ag@sms-datatech.co.jp"],
              from_email="rahulag1996@gmail.com")
    return HttpResponse("HELLO")


def send_slack_msg_View(request):
    send_slack_msg(token=settings.SLACK_TOKEN, data='{"text":"TEST"}')
    return HttpResponse("HELLO")

def send_slack_msg(token, data):
    url = "https://hooks.slack.com/services/" + token
    res = requests.post(url, data=data)
    return res

