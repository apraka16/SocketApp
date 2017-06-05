from rest_framework.serializers import ModelSerializer, CharField, EmailField
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from chat.models import Conversation, Message, Song
from django.db.models import Q


class ConversationSerializer(ModelSerializer):
    user1_name = CharField(source='user1', read_only=True)
    user2_name = CharField(source='user2', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            # 'user1',
            # 'user2',
            'user1_name',
            'user2_name',
            'started_at',
        ]


class ConversationCreateSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'user2',
        ]


class MessageCreateSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'message',
        ]


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'receiver',
            'created_at',
            'message',
        ]


class SongSerializer(ModelSerializer):
    artist_name = CharField(source='artist', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id',
            'category',
            'song_name',
            'song_desc',
            'song',
            'artist',
            'artist_name',
            'album',
            'alias',
            'genre',
            'mood',
            'song_language',
            'song_country',
            'created_at',
            'last_used',
            'song_impression',
        ]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
        ]


class UserCreateSerializer(ModelSerializer):
    email = EmailField(label='Email Address')
    email2 = EmailField(label='Confirm Email')

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
        ]
        extra_kwargs = {"password":
                        {"write_only": True}
                        }

    # def validate(self, data):
    #     return data

    def validate_email(self, value):
        data = self.get_initial()
        email1 = data.get("email2")
        email2 = value
        if email1 != email2:
            raise ValidationError("Emails must match")

        user_qs = User.objects.filter(email=email2)
        if user_qs.exists():
            raise ValidationError("This email already exists")

        return value

    def validate_email2(self, value):
        data = self.get_initial()
        email1 = data.get("email")
        email2 = value
        if email1 != email2:
            raise ValidationError("Emails must match")
        return value

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_obj = User(
            username=username,
            email=email,
        )
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    username = CharField(required=False, allow_blank=True)
    email = EmailField(label='Email Address', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'token',
        ]
        extra_kwargs = {"password":
                            {"write_only": True}
                        }

    def validate(self, data):
        user_obj = None
        username = data.get("username", None)
        email = data.get("email", None)
        password = data["password"]
        if not email and not username:
            raise ValidationError("A username and/ or email is required")

        user = User.objects.filter(
            Q(email=email) |
            Q(username=username)
        ).distinct()
        user = user.exclude(email__isnull=True).exclude(email__iexact='')
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError("This username/ email is not valid")

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect credentials")

        data["token"] = "RANDOM TOKEN"
        return data
