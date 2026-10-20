from django.contrib.auth.models import Group, User
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.test import TestCase

from .admin import AdminSignupRequestAdmin
from .models import AdminSignupRequest, Student


class AccountFlowTests(TestCase):
    def setUp(self):
        self.student_group, _ = Group.objects.get_or_create(name='Student')
        self.student_user = User.objects.create_user(
            username='student1',
            password='StudentStrong!2026',
            email='student@example.com',
        )
        self.student_group.user_set.add(self.student_user)
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Test',
            last_name='Student',
            email='student@example.com',
            mobile_no='1234567890',
            roll_number='S001',
        )
        self.admin_user = User.objects.create_superuser(
            username='admin1',
            email='admin@example.com',
            password='AdminStrong!2026',
        )

    def test_account_choice_shows_separate_login_options(self):
        response = self.client.get('/accounts/login/')
        self.assertContains(response, '/accounts/student/login/')
        self.assertContains(response, '/accounts/admin/login/')
        self.assertContains(response, '/accounts/student/signup/')
        self.assertContains(response, '/accounts/admin/signup/')

    def test_student_and_admin_login_pages_reject_other_role(self):
        response = self.client.post('/accounts/student/login/', {
            'username': 'admin1',
            'password': 'AdminStrong!2026',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post('/accounts/admin/login/', {
            'username': 'student1',
            'password': 'StudentStrong!2026',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post('/accounts/student/login/', {
            'username': 'student1',
            'password': 'StudentStrong!2026',
        })
        self.assertRedirects(response, '/dashboard/student/')
        self.client.logout()

        response = self.client.post('/accounts/admin/login/', {
            'username': 'admin1',
            'password': 'AdminStrong!2026',
        })
        self.assertRedirects(response, '/dashboard/admin/')

    def test_student_can_sign_up_and_is_logged_in(self):
        response = self.client.post('/accounts/student/signup/', {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'mobile_no': '9876543210',
            'roll_number': 'S002',
            'password1': 'NewStudentStrong!2026',
            'password2': 'NewStudentStrong!2026',
        })
        self.assertRedirects(response, '/dashboard/student/')
        user = User.objects.get(username='newstudent')
        self.assertTrue(user.groups.filter(name='Student').exists())
        self.assertEqual(user.student_profile.roll_number, 'S002')
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_admin_signup_creates_inactive_request_not_staff(self):
        response = self.client.post('/accounts/admin/signup/', {
            'username': 'pendingadmin',
            'first_name': 'Pending',
            'last_name': 'Admin',
            'email': 'pending@example.com',
            'password1': 'PendingAdminStrong!2026',
            'password2': 'PendingAdminStrong!2026',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pending approval')
        user = User.objects.get(username='pendingadmin')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(AdminSignupRequest.objects.filter(user=user).exists())

    def test_existing_admin_can_approve_signup_request(self):
        pending_user = User.objects.create_user(
            username='pending',
            email='pending@example.com',
            password='PendingStrong!2026',
            is_active=False,
        )
        signup_request = AdminSignupRequest.objects.create(user=pending_user)
        request = RequestFactory().post('/admin/api_v1/adminsignuprequest/')
        SessionMiddleware(lambda request: None).process_request(request)
        request.user = self.admin_user
        request._messages = FallbackStorage(request)
        model_admin = AdminSignupRequestAdmin(AdminSignupRequest, admin.site)

        model_admin.approve_requests(
            request, AdminSignupRequest.objects.filter(pk=signup_request.pk)
        )

        pending_user.refresh_from_db()
        signup_request.refresh_from_db()
        self.assertTrue(pending_user.is_active)
        self.assertTrue(pending_user.is_staff)
        self.assertIsNotNone(signup_request.approved_at)

    def test_non_staff_cannot_open_admin_dashboard(self):
        ordinary_user = User.objects.create_user(
            username='ordinary', password='OrdinaryStrong!2026'
        )
        self.client.force_login(ordinary_user)
        response = self.client.get('/dashboard/admin/')
        self.assertRedirects(response, '/accounts/admin/login/')

# Create your tests here.
