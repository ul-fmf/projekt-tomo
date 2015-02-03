import json
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import Field
from .models import Problem, Part


class JSONStringField(Field):
    """
    Store a JSON object in a TextField.
    When object is received store its json dump.
    When object is retrieved load JSON object from string representation.
    """
    def to_internal_value(self, data):
        return json.dumps(data)

    def to_representation(self, value):
        return json.loads(value)


class PartSerializer(ModelSerializer):
    """
    Serialize a Part object instance.
    """
    secret = JSONStringField()

    class Meta:
        model = Part
        exclude = ('_order',)


class ProblemSerializer(ModelSerializer):
    """
    Serialize a Problem object.
    """
    parts = PartSerializer(many=True)

    class Meta:
        model = Problem


class ProblemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing Problem instances.
    """
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()
