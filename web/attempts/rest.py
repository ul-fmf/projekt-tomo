from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import validators, decorators, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Field
from rest_framework.viewsets import ModelViewSet
from utils.rest import JSONStringField
from .models import Attempt


def update_fields(obj, new_values):
    changed_fields = []
    for field, value in new_values.items():
        if value != getattr(obj, field):
            setattr(obj, field, value)
        changed_fields.append(field)
    return changed_fields


class WritableJSONField(Field):
    def to_internal_value(self, data):
        return data


class AttemptSerializer(ModelSerializer):
    """
    Serialize an Attempt object.
    """
    secret = WritableJSONField(write_only=True, required=False)
    feedback = JSONStringField()

    class Meta:
        model = Attempt

    @staticmethod
    def check_secret(validated_data):
        # Check and remove secret from the validated_data dictionary
        user_secret = validated_data.pop('secret', '[]')
        secret_matches, wrong_index = validated_data['part'].check_secret(user_secret)
        if not secret_matches:
            validated_data['valid'] = False
            return wrong_index

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
        serializer = AttemptSerializer(data=request.data, many=True, partial=True)

        def _f(validator):
            return not isinstance(validator, validators.UniqueTogetherValidator)
        serializer.child.validators = filter(_f, serializer.child.validators)

        if serializer.is_valid():
            attempts = []
            wrong_indices = {}
            for attempt_data in serializer.validated_data:
                wrong_index = AttemptSerializer.check_secret(attempt_data)
                wrong_indices[attempt_data['part'].pk] = wrong_index
                updated_fields = None
                try:
                    attempt = Attempt.objects.get(user=request.user,
                                                  part=attempt_data['part'])
                    updated_fields = update_fields(attempt, attempt_data)
                except ObjectDoesNotExist:
                    attempt = Attempt(user=request.user, **attempt_data)
                finally:
                    attempt.save(update_fields=updated_fields)
                    attempts.append(attempt)
            data = {
                'attempts': AttemptSerializer(attempts, many=True).data,
                'wrong_indices': wrong_indices
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
