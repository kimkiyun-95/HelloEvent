from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.template import RequestContext

from event.forms import ImageForm, EventForm
from event.models import EventImage, Event, Tag
from location.forms import LocationForm
from django.conf import settings

from login.models import Creator, Member
from comment.models import Comment

from django.db.models import Q
from datetime import datetime

class RelatedObjectDoesNotExist(Exception):
    def __init__(self):
        self.msg = '크리에이터 존재 오류'

    def __str__(self):
        return self.msg


def register_event(request):
    try:
        if not request.user.is_authenticated:
            return redirect("login:create_creator")
        print('출력은 되는거니')
        print(Member.objects.get(id=request.user.pk).creator)
        if Member.objects.get(id=request.user.pk).creator is None:
            raise RelatedObjectDoesNotExist

        ImageFormSet = modelformset_factory(EventImage, form=ImageForm, extra=3)

        if request.method == 'POST':
            print("post 시작")
            event_form = EventForm(request.POST)
            tags = request.POST['tag'].split(',')
            image_formset = ImageFormSet(request.POST, request.FILES, queryset=EventImage.objects.none())
            location_form = LocationForm(request.POST)
            if event_form.is_valid() and image_formset.is_valid() and location_form.is_valid() :
                event = event_form.save(commit=False)
                location = location_form.save(commit=False)
                location.save()
                event.start_date_time = str(request.POST['start_date_time'])
                event.end_date_time = str(request.POST['end_date_time'])
                print(event.end_date_time)
                event.creator = Member.objects.get(id=request.user.pk).creator
                event.location = location
                event.save()
                print("세이브가 되었을까?????")
                for tag in tags:
                    print(tag)
                    if tag == "":
                        continue
                    tag = tag.strip()
                    _tag, _ = Tag.objects.get_or_create(name=tag)
                    event.tags.add(_tag)
                for form in image_formset.cleaned_data:
                    print(image_formset.cleaned_data)
                    if form :
                        image = form['image']
                        photo = EventImage(event=event, image=image)
                        print(2)
                        photo.save()
                return redirect('event:creator_detail', event.pk)

        else:
            print(100)
            creator = request.user.creator
            location = LocationForm()
            form = EventForm()
            formset = ImageFormSet(queryset=EventImage.objects.none())
            prefer_city = Member.objects.get(id=request.user.pk).city
            prefer_gu = Member.objects.get(id=request.user.pk).gu
            cxt = {
                'form':form,
                'formset':formset,
                'location':location,
                'creator':creator,
                'prefer_city' : prefer_city,
                'prefer_gu' : prefer_gu,
            }
            return render(request, 'event/event_register.html', cxt)
    except Exception as e:
        print('예외 발생 ', e)
        return redirect("login:create_creator")

def creator_detail(request, pk):
    event = Event.objects.get(pk=pk)
    creator = event.creator
    events = creator.events.all()
    comments = creator.comments.all()
    comment_num = comments.count()
    images = event.eventimage_set.all()
    image_num = event.eventimage_set.count()
    comment_3 = creator.comments.order_by('-created_at')[:3]
    tags = event.tags.all()
    ctx = {
        'event':event,
        'events':events,
        'creator':creator,
        'comments':comments,
        'comment_3':comment_3,
        'comment_num':comment_num,
        'images':images,
        'image_num':image_num,
        'tags':tags,
        'user':request.user,
    }
    return render(request, 'event/creator_event_detail.html', ctx)

def search_result(request):
    # startdate = datetime.today()
    # endtime = startdate + datetime.timedelta()
    if 'search_data' in request.GET:
        data = request.GET['search_data']
        tags = Tag.objects.filter(Q(name__exact=data))
        print(tags)
        today = datetime.today()
        print(today)
        results = Event.objects.none()
        for tag in tags:
            print(tag)
            print(tag.event_set.all())
            q = tag.event_set.all().filter(end_date_time__gte=today)
            q = q.order_by('start_date_time')
            print(q)
            results = results | q
            print(results)
        print(results)
    ctx = {
        'data':data,
        'results':results,
    }
    return render(request, "event/search_result.html", ctx)


def search_result_click(request, tag):
    data = tag
    tags = Tag.objects.filter(Q(name__exact=data))
    print(tags)
    today = datetime.today()
    print(today)
    results = Event.objects.none()
    for tag in tags:
        print(tag)
        print(tag.event_set.all())
        q = tag.event_set.all().filter(end_date_time__gte=today)
        print(q)
        q = q.order_by('start_date_time')
        print(q)
        results = results | q
        print(results)
    print(results)
    ctx = {
        'data' : data,
        'results' : results,
    }
    return render(request, "event/search_result.html", ctx)

def today_event(request):
    today_date = datetime.today().date()
    print(today_date)
    today_date_time = datetime.today()

    # number = today_date_time.weekday()

    day_name = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    today_name = day_name[today_date_time.weekday()]
    
    not_yet = Event.objects.all().filter(Q(start_date_time__date__exact = today_date) & Q(start_date_time__gt=today_date_time))
    ing = Event.objects.all().filter(Q(end_date_time__gte=today_date_time) & Q(start_date_time__lte=today_date_time)) 
    # gte: 이상, lte: 이하 gt: 초과 lt: 미만
    end = Event.objects.all().filter(Q(end_date_time__date__exact = today_date) & Q(end_date_time__lt=today_date_time))

    ctx = {
        'today_date' : today_date,
        'today_date_time' : today_date_time,
        'not_yet_events' : not_yet,
        'end_events': end,
        'ing_events' : ing,
        'today_name': today_name
    }

    return render(request, "event/today_event.html", ctx)


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    creator_pk = event.creator.pk
    event.delete()
    return redirect("login:creator_mypage", creator_pk)
