from channels import Channel, Group
from channels.auth import channel_session_user, channel_session_user_from_http
from .models import Song, Conversation, Message


def msg_consumer(message):
    song_obj = Song.objects.get(pk=message.content['message'])
    conversation = Conversation.objects.get(pk=message.content['conversation'])
    if message.content['user'] == conversation.user2.username:
        receiver = conversation.user1
        sender = conversation.user2
    else:
        receiver = conversation.user2
        sender = conversation.user1

    msg_obj = Message(conversation=conversation,
                      sender=sender,
                      receiver=receiver,
                      message=song_obj.song.url)
    msg_obj.save()
    song_obj.song_impression += 1
    song_obj.save()
    conversation.send_message(song_obj.song.url, message.content['user'])


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})  # creating the connection on the channel
    Group("room").add(message.reply_channel)


@channel_session_user
def ws_message(message):
    Channel("chat-messages").send({
        "user": message.user.username,
        "conversation": message.content['path'].strip("/"),
        "message": message['text'],
    })


@channel_session_user
def ws_disconnect(message):
    Group("room").discard(message.reply_channel)


