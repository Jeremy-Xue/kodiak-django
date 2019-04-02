import factory  
import factory.django

from . import models
from datetime import date, timedelta
import datetime
import random
YEARS_TO_KINDERGARDEN = 5

class ParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Parent

    email = factory.Sequence(lambda n: 'parent_{}@example.com'.format(n))

class ChildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Child

    # choose parent from all possible parent objects
    parent = factory.Iterator(models.Parent.objects.all())
    first_name = factory.Sequence(lambda n: "Child{}".format(n))
    last_name = factory.Faker('name')
    grade = factory.Iterator([1, 3, 5, 6])
    date_of_birth = factory.LazyAttribute(lambda o: date.today() - timedelta(days=365*(o.grade + YEARS_TO_KINDERGARDEN)))


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Activity
    title = factory.Sequence(lambda n: "Activity {}".format(n))

    #rest aren't necessary
    start_date = factory.LazyAttribute(lambda g: date.today())
    end_date = factory.LazyAttribute(lambda g: date.today())
    start_time = factory.LazyAttribute(lambda g: datetime.datetime.now().time())
    end_time = factory.LazyAttribute(lambda g: datetime.datetime.now().time())
    youngest_enrolled = 2
    oldest_enrolled = 2
    max_enrollment = 2

class EnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Enrollment

    activity = factory.Iterator(models.Activity.objects.all())
    child = factory.Iterator(models.Child.objects.all())
    confirmed = factory.Iterator([True, False])

def makeitall():
    for _ in range(10):
        ParentFactory.create()
    for _ in range(10):
        ChildFactory.create()
    for _ in range(5):
        ActivityFactory.create()
    for _ in range(20):
        EnrollmentFactory.create()