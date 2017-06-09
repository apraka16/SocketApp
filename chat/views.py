from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404
from django.db.models import Q
from django.shortcuts import redirect, render
from .models import Message, Conversation
from haystack.query import SearchQuerySet
from django.contrib.auth.models import User
from .forms import NetworkForm
import datetime


def signup(request):
    """ Ususal sign-up form """
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


def non_network_user_list(request):
    """ Finding users who are not yet connected to the request.user so as to add
    them in the 'Add User' drop-down form in homepage. This would go to forms.py
    to add in the form. """

    # fetch conversation where user is included
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user))

    network_users = []

    # fetch users other than the request.user from those conversations
    for conversation in conversations:
        if conversation.user1 == request.user:
            network_users.append(conversation.user2)
        else:
            network_users.append(conversation.user1)

    # get user ids for those users and add request.user so that he is removed on exclude
    network_users_id = [user.id for user in network_users]
    network_users_id.append(request.user.id)

    # create final list of non-network users to show in dropdown (add user)
    user_list = User.objects.exclude(id__in=network_users_id)
    user_list = [user.id for user in user_list]

    return user_list


@login_required
def index(request):
    """ For index.html display
    1. Find users who are connected to the request.user so as to add them in the 'My Network' display in homepage.
    2. Find users who are connected to the request.user so as to add them in the 'Add User' drop-down in homepage.
    RETURN: Return data

    """
    # 1
    # fetch conversation where user is included
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user))

    network_users = []

    # fetch users other than the request.user from those conversations
    for conversation in conversations:
        if conversation.user1 == request.user:
            network_users.append(conversation.user2)
        else:
            network_users.append(conversation.user1)

    # get user ids for those users and add request.user so that he is removed on exclude
    network_users_id = [user.id for user in network_users]

    # create final list of network users to display
    user_list = User.objects.filter(id__in=network_users_id)

    """ Creating drop-down form """

    # @TODO: error catching while form usage

    # 2
    form = NetworkForm(non_network_user_list(request))  # sending user ids for form drop-down

    if request.method == 'POST':
        form = NetworkForm(non_network_user_list(request), data=request.POST)
        if form.is_valid():
            # print int(form.data['user_id'])
            user_obj = User.objects.get(pk=form.data['user_id'])
            print user_obj
            try:  # Try probably be used > Try is actually used when user's page is not refreshed.
                # Results in error help-text
                conversation = Conversation.objects.get(
                    (Q(user1=request.user) & Q(user2=user_obj)) | (Q(user1=user_obj) & Q(user2=request.user)))
            except Conversation.DoesNotExist:
                conversation = Conversation(user1=request.user, user2=user_obj)
                conversation.save()

    # @TODO: possible hacks here needs to be figured out (url requests, etc.)

            return redirect(request.META['HTTP_REFERER'])

    # RETURN
    return render(request, 'chat/index.html', {
        'user_list': user_list,
        'form': form,
    })


@login_required
def fetch_conversation(request, user_id):

    """ For messages.html display
    1. Generate list of connected users to be displayed in left container
    2. Obtain conversation id to hyperlink users so that request.user may access conversation he's added into
        (left container)
    3. Render messages in selected conversation (right container)
    4. Fetch message receiver to be used by socket connection in routing messages (sockets)
    RETURN. Return data

    """
    # 1
    # Fetch conversation where user is included
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user))
    network_users = []
    # Fetch users other than the request.user from those conversations
    for conversation in conversations:
        if conversation.user1 == request.user:
            network_users.append(conversation.user2)
        else:
            network_users.append(conversation.user1)

    # Get user ids for those users and add request.user so that he is removed on exclude
    network_users_id = [user.id for user in network_users]

    # Create final list of network users to display
    user_list = User.objects.filter(id__in=network_users_id)

    # 2
    user_obj = User.objects.get(pk=user_id)
    try:
        conversation = Conversation.objects.get(
            (Q(user1=request.user) & Q(user2=user_obj)) | (Q(user1=user_obj) & Q(user2=request.user)))
    except Conversation.DoesNotExist:  # This logic should never be used since only networked users are shown in left >
        # The logic is being used sadly when user brute-force it through url
            raise Http404("User needs to be added first mate!")

    # 3
    count_msg = Message.objects.filter(conversation=conversation).count()
    if count_msg > 5:
        print datetime.datetime.now()
        latest_msg_list = Message.objects.filter(conversation=conversation).order_by('created_at')[count_msg-5:]
        print datetime.datetime.now()
    else:
        print datetime.datetime.now()
        latest_msg_list = Message.objects.filter(conversation=conversation).order_by('created_at')
        print datetime.datetime.now()

    # 4
    conv_obj = Conversation.objects.get(pk=conversation.id)
    if request.user == conv_obj.user2:
        receiver = conv_obj.user1
    else:
        receiver = conv_obj.user2

    # RETURN
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





