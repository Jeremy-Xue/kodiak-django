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
    serializer = EnrollmentSerializer(data=request.data)
    if serializer.is_valid():
        child_fname = request.data["child_first_name"]
        child_lname = request.data["child_last_name"]
        children_that_match = Child.objects.filter(first_name__contains=child_fname,last_name__contains=child_lname)
        if (len(children_that_match) == 0):
            #we didn't find a child with this name, we'd like to find one
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else: #hopefully only one child was found
            child = children_that_match.first()
            parent_email = child.parent.email
            activity_id = request.data["activity"]
            activity_name = Activity.objects.get(pk=activity_id).title
            e = serializer.save()
            #send_email(enrollment_id, parent_email, child_name, activity_name)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class EnrollmentList(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    # print(queryset)
    serializer_class = EnrollmentSerializer

# class ChildList(generics.ListCreateAPIView):
#     queryset = Enrollment.objects.all()
#     serializer_class = EnrollmentSerializer