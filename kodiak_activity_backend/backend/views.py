from django.shortcuts import render

# Create your views here.
from backend.models import *
from backend.serializers import *
from rest_framework import generics

class BackendListCreate(generics.ListCreateAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
