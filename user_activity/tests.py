from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import UserActivityLog


class ActivityLogTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

        self.log1 = UserActivityLog.objects.create(
            user=self.user1,
            action='login',
            status='PENDING'
        )
        self.log2 = UserActivityLog.objects.create(
            user=self.user2,
            action='logout',
            status='DONE'
        )

        # Setup clients
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

    # I. Model Creation Tests
    def test_model_creation(self):
        """Test UserActivityLog model instance creation"""
        log = UserActivityLog.objects.create(
            user=self.user1,
            action='test_action',
            status='PENDING'
        )
        self.assertEqual(log.action, 'test_action')
        self.assertEqual(log.status, 'PENDING')
        self.assertEqual(log.user.username, 'user1')

    # II. API Endpoint Tests
    def test_unauthenticated_access(self):
        """Test unauthenticated access returns 403"""
        client = APIClient()
        response = client.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_logs(self):
        """User sees only their own logs"""
        response = self.client1.get('/api/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['action'], 'login')

    def test_create_log(self):
        """Test log creation with auto user assignment"""
        data = {'action': 'UPLOAD_FILE'}
        response = self.client1.post('/api/logs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user1.id)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_retrieve_log(self):
        """Test retrieving own log"""
        response = self.client1.get(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'LOGIN')

    def test_retrieve_others_log(self):
        """Cannot retrieve another user's log"""
        response = self.client1.get(f'/api/logs/{self.log2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_log(self):
        """Test updating own log"""
        data = {'action': 'LOGOUT'}
        response = self.client1.patch(f'/api/logs/{self.log1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'LOGOUT')

    def test_delete_log(self):
        """Test deleting own log"""
        response = self.client1.delete(f'/api/logs/{self.log1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserActivityLog.objects.count(), 1)

    # III. State Transition Tests
    def test_valid_state_transition(self):
        """Test valid status transition (PENDING → IN_PROGRESS)"""
        response = self.client1.patch(
            f'/api/logs/{self.log1.id}/transition/',
            {'status': 'IN_PROGRESS'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.log1.refresh_from_db()
        self.assertEqual(self.log1.status, 'IN_PROGRESS')

    def test_invalid_transition(self):
        """Test invalid status transition (PENDING → DONE)"""
        response = self.client1.patch(
            f'/api/logs/{self.log1.id}/transition/',
            {'status': 'DONE'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid transition', response.data['error'])

    def test_invalid_status_value(self):
        """Test invalid status value"""
        response = self.client1.patch(
            f'/api/logs/{self.log1.id}/transition/',
            {'status': 'INVALID_STATUS'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid status', response.data['error'])
