from django.db import models
from django.core.validators import validate_email

###################################
## Helper Model
###################################
class Day(models.Model):
    DAY_POSSIBILITIES = (
        ('MON', "Monday"),
        ('TUE', "Tuesday"),
        ('WED', "Wednesday"),
        ('THU', "Thursday"),
        ('FRI', "Friday"),
        ('SAT', "Saturday"),
        ('SUN', "Sunday")
    )
    day = models.CharField(max_length=3, choices=DAY_POSSIBILITIES)
###################################
## Helper Model ^
###################################

class Parent(models.Model):
    email = models.EmailField()
    # email = models.EmailField(primary_key=True)

class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    grade = models.IntegerField()
    # below line not necessary, can access which activies a child is enrolled in
    #   from the child without it
    # activities = models.ManyToManyField(Activity, through="Enrollment")

class Activity(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    youngest_enrolled = models.IntegerField()
    oldest_enrolled = models.IntegerField()
    max_enrollment = models.IntegerField()
    enrolled_students = models.ManyToManyField(Child, through="Enrollment")
    group_code = models.CharField(max_length=10)


    ##################
    #this is honestly a bit hacky and I don't like it, but it's the simplest solution
    # for now
    ##################
    days_of_occurrence = models.ManyToManyField(Day)
    ##################
    #this is honestly a bit hacky and I don't like it, but it's the simplest solution
    # for now
    ##################
class ParentToken(models.Model):
    token = models.CharField(max_length=100)

class Enrollment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    token = models.ForeignKey(ParentToken, on_delete=models.SET_NULL, null=True)
    confirmed = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ('child', 'activity', )

