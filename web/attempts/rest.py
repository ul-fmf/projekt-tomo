import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from rest_framework import fields, decorators, validators
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .models import Attempt


class AttemptSerializer(ModelSerializer):
    """
    Serialize an Attempt object.
    """
    secret = fields.CharField(write_only=True)

    class Meta:
        model = Attempt

    @staticmethod
    def check_secret(validated_data):
        # Check and remove secret from the validated_data dictionary
        user_secret = json.loads(validated_data.pop('secret', '[]'))
        secret_matches, hint = validated_data['part'].check_secret(user_secret)
        if not secret_matches:
            validated_data['accepted'] = False

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

    @decorators.list_route(methods=['post'])
    def submit(self, request):
        serializer = AttemptSerializer(data=request.data)
        def _f(validator):
            return not isinstance(validator, validators.UniqueTogetherValidator)
        serializer.validators = filter(_f, serializer.validators)
        if serializer.is_valid():
            AttemptSerializer.check_secret(serializer.validated_data)
            created = Attempt.objects.update_or_create(
                              user=serializer.validated_data['user'],
                              part=serializer.validated_data['part'],
                              defaults=serializer.validated_data)[1]
            status = HTTP_201_CREATED if created else HTTP_200_OK
            response = {'status': 'submission saved'}
            return Response(json.dumps(response), status=status)
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)
