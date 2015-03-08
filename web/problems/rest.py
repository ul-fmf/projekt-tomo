from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from utils.rest import JSONStringField
from .models import Problem, Part


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
