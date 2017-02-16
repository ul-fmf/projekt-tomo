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
        fields = '__all__'


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
        except Exception as e:
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST)

        existing_parts = problem.parts.all()
        parts_to_update_data = [part for part in parts_data if 'id' in part]
        parts_to_create_data = [part for part in parts_data if 'id' not in part]
        parts_to_delete = existing_parts.exclude(id__in=[part['id']
                                                         for part in parts_to_update_data])
        parts_to_update = existing_parts.filter(id__in=[part['id']
                                                        for part in parts_to_update_data])
        # Make sure all parts to update are part of the problem
        if parts_to_update.count() != len(parts_to_update_data):
            existing_ids = set(parts_to_update.values_list('id', flat=True))
            to_update_ids = set([part['id'] for part in parts_to_update_data])
            missing_ids = to_update_ids.difference(existing_ids)
            missing_ids = ['@{0:06d}'.format(missing_id) for missing_id in missing_ids]
            message = 'Parts {0} do not belong to the given problem.'.format(', '.join(missing_ids))
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        # Prepare custom sort order
        # Assign None to ids of not already created parts
        sort_order = [part.get('id', None) for part in parts_data]
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
        created_ids = [o.id for o in serializer.save()]
        assert sort_order.count(None) == len(created_ids)
        # Insert ids of created tasks into sort order
        created_position = 0
        for i in range(len(sort_order)):
            if sort_order[i] == None:
                sort_order[i] = created_ids[created_position]
                created_position += 1
        problem.set_part_order(sort_order)
        # Update existing parts
        for parts_data in parts_to_update_data:
            part = parts_to_update.get(id=parts_data['id'])
            serializer = PartSerializer(data=parts_data, instance=part)
            serializer.is_valid(raise_exception=False)
            serializer.save()
        serialized_data = ProblemSerializer(instance=problem).data
        serialized_data['update'] = problem.edit_file(request.user)[1]
        return Response(serialized_data, status=status.HTTP_200_OK)
