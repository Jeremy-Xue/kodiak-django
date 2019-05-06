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
class ActivityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
    enrolled_students = ChildSerializer(read_only=True, many=True)

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
class ParentTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentToken
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

class UserSerializer(serializers.Serializer):
    email=serializers.CharField(max_length=200)
    # class Meta:
    #     model = User
    #     fields = ('email',)
    

class AuthSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=255)
    user = UserSerializer()