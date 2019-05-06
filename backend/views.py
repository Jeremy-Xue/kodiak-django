from django.shortcuts import render

# Create your views here.
from backend.models import *
from django.contrib.auth.models import User
from backend.serializers import *
from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
#JWT Authentication token stuff
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
import datetime
#email stuff
from django.conf import settings
from django.core.mail import send_mail
import random
import string
from django.core import serializers

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


from rest_auth.views import LoginView


class LoginView(generics.CreateAPIView):
# class BackendListCreate(generics.ListCreateAPIView):
#     queryset = Child.objects.all()
#     serializer_class = ChildSerializer
    queryset=User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username=request.data.get("username", "")
        password=request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            userSerialized = UserSerializer(user)
            # userSerialized.is_valid()
            print(userSerialized.data)
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            serializer = AuthSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                ),
                "status": "authorized",
                "user": userSerialized.data,
            })
            serializer.is_valid()
            print(serializer.data)
            return Response(serializer.data)
        else:
            serializer = AuthSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": "",
                "status": "unauthorized"
            })
            serializer.is_valid()
            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
class RegisterUsers(generics.CreateAPIView):
    """
    POST auth/register/
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("email", "") # only going to have email and password
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not username and not password and not email:
            return Response(
                data={
                    "message": "username, password and email is required to register a user"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_user = User.objects.create_user(
            username=username, password=password, email=email
        )
        return Response(status=status.HTTP_201_CREATED)

DEPLOYED_HOST = "https://kibsd-sessions.firebaseapp.com/"
class ActivityRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivityDetailSerializer
    authentication_classes=(JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

class ChildList(generics.ListCreateAPIView):
    authentication_classes=(JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

class ParentList(generics.ListCreateAPIView):
    authentication_classes=(JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

class ActivityList(generics.ListAPIView):
    # authentication_classes=(JSONWebTokenAuthentication,)
    permission_classes = (AllowAny,)
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class EnrollmentRUD(generics.RetrieveUpdateDestroyAPIView):
    # authentication_classes=(JSONWebTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


def generate_token(e_ids):
    parent_token_info = dict()
    # parent_token_info['enrollments'] = e_id
    h = str(hash(''.join(map((lambda x: str(x)), e_ids))))
    real_hash = ""
    for c in h:
        if (not c.isalpha()):
            real_hash += random.choice(string.ascii_uppercase + string.ascii_lowercase)
        else:
            real_hash += c
    parent_token_info["token"] = real_hash #''.join([random.choice(string.ascii_letters) for i in range(64)])
    parent_serializer = ParentTokenSerializer(data=parent_token_info)
    if (parent_serializer.is_valid()):
        p = parent_serializer.save()
        for e_id in e_ids:
            e = Enrollment.objects.get(pk=e_id)
            e.token = p
            e.save()
    # change this to include the else case
    return parent_token_info

@api_view(["POST"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def batch_update_enrollments(request):
    e_ids = request["enrollment_ids"]
    new_enrollment_statuses = request["enrollment_updates"]
    response = dict(); response
    for i in range(len(e_ids)):
        e_id = e_ids[i]; new_status = new_enrollment_statuses[i];
        enrollment = Enrollment.objects.get(pk=e_id)
        if (new_status == 'confirmed'):
            enrollment.confirmed=True
            enrollment.save()
            send_confirmation_email(e_id)
        elif (new_status == 'canceled'):
            send_cancellation_email(e_id)
            enrollment.delete()
    
    return Response(dict(), status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def enrollments_by_token(request, token):
    token_obj = ParentToken.objects.get(token=token)
    enrollments = Enrollment.objects.filter(token=token_obj)
    e_serialized = list(map(lambda x: EnrollmentSerializer(x).data, enrollments))
    # e_serialized = serializers.serialize('json', enrollments)
    response = dict()
    response["enrollments"] = e_serialized
    return Response(response,  status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def confirm_enrollment(request, pk):
    e_id = pk
    try:
        enrollment_we_want = Enrollment.objects.get(pk=e_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    enrollment_we_want.confirmed = True
    enrollment_we_want.save()
    send_confirmation_email(e_id)
    return Response(EnrollmentSerializer(enrollment_we_want).data, status=status.HTTP_206_PARTIAL_CONTENT)

@api_view(["GET"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def cancel_enrollment(request, pk):
    e_id = pk
    try:
        enrollment_we_want = Enrollment.objects.get(pk=e_id)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    send_cancellation_email(e_id)
    enrollment_we_want.delete()
    return Response(EnrollmentSerializer(enrollment_we_want).data, status=status.HTTP_206_PARTIAL_CONTENT)


@api_view(["POST"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
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
        parent_email = child.parent.email
        # parent_email = request.data['parent_email']
        e_ids = []; activities = [];
        for activity_id in request.data["activities"]:
            activity = Activity.objects.get(pk=activity_id)
            activities.append(activity)
            enrollment_info['activity'] = activity_id
            enrollment_info['child'] = child.id
            serializer = EnrollmentSaveSerializer(data=enrollment_info)
            if (serializer.is_valid()):
                e = serializer.save()
                e_ids.append(e.id)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token_info = generate_token(e_ids)
        send_email_single(token=token_info['token'], parent_email=parent_email, child=child, activities=activities)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def resend_confirm(request, pk):
    enrollment_info_ser = dict()
    e_id = pk
    enrollment_info = Enrollment.objects.get(pk = e_id)
    child = Child.objects.get(id = enrollment_info.child_id)
    activity = Activity.objects.get(id = enrollment_info.activity_id)
    parent_email = child.parent.email

    enrollment_info_ser['activity'] = activity.id
    enrollment_info_ser['child'] = child.id

    serializer = EnrollmentSaveSerializer(data=enrollment_info_ser)
    if (serializer.is_valid()):
        num_emails_sent = send_email_single(enrollment_id=e_id, parent_email=parent_email, child=child, activity=activity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_confirmation_email(enrollment_id=None):
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

def send_cancellation_email(enrollment_id=None):
    enrollment = Enrollment.objects.get(pk=enrollment_id)
    child = Child.objects.get(pk=enrollment.child)
    activity = Activity.objects.get(pk=enrollment.activity)
    parent = Parent.objects.get(pk=child.parent)
    subject = "Enrollment Cancelled!"
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    # recipient_list = ['mytest@gmail.com', 'you@email.com']
    recipient_list=[parent.email]
    html_message =  """
        <h1>{}'s enrollment in {} succesfully cancelled!</h1>
                    """.format(child.first_name, activity.title)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

@api_view(["GET"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def send_all_emails(request):
    # parent_email = "roman.a.kaufman@gmail.com"
    for parent in Parent.objects.all():
        parent_email = parent.email
        if ("example" in parent_email):
            continue
        send_email_weekly_update(parent_email)
    return Response(dict(), status=status.HTTP_200_OK)

def send_email_weekly_update(parent_email=""):
    from functools import reduce
    # confirm_route = "http://injuredroman.github.io/kodiak_sign_up/#/update_enrollments/%s"%(token)
    signup_route = DEPLOYED_HOST + "#/signup"
    #cancel_route = "http://injuredroman.github.io/kodiak_sign_up/#/cancel_enrollment/%s"%(token)
    subject = "KIBSD Sessions Weekly Digest"
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    recipient_list=[parent_email]
    parent = Parent.objects.get(email=parent_email)
    children_portion = ""
    today = datetime.datetime.now().date()
    next_seven_days = [today + datetime.timedelta(days=i) for i in range(7)]
    relevance_function = lambda a: reduce(lambda x, y: x and y, [a.start_date <= day <= a.end_date for day in next_seven_days])
    for child in parent.child_set.all():
        child_portion = ""
        activities = list(child.activity_set.all())
        relevant_activities = list(filter(relevance_function, activities))
        if (len(relevant_activities)) > 0:
            child_portion += "<p> {}'s enrollments this week:".format(child.first_name)
            child_portion += "<ul>"
            child_portion += "".join("<li>" + str(activity.title) + "</li>" for activity in relevant_activities)
            child_portion += "</ul>"
        else:
            child_portion += "<p> {} doesn't have any sessions scheduled for this week!".format(child.first_name)
        child_portion += "</p>"

        children_portion += child_portion
    html_message = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width"/>

    <!-- For development, pass document through inliner -->

    <style type="text/css">
    * {{ margin: 0; padding: 0; font-size: 100%; font-family: 'Avenir Next', "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif; line-height: 1.65; }}

    img {{ max-width: 100%; margin: 0 auto; display: block; }}

    body, .body-wrap {{ width: 100% !important; height: 100%; background: #f8f8f8; }}

    a {{ color: #71bc37; text-decoration: none; }}

    a:hover {{ text-decoration: underline; }}

    .text-center {{ text-align: center; }}

    .text-right {{ text-align: right; }}

    .text-left {{ text-align: left; }}

    .button {{ display: inline-block; color: white; background: #71bc37; border: solid #71bc37; border-width: 10px 20px 8px; font-weight: bold; border-radius: 4px; }}

    .button:hover {{ text-decoration: none; }}

    h1, h2, h3, h4, h5, h6 {{ margin-bottom: 20px; line-height: 1.25; }}

    h1 {{ font-size: 32px; }}

    h2 {{ font-size: 28px; }}

    h3 {{ font-size: 24px; }}

    h4 {{ font-size: 20px; }}

    h5 {{ font-size: 16px; }}

    p, ul, ol {{ font-size: 16px; font-weight: normal; margin-bottom: 20px; }}

    .container {{ display: block !important; clear: both !important; margin: 0 auto !important; max-width: 580px !important; }}

    .container table {{ width: 100% !important; border-collapse: collapse; }}

    .container .masthead {{ padding: 80px 0; background: #71bc37; color: white; }}

    .container .masthead h1 {{ margin: 0 auto !important; max-width: 90%; text-transform: uppercase; }}

    .container .content {{ background: white; padding: 30px 35px; }}

    .container .content.footer {{ background: none; }}

    .container .content.footer p {{ margin-bottom: 0; color: #888; text-align: center; font-size: 14px; }}

    .container .content.footer a {{ color: #888; text-decoration: none; font-weight: bold; }}

    .container .content.footer a:hover {{ text-decoration: underline; }}

        </style>
    </head>
<body>
<table class="body-wrap">
    <tr>
        <td class="container">

            <!-- Message start -->
            <table>
                <tr>
                    <td align="center" class="masthead">

                        <h1>KIBSD Sessions Weekly Digest</h1>

                    </td>
                </tr>
                <tr>
                    <td class="content">

                        <h2>Hi Parent, here are your children's activities for this upcoming week: </h2> 
                        """ + children_portion + """

                        <table>
                            <tr>
                                <td align="center">
                                    <p>
                                        <a href="{}" class="button">Sign up for more!</a>
                                    </p>
                                </td>
                            </tr>
                        </table>
                        <p><em>– KIBSD</em></p>

                    </td>
                </tr>
            </table>

        </td>
    </tr>
    <tr>
        <td class="container">

            <!-- Message start -->
            <table>
                <tr>
                    <td class="content footer" align="center">
                        <p>Sent by <a href="#">KIBSD</a>, Address Placeholder</p>
                        <p><a href="mailto:">hello@company.com</a> | <a href="#">Unsubscribe</a></p>
                    </td>
                </tr>
            </table>

        </td>
    </tr>
</table>
</body>
</html>""".format(signup_route)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

def send_email_single(token="", parent_email="", child="", activities=""):
    # confirm_route = "http://injuredroman.github.io/kodiak_sign_up/#/update_enrollments/%s"%(token)
    confirm_route = DEPLOYED_HOST + "#/update_enrollments/%s"%(token)
    #cancel_route = "http://injuredroman.github.io/kodiak_sign_up/#/cancel_enrollment/%s"%(token)
    subject = "Confirm %s's enrollments"%(child.first_name)
    from_email = settings.DEFAULT_FROM_EMAIL
    message = ''
    recipient_list=[parent_email]
    html_message = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width"/>

    <!-- For development, pass document through inliner -->

    <style type="text/css">
    * {{ margin: 0; padding: 0; font-size: 100%; font-family: 'Avenir Next', "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif; line-height: 1.65; }}

    img {{ max-width: 100%; margin: 0 auto; display: block; }}

    body, .body-wrap {{ width: 100% !important; height: 100%; background: #f8f8f8; }}

    a {{ color: #71bc37; text-decoration: none; }}

    a:hover {{ text-decoration: underline; }}

    .text-center {{ text-align: center; }}

    .text-right {{ text-align: right; }}

    .text-left {{ text-align: left; }}

    .button {{ display: inline-block; color: white; background: #71bc37; border: solid #71bc37; border-width: 10px 20px 8px; font-weight: bold; border-radius: 4px; }}

    .button:hover {{ text-decoration: none; }}

    h1, h2, h3, h4, h5, h6 {{ margin-bottom: 20px; line-height: 1.25; }}

    h1 {{ font-size: 32px; }}

    h2 {{ font-size: 28px; }}

    h3 {{ font-size: 24px; }}

    h4 {{ font-size: 20px; }}

    h5 {{ font-size: 16px; }}

    p, ul, ol {{ font-size: 16px; font-weight: normal; margin-bottom: 20px; }}

    .container {{ display: block !important; clear: both !important; margin: 0 auto !important; max-width: 580px !important; }}

    .container table {{ width: 100% !important; border-collapse: collapse; }}

    .container .masthead {{ padding: 80px 0; background: #71bc37; color: white; }}

    .container .masthead h1 {{ margin: 0 auto !important; max-width: 90%; text-transform: uppercase; }}

    .container .content {{ background: white; padding: 30px 35px; }}

    .container .content.footer {{ background: none; }}

    .container .content.footer p {{ margin-bottom: 0; color: #888; text-align: center; font-size: 14px; }}

    .container .content.footer a {{ color: #888; text-decoration: none; font-weight: bold; }}

    .container .content.footer a:hover {{ text-decoration: underline; }}

        </style>
    </head>
<body>
<table class="body-wrap">
    <tr>
        <td class="container">

            <!-- Message start -->
            <table>
                <tr>
                    <td align="center" class="masthead">

                        <h1>Confirm your child's enrollment</h1>

                    </td>
                </tr>
                <tr>
                    <td class="content">

                        <h2>Hi Parent,</h2>

                        <p> Please confirm or cancel {}'s enrollment in:

                        """.format(child.first_name) + "".join("<p>" + str(activity.title) + "</p>" for activity in activities) + """


                        </p>

                        <table>
                            <tr>
                                <td align="center">
                                    <p>
                                        <a href="{}" class="button">Take me to my Enrollments!</a>
                                    </p>
                                </td>
                            </tr>
                        </table>

                        <p>This link will expire in 1 day.</p>

                        <p><em>– KIBSD</em></p>

                    </td>
                </tr>
            </table>

        </td>
    </tr>
    <tr>
        <td class="container">

            <!-- Message start -->
            <table>
                <tr>
                    <td class="content footer" align="center">
                        <p>Sent by <a href="#">KIBSD</a>, Address Placeholder</p>
                        <p><a href="mailto:">hello@company.com</a> | <a href="#">Unsubscribe</a></p>
                    </td>
                </tr>
            </table>

        </td>
    </tr>
</table>
</body>
</html>""".format(confirm_route)
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

# Email time code
# Please confirm or cancel {}'s enrollment in {}, from {} to {}, between {} and {}. 
# 

@api_view(["POST"])
@authentication_classes((JSONWebTokenAuthentication,))
@permission_classes((IsAuthenticated,))
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
    authentication_classes=(JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Enrollment.objects.all()
    # print(queryset)
    serializer_class = EnrollmentSerializer

# class ChildList(generics.ListCreateAPIView):
#     queryset = Enrollment.objects.all()
#     serializer_class = EnrollmentSerializer