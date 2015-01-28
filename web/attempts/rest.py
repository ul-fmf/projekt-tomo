import json
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Attempt


class AttemptSerializer(serializers.ModelSerializer):
    """
    Serialize an Attempt object.
    """
    secret = CharField(write_only=True)

    class Meta:
        model = Attempt

    @staticmethod
    def check_secret(validated_data):
        # Check and remove secret from the validated_data dictionary
        user_secret = json.loads(validated_data.pop('secret', '[]'))
        secret_matches, hint = validated_data['part'].check_secret(user_secret)
        if not secret_matches:
            validated_data['valid'] = False

    def create(self, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).update(instance, validated_data)


class AttemptViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Attempt instances.
    """
    serializer_class = AttemptSerializer
    queryset = Attempt.objects.all()
