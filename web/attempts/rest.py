import json
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer, Field
from rest_framework import validators, decorators, status
from rest_framework.response import Response
from .models import Attempt
from rest_framework.authentication import TokenAuthentication


class WritableJSONField(Field):
    def to_internal_value(self, data):
        return data


class AttemptSerializer(ModelSerializer):
    """
    Serialize an Attempt object.
    """
    secret = WritableJSONField(write_only=True, required=False)

    class Meta:
        model = Attempt

    @staticmethod
    def check_secret(validated_data):
        # Check and remove secret from the validated_data dictionary
        user_secret = validated_data.pop('secret', '[]')
        secret_matches = validated_data['part'].check_secret(user_secret)[0]
        if not secret_matches:
            validated_data['valid'] = False

    def create(self, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).update(instance, validated_data)


class AttemptViewSet(ModelViewSet):
    """
    A viewset for viewing and editing Attempt instances.
    """
    serializer_class = AttemptSerializer
    queryset = Attempt.objects.all()

    @decorators.list_route(methods=['post'], authentication_classes=[TokenAuthentication])
    @transaction.atomic    
    def submit(self, request):
        serializer = AttemptSerializer(data=request.data, many=True)
        def _f(validator):
            return not isinstance(validator, validators.UniqueTogetherValidator)
        serializer.child.validators = filter(_f, serializer.child.validators)
        
        if serializer.is_valid():
            for attempt in serializer.validated_data:
                AttemptSerializer.check_secret(attempt)
                Attempt.objects.update_or_create(
                        user=request.user,
                        part=attempt['part'],
                        defaults=attempt)
            response = {'status': 'submission saved'}
            return Response(json.dumps(response), status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
