from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import *


class LoginPageViewTest(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_login_page_view_authenticated_user(self):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request to the login page
        response = self.client.get(reverse('login_page'))

        # Check if the response redirects to the manager dashboard (assuming test_user is a superuser)
        self.assertRedirects(response, reverse('manager_dashboard'))

    def test_login_page_view_invalid_credentials(self):
        # Attempt to log in with invalid credentials
        response = self.client.post(reverse('login_page'), {
                                    'username': 'testuser', 'password': 'wrongpassword'})

        # Check if the response status code is 200 (login page with errors)
        self.assertEqual(response.status_code, 200)

        # Check if an error message is displayed
        self.assertContains(response, "Invalid Username or Password")

    def test_login_page_view_unauthenticated_user(self):
        # Make a GET request to the login page when not logged in
        response = self.client.get(reverse('login_page'))

        # Check if the response status code is 200 (login page)
        self.assertEqual(response.status_code, 200)


class AddStaffViewTest(TestCase):
    def test_add_staff_view(self):
        # Create a test user for authentication
        test_user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Prepare data for the staff member to be added
        data = {
            'username': 'newstaff',
            'password': 'newpassword',
            'conform_password': 'newpassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '1234567890',
        }

        # Make a POST request to the add_staff view with the data
        response = self.client.post(reverse('add_staff'), data)

        # Check if the response status code is 302 (redirection after success)
        self.assertEqual(response.status_code, 302)

        # Check if the staff member was added to the database
        staff = Staff.objects.get(user__username='newstaff')
        self.assertEqual(staff.first_name, 'John')
        self.assertEqual(staff.last_name, 'Doe')
        self.assertEqual(staff.email, 'john@example.com')

    def test_add_staff_view_with_existing_user(self):
        # Create a test user for authentication
        test_user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Create an existing staff member
        Staff.objects.create(
            user=test_user,
            first_name='Existing',
            last_name='Staff',
            email='existing@example.com',
            phone_number='1234567890'
        )

        # Prepare data for a staff member with an existing username
        data = {
            'username': 'testuser',  # Existing username
            'password': 'newpassword',
            'conform_password': 'newpassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '1234567890',
        }

        # Make a POST request to the add_staff view with the data
        response = self.client.post(reverse('add_staff'), data)

        # Check if the response status code is 200 (form errors)
        self.assertEqual(response.status_code, 200)

        # Check if an error message is displayed
        self.assertContains(response, "Username or email already exists.")

    def test_add_staff_view_with_password_mismatch(self):
        # Create a test user for authentication
        test_user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Prepare data for a staff member with password mismatch
        data = {
            'username': 'newstaff',
            'password': 'password1',
            'conform_password': 'password2',  # Passwords don't match
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '1234567890',
        }

        # Make a POST request to the add_staff view with the data
        response = self.client.post(reverse('add_staff'), data)

        # Check if the response status code is 200 (form errors)
        self.assertEqual(response.status_code, 200)

        # Check if an error message is displayed
        self.assertContains(response, "Passwords do not match.")


class AddTaskViewTestCase(TestCase):
    def test_add_task_with_valid_data(self):
        # Create a valid POST request with unique title and future due date
        response = self.client.post(
            reverse('add_task'),  # Assuming 'add_task' is the URL name for your view
            {
                'title': 'New Task',
                'description': 'Description of the task',
                'due_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Future date
                'priority': 'High',
                'status': 'pending',
            }
        )

        # Check if the response redirects to the manager_dashboard
        self.assertRedirects(response, reverse('manager_dashboard'))  # Adjust URL name if needed

        # Check if the task was added successfully (you may need to adjust this based on your model)
        self.assertEqual(Task.objects.count(), 1)

    def test_add_task_with_duplicate_title(self):
        # Create a task with the same title to simulate a duplicate title
        Task.objects.create(
            title='New Task',
            description='Existing Task Description',
            due_date=timezone.now() + timedelta(days=2),
            priority='High',
            status='pending',
        )

        # Attempt to add a task with the same title
        response = self.client.post(
            reverse('add_task'),
            {
                'title': 'New Task',
                'description': 'Description of the task',
                'due_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Future date
                'priority': 'High',
                'status': 'pending',
            }
        )

        # Check if the response contains the error message for duplicate title
        self.assertContains(response, "A task with the same title already exists.")

        # Check if the task count remains the same (no new task added)
        self.assertEqual(Task.objects.count(), 1)

    def test_add_task_with_past_due_date(self):
        # Attempt to add a task with a past due date
        response = self.client.post(
            reverse('add_task'),
            {
                'title': 'New Task',
                'description': 'Description of the task',
                'due_date': (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Past date
                'priority': 'High',
                'status': 'pending',
            }
        )

        # Check if the response contains the error message for past due date
        self.assertContains(response, "The due date cannot be in the past.")

        # Check if the task count remains the same (no new task added)
        self.assertEqual(Task.objects.count(), 0)  # No task should be added
