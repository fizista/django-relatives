from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
try:
    from django.contrib.contenttypes.generic import GenericForeignKey
except ImportError:
    # Django >= 1.9
    from django.contrib.contenttypes.fields import GenericForeignKey
try:
    from django.contrib.contenttypes.generic import GenericRelation
except ImportError:
    # Django >= 1.9
    from django.contrib.contenttypes.fields import GenericRelation


@python_2_unicode_compatible
class Pirate(models.Model):

    """Pirates have no admin URL"""

    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Pet(models.Model):

    """Pet have an admin URL and link to Pirates"""

    owner = models.ForeignKey(Pirate)


@python_2_unicode_compatible
class Ship(models.Model):

    """Ships have an admin URL and are linked to by sailors"""

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Sailor(models.Model):

    """Sailors have an admin URL and sometimes link to ships"""

    name = models.CharField(max_length=80)
    ship = models.ForeignKey(Ship, null=True)

    def __str__(self):
        return self.name


class Actor(models.Model):

    """Actors have an admin URL and a many-to-many relationship with movies"""

    name = models.CharField(max_length=80)
    movies = models.ManyToManyField('Movie', related_name='actors')


class Movie(models.Model):

    """Movies have an admin URL and are linked to (m2m) by actors"""

    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Something(models.Model):

    """Somethings don't have an admin URL and are linked to by NotInAdmins"""

    text = models.CharField(max_length=10)

    def __str__(self):
        return self.text


class NotInAdmin(models.Model):

    """NotInAdmins do not have an admin URL and link to Somethings"""

    fk = models.ForeignKey(Something)


class Book(models.Model):

    """Book have an admin URL and are linked to images via GenericForeignKey"""

    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Image(models.Model):

    """Image have an admin URL and link to Book via GenericForeignKey"""

    ct = models.ForeignKey(ContentType)
    obj_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('ct', 'obj_id')

    def __str__(self):
        return str(self.content_object)


class Journal(models.Model):

    """Journal have an admin URL and are linked to images via GenericForeignKey
    also it have GenericRelation link to Images"""

    name = models.CharField(max_length=10)
    images = GenericRelation(Image)

    def __str__(self):
        return self.name
