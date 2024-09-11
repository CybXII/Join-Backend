from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from join.models import CustomUser, BoardItem
from rest_framework.authtoken.models import Token

class BoardViewTests(APITestCase):

    def setUp(self):
        # Create a user and authenticate
        self.user = CustomUser.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a sample board item
        self.board_item = BoardItem.objects.create(
            title="Test Task",
            description="Test Task Description",
            due_date="2024-12-31",
            prio=2,
            task_status=0,
            position=1,
            category="Work",
            author_id=1
        )

    def test_get_board_items(self):
        # Test the GET method for BoardView
        url = reverse('tasks-list')  # URL name for the GET/POST requests
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tasks', response.data)
        self.assertIn('assignAble', response.data)

    def test_post_board_item(self):
        # Test the POST method for BoardView
        url = reverse('tasks-list')  # URL name for the GET/POST requests
        data = {
            "title": "New Task",
            "description": "New Task Description",
            "due_date": "2024-12-31",
            "prio": 0,
            "task_status": 3,
            "position": 2,
            "category": "Technical Task",
            "author_id": 1  # Beispiel für ein zusätzliches Pflichtfeld
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Task")

    def test_put_board_item(self):
        # Test the PUT method for BoardView
        url = reverse('tasks-detail', args=[self.board_item.id])  # URL name for PUT/DELETE requests
        data = {
            "title": "Updated Task",
            "description": "Updated Task Description",
            "prio": 1,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board_item.refresh_from_db()
        self.assertEqual(self.board_item.title, "Updated Task")

    def test_delete_board_item(self):
        # Test the DELETE method for BoardView
        url = reverse('tasks-detail', args=[self.board_item.id])  # URL name for PUT/DELETE requests
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(BoardItem.objects.filter(id=self.board_item.id).exists())


class LoginViewTests(APITestCase):

    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='testpassword'
        )

    def test_login(self):
        url = reverse('login')  # URL name for login
        data = {'username': 'test@test.com', 'password': 'testpassword'}
        response = self.client.post(url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        url = reverse('login')  # URL name for login
        data = {'email': 'test@test.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
