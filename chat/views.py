from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import redirect, render
from .models import Message, Conversation
from haystack.query import SearchQuerySet
from django.contrib.auth.models import User
from .forms import NetworkForm


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            confirm_password = form.cleaned_data.get('password2')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/chat')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def index(request):
    user_list = User.objects.exclude(username=request.user)
    form = NetworkForm()
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            print form.data
            return redirect(request.META['HTTP_REFERER'])

    return render(request, 'chat/index.html', {
        'user_list': user_list,
        'form': form,
    })


@login_required
def fetch_conversation(request, user_id):
    user_list = User.objects.exclude(username=request.user)
    user_obj = User.objects.get(pk=user_id)
    try:
        conversation = Conversation.objects.get(
            (Q(user1=request.user) & Q(user2=user_obj)) | (Q(user1=user_obj) & Q(user2=request.user)))
    except Conversation.DoesNotExist:
        conversation = Conversation(user1=request.user, user2=user_obj)
        conversation.save()

    latest_msg_list = Message.objects.filter(conversation=conversation).order_by('created_at')
    conv_obj = Conversation.objects.get(pk=conversation.id)
    if request.user == conv_obj.user2:
        receiver = conv_obj.user1
    else:
        receiver = conv_obj.user2
    context = {
        'user_list': user_list,
        'conversation_id': conversation.id,
        'latest_msg_list': latest_msg_list,
        'receiver': receiver,
    }
    return render(request, 'chat/messages.html', context)


@login_required
def search_song(request):
    while len(request.POST.get('message')) > 2:
        if request.POST.get('category') == unicode('All', 'utf-8'):
            songs = SearchQuerySet().autocomplete(text=request.POST.get('message', ''))
        else:
            songs = SearchQuerySet().autocomplete(text=request.POST.get('message', ''))\
            .filter(category=request.POST.get('category'))
        context = {
            'songs': songs,
        }
        return render(request, 'search/search.html', context)
    return render(request, 'search/search.html', {'songs': None})





