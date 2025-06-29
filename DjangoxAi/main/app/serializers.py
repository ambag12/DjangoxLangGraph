from .models import Doc,Staff
from rest_framework import serializers
from django.contrib.auth.models import User

class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model=Doc
        fields = ['title', 'content']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model=Staff
        fields="__all__"
        