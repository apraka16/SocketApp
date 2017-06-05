from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from haystack.query import SearchQuerySet
from rest_framework.permissions import (
    AllowAny, IsAdminUser, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from django.db.models import Q
from django.contrib.auth.models import User
from chat.models import Conversation, Message, Song
from .serializers import (ConversationSerializer,
                          ConversationCreateSerializer,
                          MessageCreateSerializer,
                          MessageSerializer,
                          SongSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          UserLoginSerializer,
                          )
from rest_framework.validators import ValidationError


# creates restful API conversation list - users see only related conversation
class ConversationListAPIView(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    # overwriting default queryset by method so that logged in use would only see his conversations
    def get_queryset(self):
        queryset = Conversation.objects.filter(Q(user1=self.request.user) |
                                               Q(user2=self.request.user)).order_by(
            '-started_at')
        return queryset


# creates restful API conversation detail for each ID - users can only query related conversation
class ConversationDetailAPIView(RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(Q(user1=self.request.user) |
                                               Q(user2=self.request.user)).order_by('-started_at')
        return queryset


class ConversationCreateAPIView(CreateAPIView):
    serializer_class = ConversationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(Q(user1=self.request.user) |
                                               Q(user2=self.request.user)).order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        other_user = User.objects.get(pk=self.request.data["user2"])
        if self.request.user == other_user:
            raise ValidationError("Both parties cannot be the same")
        else:
            try:
                Conversation.objects.get(
                    (Q(user1=self.request.user) & Q(user2=other_user)) |
                    (Q(user1=other_user) & Q(user2=self.request.user)))
                raise ValidationError("Conversation already exists")
            except Conversation.DoesNotExist:
                serializer.save(user1=self.request.user,
                                )
                return Response(serializer.data, status=HTTP_200_OK)


# creates restful API for deleting particular conversation using ID - users can only delete related conversation
class ConversationDeleteAPIView(DestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user)).order_by(
            '-created_at')
        return queryset


# for creating messages constrained by the conversation a user is in, hence
# the receiver, conversation and sender is static, only messages can change
class MessageCreateAPIView(CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.filter(Q(sender=self.request.user) |
                                          Q(receiver=self.request.user)).order_by('-created_at')

        queryset_next = queryset.filter(Q(conversation=self.request.parser_context['kwargs']['conversation_id']))
        return queryset_next

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(pk=self.request.parser_context['kwargs']['conversation_id'])
        if self.request.user == conversation.user1:
            receiver = conversation.user2
        else:
            receiver = conversation.user1
        serializer.save(sender=self.request.user,
                        conversation=conversation,
                        receiver=receiver)


# creates restful API messages list - users see messages sent/ received to/ from them
# user can only see all messages underlying conversation he's put in the url for
# url access is /conversation/12/messages/
class MessageListAPIView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.filter(Q(sender=self.request.user) |
                                          Q(receiver=self.request.user)).order_by('-created_at')

        queryset_next = queryset.filter(Q(conversation=self.request.parser_context['kwargs']['conversation_id']))
        return queryset_next


# creates restful API messages detail for each ID - users can only query related (sent/ receipt) messages
# user can only see selected message underlying particular conversation
# url access is /conversation/12/messages/232/
class MessageDetailAPIView(RetrieveAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.filter(Q(sender=self.request.user) |
                                          Q(receiver=self.request.user)).order_by('-created_at')

        queryset_next = queryset.filter(Q(conversation=self.request.parser_context['kwargs']['conversation_id']))
        return queryset_next


# creates restful API for deleting particular message using ID - users can only delete related messages
# user can only go to a conversation, select message underlying conversation and then delete
class MessageDeleteAPIView(DestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Message.objects.filter(Q(sender=self.request.user) |
                                          Q(receiver=self.request.user)).order_by('-created_at')

        queryset_next = queryset.filter(Q(conversation=self.request.parser_context['kwargs']['conversation_id']))
        return queryset_next


class SongListAPIView(ListAPIView):
    serializer_class = SongSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        text = self.request.query_params.get('q', None)
        if text is not None:
            songs = SearchQuerySet().autocomplete(text=text)
            if songs:
                pk_values = [song.object.pk for song in songs]
                query = reduce(lambda qu, pk_value: qu|Q(pk=pk_value), pk_values, Q())
                queryset = Song.objects.filter(query)
                return queryset
        elif text is None:
            queryset = Song.objects.all()
            return queryset


# creates restful API song list
class SongDetailAPIView(RetrieveAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsAdminUser]


# creates restful API user list
class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


