from rest_framework import serializers


class SelfFollowValidator:

    def __call__(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError("You can't follow yourself")
