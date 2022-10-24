from problems.rest import ProblemSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from utils.rest import DownloadMixin

from .models import Course, ProblemSet


class ProblemSetBackupSerializer(ModelSerializer):
    """
    Serialize an entire ProblemSet object.
    """

    problems = ProblemSerializer(many=True)

    class Meta:
        model = ProblemSet


class ProblemSetSerializer(ModelSerializer):
    """
    Serialize a ProblemSet object.
    """

    class Meta:
        model = ProblemSet
        fields = ("id", "title")


class CourseBackupSerializer(ModelSerializer):
    """
    Serialize an entire ProblemSet object.
    """

    problem_sets = ProblemSetBackupSerializer(many=True)

    class Meta:
        model = Course


class CourseSerializer(ModelSerializer):
    """
    Serialize a Course object.
    """

    problem_sets = ProblemSetSerializer(many=True)

    class Meta:
        model = Course
        fields = ("id", "title", "problem_sets")


class ProblemSetViewSet(GenericViewSet, DownloadMixin):
    """
    A viewset for serializing/deserializing ProblemSet instances.
    """

    serializer_class = ProblemSetBackupSerializer
    queryset = ProblemSet.objects.all()


class CourseViewSet(GenericViewSet, DownloadMixin):
    """
    A viewset for serializing/deserializing Course instances.
    """

    serializer_class = CourseBackupSerializer
    queryset = Course.objects.all()
