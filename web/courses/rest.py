from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Course, ProblemSet


class ProblemSetSerializer(ModelSerializer):
    """
    Serialize a ProblemSet object.
    """
    class Meta:
        model = ProblemSet
        fields = ('id', 'title')


class CourseSerializer(ModelSerializer):
    """
    Serialize a Course object.
    """
    problem_sets = ProblemSetSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'problem_sets')


class CourseViewSet(ReadOnlyModelViewSet):
    """
    A viewset for (read-only) viewing Course instances.
    """
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.taught_courses.all()
