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

class RelatedObjectDoesNotExist(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# @login_required
# def register_event(request):
#     try:
#         if request.user.creator is None:
#             raise RelatedObjectDoesNotExist("오류!")
#         else:
#             ImageFormSet = modelformset_factory(EventImage, form=ImageForm, extra=3)
#
#             if request.method == 'POST':
#                 event_form = EventForm(request.POST)
#                 tags = request.POST['tag'].split(',')
#                 image_formset = ImageFormSet(request.POST, request.FILES, queryset=EventImage.objects.none())
#                 if event_form.is_valid() and image_formset.is_valid():
#                     event = event_form.save(commit=False)
#                     event.creator = Member.objects.get(id=request.user.pk).creator
#                     event.save()
#                     for tag in tags:
#                         print(tag)
#                         tag = tag.strip()
#                         Tag.objects.create(name=tag, event=event)
#
#                     for form in image_formset.cleaned_data:
#                         print(image_formset.cleaned_data)
#                         if form :
#                             image = form['image']
#                             photo = EventImage(event=event, image=image)
#                             print(2)
#                             photo.save()
#                 return redirect('login:login')
#             else:
#                 creator = request.user.creator
#                 form = EventForm()
#                 formset = ImageFormSet(queryset=EventImage.objects.none())
#                 cxt = {
#                     'form':form,
#                     'formset':formset,
#                     'creator':creator,
#                 }
#                 return render(request, 'event/event_register.html', cxt)
#     except RelatedObjectDoesNotExist:
#         return redirect('login:create_creator')


def creator_detail(request, pk):
    event = Event.objects.get(pk=pk)
    creator = event.creator
    # Creator.objects.get(id=1).event_set.get(pk=1)
    ctx = {
        # 'event':event,
        # 'creator':event.creator,
        # 'event_name' : event.event_name,
        # 'genre' : event.genre,
        # 'creator_photo' : creatordetail.creator_photo,
        # 'creator':creator,
        'event':event,
        'creator':creator
    }
    return render(request, 'event/creator_event_detail.html', ctx)


@login_required
def register_event(request):
    try:
        print('출력은 되는거니')
        # tmp = Member.objects.get(id=request.user.pk).creator

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
                event.start_date_time = request.POST['start_date_time']
                event.end_date_time = request.POST['end_date_time']
                event.creator = Member.objects.get(id=request.user.pk).creator
                event.location = location
                event.save()
                for tag in tags:
                    print(tag)
                    tag = tag.strip()
                    Tag.objects.create(name=tag, event=event)
                for form in image_formset.cleaned_data:
                    print(image_formset.cleaned_data)
                    if form :
                        image = form['image']
                        photo = EventImage(event=event, image=image)
                        print(2)
                        photo.save()
                return redirect('login:login')
        else:
            creator = request.user.creator
            location = LocationForm()
            form = EventForm()
            formset = ImageFormSet(queryset=EventImage.objects.none())
            cxt = {
                'form':form,
                'formset':formset,
                'location':location,
                'creator':creator,
            }
            return render(request, 'event/event_register.html', cxt)
    except Exception as e:
        print('예외 발생 ', e)
        return redirect("login:create_creator")

def creator_detail(request, pk):
    event = Event.objects.get(pk=pk)
    creator = event.creator
    comments = creator.comments.all()
    ctx = {
        'event':event,
        'creator':creator,
        'comments':comments,
    }
    return render(request, 'event/creator_event_detail.html', ctx)