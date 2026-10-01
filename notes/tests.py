from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Note


User = get_user_model()


class NotesApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='owner-pass-123')
        self.other_user = User.objects.create_user(username='other', password='other-pass-123')

    def test_registration_login_and_profile(self):
        response = self.client.post(
            '/register/',
            {'username': 'new-user', 'password': 'new-user-pass-123', 'email': 'new@example.com'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

        response = self.client.post(
            '/login/',
            {'username': 'new-user', 'password': 'new-user-pass-123'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        profile = self.client.get('/profile/')
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data['username'], 'new-user')

    def test_notes_require_authentication_and_only_owner_can_mutate(self):
        self.assertEqual(self.client.get('/notes/').status_code, status.HTTP_401_UNAUTHORIZED)
        note = Note.objects.create(title='Private', content='Text', owner=self.owner)
        self.client.force_authenticate(user=self.other_user)

        self.assertEqual(self.client.get(f'/notes/{note.id}/').status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.patch(f'/notes/{note.id}/', {'title': 'Changed'}).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(f'/notes/{note.id}/').status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(user=self.owner)
        created = self.client.post('/notes/', {'title': 'Owned', 'content': 'Created by owner'})
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['owner'], self.owner.username)

        response = self.client.patch(f'/notes/{note.id}/', {'title': 'Changed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Changed')
        self.assertEqual(self.client.delete(f'/notes/{note.id}/').status_code, status.HTTP_204_NO_CONTENT)

    def test_note_list_search_ordering_and_pagination(self):
        Note.objects.bulk_create([
            Note(title=f'Note {index:02}', content='needle' if index == 4 else 'other', owner=self.owner)
            for index in range(12)
        ])
        self.client.force_authenticate(user=self.owner)

        response = self.client.get('/notes/?search=needle&page_size=2&ordering=-title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Note 04')

        paginated = self.client.get('/notes/?title__icontains=Note&ordering=-title&page_size=5')
        self.assertEqual(paginated.data['count'], 12)
        self.assertEqual(len(paginated.data['results']), 5)
        self.assertEqual(paginated.data['results'][0]['title'], 'Note 11')

    def test_note_uses_auto_field_primary_key(self):
        self.assertEqual(Note._meta.pk.get_internal_type(), 'AutoField')
