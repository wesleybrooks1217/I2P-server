from rest_framework import serializers
from .models import College


# Create your serializers here.

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ('id', 'name')
