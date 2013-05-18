from __future__ import unicode_literals
from django.test import TestCase
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from relatives.utils import edit_link
from .models import (Pirate, Pet, Ship, Sailor, Movie, Actor, NotInAdmin,
                     Something)


class EditLinkTest(TestCase):

    def test_no_admin_url(self):
        pirate = Pirate.objects.create(id=1, name="Lowell Taylor")
        self.assertEqual(edit_link(pirate), "Lowell Taylor")

    def test_with_primary_key(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        self.assertEqual(edit_link(ship),
                         '<a href="/adm/tests/ship/1/">Star of India</a>')

    def test_no_primary_key(self):
        ship = Ship(name="Star of India")
        self.assertEqual(edit_link(ship), "Star of India")


class TemplateFilterTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('u', 'u@example.com', 'pass')

    def login(self):
        self.client.login(username=self.user.username, password='pass')

    def test_foreign_key(self):
        self.login()
        ship = Ship.objects.create(id=1, name="Star of India")
        sailor = Sailor.objects.create(name="John Ford", ship=ship)
        response = self.client.get(reverse('admin:tests_sailor_change',
                                           args=[sailor.id]))
        self.assertIn(b'<a href="/adm/tests/ship/1/">Star of India</a>',
                      response.content)

    def test_no_foreign_key(self):
        self.login()
        ship = Ship.objects.create(id=1, name="Star of India")
        response = self.client.get(reverse('admin:tests_ship_change',
                                           args=[ship.id]))
        self.assertIn(b'<p>Star of India</p>', response.content)

    def test_foreign_key_without_admin_url(self):
        self.login()
        pirate = Pirate.objects.create(id=1, name="Kristi Bell")
        pet = Pet.objects.create(owner=pirate)
        response = self.client.get(reverse('admin:tests_pet_change',
                                           args=[pet.id]))
        self.assertIn(b'Kristi Bell', response.content)
        self.assertNotIn(b'Kristi Bell</a>', response.content)
        self.assertNotIn(b'Kristi Bell</option>', response.content)

    def test_nullable_foreign_key(self):
        self.login()
        sailor = Sailor.objects.create(name="John Ford")
        response = self.client.get(reverse('admin:tests_sailor_change',
                                           args=[sailor.id]))
        self.assertIn(b'(None)', response.content)


class RelatedObjectsTagTest(TestCase):
    def test_foreign_keys(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        body = render_to_string('related_objects_fk_test.html', {'obj': ship})
        self.assertEqual(body.strip(),
                         '<a href="/adm/tests/sailor/?ship=1">Sailors</a>')

    def test_no_admin_url(self):
        thing = Something.objects.create()
        NotInAdmin.objects.create(id=1, fk=thing)
        body = render_to_string('related_objects_fk_test.html', {'obj': thing})
        self.assertEqual(body.strip(), '')

    def test_many_to_many(self):
        movie = Movie.objects.create(id=1, name="Yojimbo")
        actor = Actor.objects.create(name="Tatsuya Nakadai")
        actor.movies.add(movie)
        body = render_to_string('related_objects_m2m_test.html',
                                {'obj': movie})
        self.assertEqual(body.strip(),
                         '<a href="/adm/tests/actor/?movies=1">Actors</a>')

    def test_reverse_many_to_many(self):
        movie = Movie.objects.create(id=1, name="Yojimbo")
        actor = Actor.objects.create(name="Tatsuya Nakadai")
        actor.movies.add(movie)
        body = render_to_string('related_objects_m2m_test.html',
                                {'obj': actor})
        self.assertEqual(body.strip(), '')