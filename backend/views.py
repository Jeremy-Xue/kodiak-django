from django.shortcuts import render

# Create your views here.
from backend.models import *
from backend.serializers import *
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
from django.conf import settings
from django.core.mail import send_mail

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

class EnrollmentRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

@api_view(["GET"])
def confirm_enrollment(request, pk):
    e_id = pk
    try:
        enrollment_we_want = Enrollment.objects.get(pk=e_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    enrollment_we_want.confirmed = True
    enrollment_we_want.save()
    send_confirmation_email(e_id)
    print("here")
    return Response(EnrollmentSerializer(enrollment_we_want).data, status=status.HTTP_206_PARTIAL_CONTENT)

@api_view(["POST"])
def create_enrollment(request):
    enrollment_info = dict()
    child_fname = request.data["child_first_name"]
    child_lname = request.data["child_last_name"]
    children_that_match = Child.objects.filter(first_name__contains=child_fname,last_name__contains=child_lname)
    if (len(children_that_match) == 0):
        #we didn't find a child with this name, we'd like to find one
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else: #hopefully only one child was found
        child = children_that_match.first()
        # parent_email = child.parent.email
        parent_email = request.data['parent_email']
        activity_id = request.data["activity"]
        activity = Activity.objects.get(pk=activity_id)
        enrollment_info['activity'] = activity_id
        enrollment_info['child'] = child.id
        serializer = EnrollmentSaveSerializer(data=enrollment_info)
        if (serializer.is_valid()):
            e = serializer.save()
            num_emails_sent = send_email(enrollment_id=e.id, parent_email=parent_email, child=child, activity=activity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_confirmation_email(enrollment_id=None,hostname="https://banana-tart-91724.herokuapp.com"):
    enrollment = Enrollment.objects.get(pk=enrollment_id)
    child = Child.objects.get(pk=enrollment.child.pk)
    activity = Activity.objects.get(pk=enrollment.activity.pk)
    parent = Parent.objects.get(pk=child.parent.pk)
    subject = "Enrollment Confirmed!"
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    # recipient_list = ['mytest@gmail.com', 'you@email.com']
    recipient_list=[parent.email]
    html_message =  """
        <h1>{}'s enrollment in {} confirmed!</h1>
                    """.format(child.first_name, activity.title)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
def send_cancellation_email(enrollment_id=None,hostname="https://banana-tart-91724.herokuapp.com"):
    enrollment = Enrollment.objects.get(pk=enrollment_id)
    child = Child.objects.get(pk=enrollment.child)
    activity = Activity.objects.get(pk=enrollment.activity)
    parent = Parent.objects.get(pk=child.parent)
    subject = "Enrollment Confirmed!"
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    # recipient_list = ['mytest@gmail.com', 'you@email.com']
    recipient_list=[parent.email]
    html_message =  """
        <h1>{}'s enrollment in {} confirmed!</h1>
                    """.format(child.first_name, activity.title)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

def send_email(enrollment_id=0, parent_email="", child="", activity=""):
    confirm_route = "http://injuredroman.github.io/kodiak_sign_up/#/confirm_enrollment/%d"%(enrollment_id)
    hostname="http://127.0.0.1:8000/"
    confirm_route = hostname + "api/confirm_enrollment/{}/".format(enrollment_id)
    cancel_route = "http://injuredroman.github.io/kodiak_sign_up/#/cancel_enrollment/%d"%(enrollment_id)
    subject = "Confirm %s's enrollment in %s"%(child.first_name, activity.title)
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    recipient_list=[parent_email]
    html_message = """<body> Please confirm or cancel {}'s enrollment in {}, from {} to {}, between {} and {}.\n
          <button class="btn btn-success" "><a href="{}"> Confirm Enrollment</a></button>
          <button class="btn btn-success" "><a href="{}"> Cancel Enrollment</a></button>
       </body>""".format(child.first_name, activity.title, activity.start_date, activity.end_date, activity.start_time, activity.end_time, confirm_route, cancel_route)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)


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