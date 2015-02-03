from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from .models import Problem


class ProblemSerializer(ModelSerializer):
    """
    Serialize a Problem object.
    """
    class Meta:
        model = Problem


class ProblemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing Problem instances.
    """
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()
