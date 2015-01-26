'''
Created on Jan 26, 2015

@author: gregor
'''

from rest_framework import serializers, viewsets, status, response
import json
from rest_framework.fields import CharField

from .models import Attempt
from problems.models import Part

class AttemptSerializer(serializers.ModelSerializer):
    """
    Serialize an Attempt object.
    """        
    secret = CharField(write_only=True)
    
    class Meta:
        model = Attempt
        
    @staticmethod
    def check_secret(validated_data):
        # Check and remove secret from the validated_data dictionary
        user_secret = validated_data.pop('secret', '[]')
        part_secret = validated_data['part'].secret
        if json.dumps(json.loads(user_secret)) != json.dumps(json.loads(part_secret)):
            validated_data['accepted'] = False 
    
    def create(self, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self.check_secret(validated_data)
        return super(AttemptSerializer, self).update(instance, validated_data)


class AttemptViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Attempt instances.
    """
    serializer_class = AttemptSerializer
    queryset = Attempt.objects.all()

