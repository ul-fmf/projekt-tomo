from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework import decorators, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
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

    @decorators.list_route(methods=['post'], authentication_classes=[TokenAuthentication])
    @transaction.atomic
    def submit(self, request):
        serializer = ProblemSerializer(data=request.data, many=False)

        # Send BAD_REQUEST with error details on invalid input data
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # So the data is valid
        parts_data = request.data.pop('parts')
        problem_data = request.data

        # If problem_data has no id save it and its parts to the database
        if 'id' not in problem_data:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Get the problem from database.
        # If problem does not exist, respond with BAD_REQEST
        # with exception details.
        problem = None
        try:
            problem = Problem.objects.get(pk=problem_data['id'])
        except Exception, e:
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST)

        existing_parts = problem.parts.all()
        parts_to_update_data = filter(lambda part: 'id' in part, parts_data)
        parts_to_create_data = filter(lambda part: 'id' not in part, parts_data)
        parts_to_delete = existing_parts.exclude(id__in=[part['id']
                                                         for part in parts_to_update_data])
        parts_to_update = existing_parts.filter(id__in=[part['id']
                                                        for part in parts_to_update_data])
        # Make sure all parts to update are part of the problem
        if parts_to_update.count() != len(parts_to_update_data):
            existing_ids = set(parts_to_update.values_list('id', flat=True))
            to_update_ids = set([part['id'] for part in parts_to_update_data])
            missing_ids = to_update_ids.difference(existing_ids)
            message = 'Parts with ids {0} are not in the database.'.format(missing_ids)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # First save the problem instance, use partial since essential parts data is missing
        problem_serializer = ProblemSerializer(data=problem_data, instance=problem, partial=True)
        problem_serializer.is_valid(raise_exception=False)
        problem = problem_serializer.save()
        # Delete not needed parts.
        # Beware: all attempts for these parts will be deleted.
        parts_to_delete.delete()
        # Create new parts
        serializer = PartSerializer(data=parts_to_create_data, many=True)
        serializer.is_valid(raise_exception=False)
        serializer.save()
        # Update existing parts
        for parts_data in parts_to_update_data:
            part = parts_to_update.get(id=parts_data['id'])
            serializer = PartSerializer(data=parts_data, instance=part)
            serializer.is_valid(raise_exception=False)
            serializer.save()
        return Response(ProblemSerializer(instance=problem).data, status=status.HTTP_200_OK)
