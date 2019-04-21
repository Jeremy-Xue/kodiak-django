from rest_framework import serializers
from backend.models import *
from django.contrib.auth.models import User

class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = '__all__'

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class EnrollmentSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
    child = ChildSerializer(read_only=True)
    activity = ActivitySerializer(read_only=True)

class UserSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
