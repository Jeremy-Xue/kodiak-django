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
    day = models.CharField(max_length=3, options=DAY_POSSIBILITIES)
###################################
## Helper Model ^
###################################

class Parent(models.Model):
    # email = models.CharField(primary_key=True, max_length=50,
    #         validators=[validate_email])
    email = models.EmailField(primary_key=True)

class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    grade = models.IntegerField()
    activities = models.ManyToManyField(Activity, through="Assignment")

class Enrollment(models.Model):
    confirmed = models.BooleanField()

class Activity(models.Model):
    title = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    youngest_enrolled = models.IntegerField()
    oldest_enrolled = models.IntegerField()
    max_enrollment = models.IntegerField()
    enrolled_students = models.ManyToManyField(Child, through="Assignment")
    instructor = models.CharField()


    ##################
    #this is honestly a bit hacky and I don't like it, but it's the simplest solution
    # for now
    ##################
    days_of_occurrence = models.ManyToManyField(Day)
    ##################
    #this is honestly a bit hacky and I don't like it, but it's the simplest solution
    # for now
    ##################