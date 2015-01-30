import hashlib
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.conf import settings
from .models import Problem


def generate_token(user_id, problem_id, secret_key=settings.SECRET_KEY):
    return hashlib.sha512('{0}-{1}-{2}'.format(secret_key, user_id, problem_id)).hexdigest()


class ProblemSerializer(ModelSerializer):
    """
    Serialize a Problem object.
    """
    secret = SerializerMethodField()

    class Meta:
        model = Problem

    def get_secret(self, problem):
        return generate_token(self.context['request'].user.id, problem.id)
        

class ProblemViewSet(ModelViewSet):
    """
    A viewset for viewing and editing Problem instances.
    """
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()
