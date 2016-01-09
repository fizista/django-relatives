from __future__ import unicode_literals
import django
from django.test import TestCase
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from distutils.version import StrictVersion as SV


from relatives.utils import object_link, object_edit_link
from .models import (Pirate, Pet, Ship, Sailor, Movie, Actor, NotInAdmin,
                     Something, Book, Image, Journal)


def version(default_value, django18__gte=None, django19__gte=None):
    "Return correct value for correct version liblary"

    django_ver = '.'.join([str(v) for v in django.VERSION[0:2]])

    if django18__gte and SV(django_ver) >= SV('1.8'):
        return django18__gte
    if django19__gte and SV(django_ver) >= SV('1.9'):
        return django19__gte

    return default_value


class ObjectEditLinkTest(TestCase):

    def test_default(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        self.assertEqual(
            object_edit_link()(ship),
            version(
                '<a href="/adm/tests/ship/1/">Star of India</a>',
                django19__gte='<a href="/adm/tests/ship/1/change/">Star of India</a>'
            )
        )
        pirate = Pirate.objects.create(id=1, name="Lowell Taylor")
        self.assertEqual(object_edit_link()(pirate), "Lowell Taylor")

    def test_custom_edit_text(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        self.assertEqual(
            object_edit_link("Go There")(ship),
            version(
                '<a href="/adm/tests/ship/1/">Go There</a>',
                django19__gte='<a href="/adm/tests/ship/1/change/">Go There</a>'
            )
        )

    def test_default_blank_text(self):
        pirate = Pirate.objects.create(id=1, name="Lowell Taylor")
        self.assertEqual(object_edit_link("Edit")(pirate), "")

    def test_custom_edit_and_blank_text(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        pirate = Pirate.objects.create(id=1, name="Lowell Taylor")
        self.assertEqual(
            object_edit_link("Go There", "N/A")(ship),
            version(
                '<a href="/adm/tests/ship/1/">Go There</a>',
                django19__gte='<a href="/adm/tests/ship/1/change/">Go There</a>'
            )
        )
        self.assertEqual(object_edit_link("Go There", "N/A")(pirate), "N/A")


class ObjectLinkTest(TestCase):

    def test_no_admin_url(self):
        pirate = Pirate.objects.create(id=1, name="Lowell Taylor")
        self.assertEqual(object_link(pirate), "Lowell Taylor")

    def test_with_primary_key(self):
        ship = Ship.objects.create(id=1, name="Star of India")
        self.assertEqual(
            object_link(ship),
            version(
                '<a href="/adm/tests/ship/1/">Star of India</a>',
                django19__gte='<a href="/adm/tests/ship/1/change/">Star of India</a>'
            )
        )


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
        self.assertIn(
            version(
                b'<a href="/adm/tests/ship/1/">Star of India</a>',
                django19__gte=b'<a href="/adm/tests/ship/1/change/">Star of India</a>'
            ),
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

    def test_add_form_for_non_nullable_fk(self):
        self.login()
        response = self.client.get(reverse('admin:tests_pet_add'))
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

    def test_generic_foreign_key_not(self):
        book = Book.objects.create(name="Django")
        body = render_to_string('related_objects_generic_test.html',
                                {'obj': book})
        self.assertEqual(body.strip(), '')

    def test_generic_foreign_key_present(self):
        book = Book.objects.create(name="Django")
        Image.objects.create(content_object=book)
        ct_pk = ContentType.objects.get_for_model(book).pk
        exp = '<a href="/adm/tests/image/?ct={0}&amp;obj_id={1}">Images</a>'\
            .format(ct_pk, book.pk)
        body = render_to_string('related_objects_generic_test.html',
                                {'obj': book})
        self.assertEqual(body.strip(), exp)

    def test_generic_relation_and_gfk_present(self):
        journal = Journal.objects.create(name="Django")
        Image.objects.create(content_object=journal)
        ct_pk = ContentType.objects.get_for_model(journal).pk
        exp = '<a href="/adm/tests/image/?ct={0}&amp;obj_id={1}">Images</a>'\
            .format(ct_pk, journal.pk)
        body = render_to_string('related_objects_generic_test.html',
                                {'obj': journal})
        self.assertEqual(body.strip(), exp)
