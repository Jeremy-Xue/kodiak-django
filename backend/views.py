from django.shortcuts import render

# Create your views here.
from backend.models import *
from backend.serializers import *
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime

# class BackendListCreate(generics.ListCreateAPIView):
#     queryset = Child.objects.all()
#     serializer_class = ChildSerializer

class ChildList(generics.ListCreateAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

class ParentList(generics.ListCreateAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

class ActivityList(generics.ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

@api_view(["POST"])
def create_enrollment(request):
    request.data....

    #send_email(enrollment_id, parent_email)
    #hostname/#/confirm_enrollment/enrollment_id
    #hostname/#/cancel_enrollment/enrollment_id
@api_view(["POST"])
def activity_post(request):
    if request.method == "POST":
        #when creating an activity, need to create the days that correspond
            #to its running
        result_days_of_occurrence = []
        for day in request.data["days_of_occurrence"]:
            daySerializer=DaySerializer(data={"day": day})
            if (daySerializer.is_valid()):
                d = daySerializer.save()
                result_days_of_occurrence.append(d.id)
            else:
                return Response(daySerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        del request.data["days_of_occurrence"]
        activityData = request.data
        activityData["days_of_occurrence"] = result_days_of_occurrence
        activityData["start_date"] = datetime.datetime.strptime(activityData["start_date"], '%m/%d/%Y').strftime('%Y-%m-%d') 
        activityData["end_date"] = datetime.datetime.strptime(activityData["end_date"], '%m/%d/%Y').strftime('%Y-%m-%d')
        activitySerializer = ActivitySerializer(data=activityData)
        if activitySerializer.is_valid():
            activitySerializer.save()
            return Response(activitySerializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(activitySerializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnrollmentList(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    # print(queryset)
    serializer_class = EnrollmentSerializer

# class ChildList(generics.ListCreateAPIView):
#     queryset = Enrollment.objects.all()
#     serializer_class = EnrollmentSerializer