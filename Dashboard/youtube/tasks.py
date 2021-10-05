# Create your tasks here
from __future__ import absolute_import, unicode_literals
import demjson
import json
import time
from datetime import datetime, timedelta
from uuid import uuid4
import datetime as dt

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from scrapyd_api import ScrapydAPI
from sqlite3 import IntegrityError

from dashboard.models import ScrapyRequest
from output.models import ScrapyItem
from youtube import limits
from youtube.models import Request, User, Media, RelatedVideos

scrapyd = ScrapydAPI("http://localhost:6800")


# TODO: Add Parsing Error
# TODO: Think of better way to implement spin
def spin(task_id, unique_id):
    while scrapyd.job_status('youtube', task_id) == "pending":
        time.sleep(1)
    time_started = datetime.now()
    while scrapyd.job_status('youtube', task_id) != "finished":
        if (datetime.now()-time_started) > timedelta(seconds=100):
            return 0
        time.sleep(1)
    if ScrapyItem.objects.filter(unique_id=unique_id).count() == 0:
        scrapyd.cancel('youtube', task_id)
        return -1
    else:
        return 1


def get_uuid():
    return str(uuid4())


def get_output_from_task(unique_id):
    try:
        output = ScrapyItem.objects.get(unique_id=unique_id)
        return json.loads(output.data.encode("utf-8"))
    except ObjectDoesNotExist:
        return None

def get_error_from_task(unique_id):
    try:
        output = ScrapyItem.objects.get(unique_id=unique_id)
        error = json.loads(output.error.encode("utf-8"))
        error_code = error['code']
        if error_code is None:
            error_code = "UE"
        error_message = error['_type']
        return error_code, error_message
    except ObjectDoesNotExist:
        return "UE", "UE"


@shared_task(name="youtube_initial")
def youtube_initial(request_id):
    request = Request.objects.get(id=request_id)
    if request.time_start_scraping is not None:
        return
    condition = request.condition
    request.time_start_scraping = datetime.now()
    request.save()
    try:
        video_from_keyword(request, condition)
    except Exception as e:
        request.update_status("Request Failed with Exception %s" % e)
        return 0
    request.update_status("Request Complete")
    request.time_end_scraping = datetime.now()
    #request.save()
    #result = check_data_initial(request)
    #print(result)
    #request.update_status("Check Data Complete. %s" % result)
    request.time_end = datetime.now()
    request.save()


def video_from_keyword(request, condition):
    # Step1
    request.update_status("Scraping Videos to find Users using given Condition.")
    keyword = condition.search_text
    users = []
    continuation = None
    itct = None
    old = None
    while (len(users)) < limits.DAILY_USER_COUNT:
        old = continuation
        for trial in range(limits.MAX_TRIES):
            unique_id = get_uuid()
            task_id = scrapyd.schedule(project="youtube", spider="search", unique_id=unique_id, keyword=keyword,
                                       order='date', type='video', date='week', continuation=continuation,
                                       itct=itct)
            s = ScrapyRequest(task_id=task_id, unique_id=unique_id, project="youtube", spider="search",
                              parameters={"keyword": keyword, "order": 'date', 'type': 'video', 'date': 'week',
                                          'continuation': continuation, 'itct': itct})
            s.save()
            scraping_result = spin(task_id, unique_id)
            if scraping_result == 1:
                s.update_status("Scraping Success")
                new_users, continuation, itct, error_code, error_message, status = find_users_from_keyword(unique_id, condition, users)
                if status:
                    users = users + new_users
                    break
                else:
                    request.add_error("Error in Scraping Videos from Keyword. Try %d Message: %s"%(trial, error_message),error_code, 4)
                    s.update_status("Scraping Complete with Error")
            elif scraping_result == -1:
                s.update_status("Scraping Error")
                request.add_error("Error in Scraping Videos from Keyword. Try %d" % trial)
            else:
                s.update_status("Timeout Error")
        if continuation is None:
            break
        if continuation == old:
            break

    if len(users) == 0:
        request.add_error("Couldn't get any New User.")
        return
    #elif len(users) < limits.DAILY_USER_COUNT:
    #    request.add_error("Couldn't get required number of New Users")

    user_info(users, request)
    user_videos(users, request)


def find_users_from_keyword(unique_id, condition, users):
    # Initialise Variables
    new_users = []
    continuation = None
    itct = None

    # Load Data
    output = get_output_from_task(unique_id)

    if output is None:
        error_message, code = get_error_from_task(unique_id)
        return new_users, continuation, itct, code, error_message, False

    if output['videos'] is not None:
        for video in output['videos']:
            if (len(users)+len(new_users)) >= limits.DAILY_USER_COUNT:
                break
            if video is not None and video['owner'] is not None:
                try:
                    if (video['owner']['identifier'] not in new_users) and (video['owner']['identifier'] not in users) and update_user(video['owner'], condition):
                        new_users.append(video['owner']['identifier'])
                except Exception as e:
                    print("Error updating user info in find_users_from_keyword %s" % video['owner']['identifier'], e)

    if output['pagination'] is not None:
        continuation = output['pagination']['continuation']
        itct = output['pagination']['itct']
    return new_users, continuation, itct, None, None, True


def user_info(users, request):
    # Step 2
    total_users = len(users)
    for i, user in enumerate(users):
        for trial in range(limits.MAX_TRIES):
            request.update_status("Scraping User Info. %d out of %d" % (i+1, total_users))
            unique_id = get_uuid()
            task_id = scrapyd.schedule(project="youtube", spider="channel", channelId=user, unique_id=unique_id)
            s = ScrapyRequest(task_id=task_id, unique_id=unique_id, project="youtube", spider="channel",
                              parameters={"channelId": user})
            s.save()
            scraping_result = spin(task_id, unique_id)
            if scraping_result==1:
                s.update_status("Scraping Success")
                error_code, error_message,status = parse_user_info(unique_id)
                if status:
                    break
                else:
                    s.update_status("Scraping Complete with Error")
                    request.add_error("Scraping User Info Failed for User: %s Try %d Message: %s" % (user, trial, error_message), error_code, 4)
            elif scraping_result==-1:
                s.update_status("Scraping Error")
                request.add_error("Scraping User Info Failed for User: %s Try %d" % (user, trial))
            else:
                s.update_status("Timeout Error")


def parse_user_info(unique_id):
    output = get_output_from_task(unique_id)
    if output is None:
        error_code, error_message = get_error_from_task(unique_id)
        return error_code, error_message, False
    try:
        update_user(output, full_info=True)
    except Exception as e:
        print("Exception is parsing user info %s in parse_user_info" % output['identifier'], e)
    return None, None, True


def user_videos(users, request):
    # Step 3
    all_posts = []
    total_users = len(users)
    for i, user in enumerate(users):
        request.update_status("Scraping User Videos. %d out of %d" % (i+1, total_users))
        posts = []
        continuation = None
        itct = None
        while len(posts) < limits.DAILY_POST_COUNT:
            for trial in range(limits.MAX_TRIES):
                unique_id = get_uuid()
                task_id = scrapyd.schedule(project="youtube", spider="channel_videos", channelId=user, unique_id=unique_id,
                                           continuation=continuation, itct=itct)
                s = ScrapyRequest(task_id=task_id, unique_id=unique_id, project="youtube", spider="channel_videos",
                                  parameters={"channelId": user, "continuation": continuation, "itct": itct})
                s.save()
                scraping_result = spin(task_id, unique_id)
                if scraping_result==1:
                    s.update_status("Scraping Success")
                    new_posts, continuation, itct, error_code, error_message, status = parse_user_videos(unique_id, user, posts)
                    if status:
                        posts = posts + new_posts
                        break
                    else:
                        s.update_status("Scraping Complete with Error")
                        request.add_error("Error in Scraping User Videos for User: %s Try %d Message: %s" % (user, trial, error_message), error_code, 4)
                elif scraping_result==-1:
                    s.update_status("Scraping Error")
                    request.add_error("Error in Scraping User Videos for User: %s Try %d" % (user, trial))
                    if trial == 2:
                        continuation = None
                else:
                    s.update_status("Timeout Error")
            if continuation is None or itct is None:
                break

        if len(posts) == 0:
            request.add_error("Couldn't get any Post for User: %s" % user)

        all_posts = all_posts + posts
    return all_posts


def parse_user_videos(unique_id, user=None, posts=[]):
    new_flag = True
    videos = []
    output = get_output_from_task(unique_id)
    continuation = None
    itct = None
    if output is None:
        error_code, error_message = get_error_from_task(unique_id)
        return videos, continuation, itct, error_code, error_message, False

    if output['media_list'] is not None:
        for video in output['media_list']:
            if (len(posts) + len(videos)) >= limits.DAILY_POST_COUNT:
                break
            if video is not None:
                try:
                    new_flag = update_post(video, user) and new_flag
                except Exception as e:
                    print("Exception in updating post %s %s in parse_user_videos" % (video['identifier'], user), e)
                videos.append(video['identifier'])
    if output['pagination'] is not None:
        continuation = output['pagination']['continuation']
        itct = output['pagination']['itct']
    return videos, continuation, itct, None, None, True


def post_info(posts, request):
    # Step 4
    total_posts = len(posts)
    for i, post in enumerate(posts):
        for trial in range(limits.MAX_TRIES):
            request.update_status("Scraping Videos Info. %d out of %d" % (i+1, total_posts))
            unique_id = get_uuid()
            task_id = scrapyd.schedule(project="youtube", spider="video", videoId=post, unique_id=unique_id)
            s = ScrapyRequest(task_id=task_id, unique_id=unique_id, project="youtube", spider="video",
                              parameters={"videoId": post})
            s.save()
            scraping_result = spin(task_id, unique_id)
            if scraping_result==1:
                s.update_status("Scraping Success")
                error_code, error_message, status = parse_video_info(unique_id)
                if status:
                    break
                else:
                    s.update_status("Scraping Complete with Error")
                    request.add_error("Scraping Video Info Failed for Video: %s Try %d Message: %s" % (post, trial, error_message), error_code, 4)
            elif scraping_result==-1:
                s.update_status("Scraping Error")
                request.add_error("Scraping Video Info Failed for Video: %s Try %d" % (post, trial))
            else:
                s.update_status("Timeout Error")


def parse_video_info(unique_id):
    output = get_output_from_task(unique_id)
    if output is None:
        error_code, error_message = get_error_from_task(unique_id)
        return error_code, error_message, False
    try:
        update_post(output, full_info=True)
    except Exception as e:
        print("Exception in updating post %s in parse_video_info" % output['identifier'], e)
    return None, None, True


@shared_task(name="youtube_daily")
def youtube_daily(request_id):
    #users = [x[0] for x in list(User.objects.filter(is_registered=True, registered_on__range=(datetime.now() - dt.timedelta(days=5), datetime.now())).values_list("channel_id"))]

    request = Request.objects.get(id=request_id)
    if request.time_start_scraping is not None:
        return
    request.time_start_scraping = datetime.now()
    request.save()
    users = [x[0] for x in list(User.objects.filter(is_registered=True).values_list("channel_id"))]
    try:
        i=0
        while(True):
            users_part = users[100*i:100*(i+1)]
            if len(users_part)==0:
                break
            r = Request(is_scheduled=1)
            r.save()
            daily_subtask.delay(users_part, r.id)
            i+=1
    except Exception as e:
        request.update_status("Request Failed with Exception %s" %e)
        return

    request.update_status("Request Complete")
    request.time_end_scraping = datetime.now()
    request.save()
    #result = check_data_daily(request)
    #print(result)
    #request.update_status("Check Data Complete %s" % result)
    #request.time_end = datetime.now()
    #request.save()


# DB
def update_user(output, condition=None, full_info=False):
    channel_id = output['identifier']
    new_flag = False
    try:
        u = User.objects.get(channel_id=channel_id)
    except ObjectDoesNotExist:
        u = User(channel_id=channel_id)

    u.user_url = "https://www.youtube.com/channel/"+channel_id
    if u.full_info == 0 and u.condition is None:
        new_flag = True
    if condition is not None and u.condition is None:
        u.condition = condition
    if output['title'] is not None:
        u.title = output['title']
    if output['description'] is not None:
        u.description = output['description']
    if output['statistics'] is not None:
        if output['statistics']['subscribers'] is not None:
            if type(output['statistics']['subscribers']) is not str:
                u.subscriber_count = output['statistics']['subscribers']
        if output['statistics']['views'] is not None:
            if type(output['statistics']['views']) is not str:
                u.view_count = output['statistics']['views']
    if output['profile_thumbnail'] is not None:
        u.thumbnail_url = output['profile_thumbnail']
    if output['banner_thumbnail'] is not None:
        u.banner_url = output['banner_thumbnail']

    if output['links'] is not None:
        try:
            u.links = json.dumps(output['links'])
        except:
            u.links = output['links']
    if output['created_date'] is not None:
        if type(output['created_date']) is not str:
            try:
                u.published_at = datetime.fromtimestamp(output['created_date'])
            except:
                pass
    u.last_updated = datetime.today()
    u.full_info = u.full_info or full_info
    u.save()
    return new_flag


def update_post(output, owner=None, full_info=False):
    video_id = output['identifier']
    new_flag = True
    try:
        m = Media.objects.get(video_id=video_id)
    except ObjectDoesNotExist:
        new_flag = False
        if output['owner'] is not None:
            owner_channel_id = output['owner']['identifier']
            try:
                u = User.objects.get(channel_id=owner_channel_id)
            except ObjectDoesNotExist:
                u = User(channel_id=owner_channel_id)
            try:
                update_user(output['owner'])
            except Exception as e:
                print("Error updating user info %s in update_post", output['owner']['identifier'], e)
        else:
            u = User.objects.get(channel_id=owner)
        m = Media(video_id=video_id, channel_id=u.channel_id)
        m.save()
    m.content_url = "https://www.youtube.com/watch?v="+video_id
    if output['title'] is not None:
        m.title = output['title']
    if output['description'] is not None:
        m.description = output['description']
    if output['upload_date'] is not None:
        if type(output['upload_date']) is not str:
            try:
                m.published_at = datetime.fromtimestamp(output['upload_date'])
            except:
                pass
    if output['statistics'] is not None:
        if output['statistics']['views'] is not None:
            if type(output['statistics']['views']) is not str:
                m.view_count = output['statistics']['views']
        if output['statistics']['likes'] is not None:
            if type(output['statistics']['likes']) is not str:
                m.likes = output['statistics']['likes']
        if output['statistics']['dislikes'] is not None:
            if type(output['statistics']['dislikes']) is not str:
                m.dislikes = output['statistics']['dislikes']
    if output['genre'] is not None:
        m.tags = output['genre']
    if output['thumbnail_url'] is not None:
        m.thumbnail_url = output['thumbnail_url']
    if output['related_videos'] is not None:
        for related_video in output['related_videos']:
            try:
                update_post(related_video)
                r = RelatedVideos(from_media_id=video_id, to_media_id=related_video['identifier'])
                r.save()
            except IntegrityError:
                pass
    m.full_info = m.full_info or full_info
    m.last_updated = datetime.today()
    m.save()
    return new_flag


# Check Data
def check_data_initial(request):
    errors = []
    condition_id = request.condition_id

    users = User.objects.filter(condition_id=condition_id, full_info=True)
    if len(users) < limits.DAILY_USER_COUNT:
        errors.append("Daily User count not satisfied.")

    for user in users:
        user_errors = check_user_data(user)
        user_video_errors = check_user_videos_initial(user)
        if user_errors is not None:
            errors.append({"user": user, "info_errors": user_errors})
        if user_video_errors is not None:
            errors.append({"user": user, "video_errors": user_video_errors})
    if len(errors) == 0:
        return None
    return errors


def check_data_daily(request):
    date = datetime.date(request.time_start_scraping)
    users = User.objects.filter(is_registered=True, registered_on__range=(datetime.now() - dt.timedelta(days=5), datetime.now()))
    errors = []

    for user in users:
        user_errors = check_user_data(user, date)
        user_video_errors = check_user_videos_daily(user, date)
        if user_errors is not None:
            errors.append({"user": user, "info_errors": user_errors})
        if user_video_errors is not None:
            errors.append({"user": user, "video_errors": user_video_errors})

    return errors


def check_user_basic(user):
    errors = []
    if user.title is None:
        errors.append("Title is Missing")
    if len(errors) == 0:
        return None
    return errors


def check_user_data(user, update_date=None):
    errors = []
    if user.title is None:
        errors.append("Title is Missing")
    if user.description is None:
        errors.append("Description is Null or Missing")
    if user.subscriber_count is None:
        errors.append("Subscriber Count is Missing")
    elif not (isinstance(user.subscriber_count, float) or isinstance(user.subscriber_count, int)):
        errors.append("Subscriber Count is not numeric")
    if user.view_count is None:
        errors.append("View Count is Missing")
    elif not (isinstance(user.view_count, float) or isinstance(user.view_count, int)):
        errors.append("View Count is not numeric")
    if user.thumbnail_url is None:
        errors.append("Thumbnail_url is Null or Missing")
    if user.published_at is None:
        errors.append("Published Data is missing")
    elif not isinstance(user.published_at, dt.date):
        errors.append("Published date is not datelike")
    if len(errors) == 0:
        return None
    return errors


def check_user_videos_initial(user):
    errors = []
    videos = Media.objects.filter(channel_id=user.channel_id)

    if len(videos) < limits.DAILY_POST_COUNT:
        errors.append("Not enough videos scraped for User:%s" % user.channel_id)

    for video in videos:
        video_errors = check_video_basic(video, user.channel_id)
        if video_errors is not None:
            errors.append({"video": video, "video_info_errors": video_errors})
    if len(errors) == 0:
        return None
    return errors


def check_user_videos_daily(user, update_date=None):
    errors = []
    videos = Media.objects.filter(channel_id=user.channel_id, full_info=True)

    if len(videos) < limits.DAILY_POST_COUNT:
        errors.append("Not enough videos scraped for User:%s" % user.channel_id)

    for video in videos:
        video_errors = check_video_info(video, user.channel_id, update_date)
        if video_errors is not None:
            errors.append({"video": video, "video_info_errors": video_errors})
    if len(errors) == 0:
        return None
    return errors


def check_video_basic(video, user_id=None):
    errors = []
    if user_id is not None:
        if video.channel_id != user_id:
            errors.append("Owner information Incorrect")
    else:
        if video.channel_id is None:
            errors.append("Owner information Missing")
    if video.thumbnail_url is None:
        errors.append("Content Thumbnail is missing")
    if video.title is None:
        errors.append("Title is missing")
    if len(errors) == 0:
        return None
    return errors


def check_video_info(video, user_id=None, update_date=None):
    errors = []
    if user_id is not None:
        if video.channel_id != user_id:
            errors.append("Owner information Incorrect")
    else:
        if video.channel_id is None:
            errors.append("Owner information Missing")
    if video.title is None:
        errors.append("Title is missing")

    if video.thumbnail_url is None:
        errors.append("Video Thumbnail is missing")

    if video.published_at is None:
        errors.append("Date of Upload is missing")
    elif not isinstance(video.published_at, dt.date):
        errors.append("Date of Upload is not datelike")

    if video.view_count is None:
        errors.append("View_count is Missing")
    elif not (isinstance(video.view_count, float) or isinstance(video.view_count, int)):
        errors.append("View_count is not numeric")

    if video.likes is None:
        errors.append("likes is Missing")
    elif not (isinstance(video.likes, float) or isinstance(video.likes, int)):
        errors.append("likes is not numeric")

    if video.dislikes is None:
        errors.append("dislikes is Missing")
    elif not (isinstance(video.dislikes, float) or isinstance(video.dislikes, int)):
        errors.append("dislikes is not numeric")

    error = check_related_videos(video)
    if error is not None:
        errors.append({"Related_Video_Errors": error})
    if len(errors) == 0:
        return None
    return errors


def check_related_videos(video):
    related_videos = video.related_videos.all()
    errors = []
    for related_video in related_videos:
        error = check_video_basic(related_video)
        if error is not None:
            errors.append({"Video": related_video, "Video_info_error": error})

    if len(errors) == 0:
        return None
    return errors

@shared_task(name="youtube_daily_subtask")
def daily_subtask(users, request_id):
    request = Request.objects.get(id=request_id)
    if request.time_start_scraping is not None:
        return
    request.time_start_scraping = datetime.now()
    request.save()
    try:
        user_info(users, request)
        posts = user_videos(users, request)
        post_info(posts, request)
    except Exception as e:
        request.update_status("Sub-Request Request Failed with Exception %s" %e)
        return

    request.update_status("Sub-Request Request Complete")
    request.time_end_scraping = datetime.now()
    request.save()
