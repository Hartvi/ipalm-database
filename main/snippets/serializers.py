from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Snippet, Snippet2

User = get_user_model()


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(
        view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner', 'title', 'code',
                  'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)
    snippets2 = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet2-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets', 'snippets2')  # which fields to display on the site


class Snippet2Serializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(view_name='customuser-detail', read_only=True)
    # owner = UserSerializer()
    snippet = serializers.HyperlinkedRelatedField(
        many=False, view_name='snippet-detail', read_only=True)

    class Meta:
        model = Snippet2
        fields = ('url', 'owner', 'snippet')


