from django.http import HttpResponse,JsonResponse
from django.core import serializers
from django.shortcuts import render,redirect
from login.models import Member,Creator 
from event.models import Event,EventImage
from location.models import Event_Location
from django.views.decorators.csrf import csrf_exempt
import json
def show_map(request):
    prefer_city = Member.objects.get(id=request.user.pk).city
    prefer_gu = Member.objects.get(id=request.user.pk).gu
    ctx = {
        'prefer_city' : prefer_city,
        'prefer_gu' : prefer_gu,
    }
    return render(request,'location/map_list.html',ctx)

def search_map(request):
    if request.method == "POST":
        selected_city = request.POST.get('selected_city') 
        selected_gu = request.POST.get('selected_gu') 
        if selected_city == '시' or selected_gu == '구':
            return redirect('login:main')
        events = Event.objects.all()
        ctx = {
            'selected_city' : selected_city,
            'selected_gu' : selected_gu,
            'events' : events,
        }
    
    return render(request,'location/search_map.html',ctx)

@csrf_exempt
def ajax_search_genre(request):
    genre = request.POST.get('genre',None)
    events = Event.objects.filter(genre=genre)
    locations = Event_Location.objects.all()
    creators = Creator.objects.all()
    eventimages = EventImage.objects.all()

    event = serializers.serialize('json', events)
    location = serializers.serialize('json',locations)
    creator = serializers.serialize('json',creators)
    eventimage = serializers.serialize('json',eventimages)
    
    response_data = {}
    response_data['event'] = event
    response_data['eventimage'] = eventimage
    response_data['location'] = location
    response_data['creator'] = creator

    print('eventimage 모델 : ',eventimage)
    print('event 모델 : ',event)
    print('evreator 모델 : ',creator)
    return JsonResponse(response_data)
        
