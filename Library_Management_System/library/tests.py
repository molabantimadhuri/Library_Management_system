from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Book, Issue, Member, calculate_fine_for_issue


class BookModelTests(TestCase):
    def test_book_creation(self):
        book = Book.objects.create(title='Python Basics', author='A. Smith', category='Programming', copies=3)
        self.assertEqual(book.title, 'Python Basics')
        self.assertEqual(book.available_copies, 3)

    def test_book_validation(self):
        book = Book(title='', author='', category='', copies=0)
        with self.assertRaises(ValidationError):
            book.full_clean()


class MemberModelTests(TestCase):
    def test_member_creation(self):
        member = Member.objects.create(name='Alice', email='alice@example.com')
        self.assertEqual(member.name, 'Alice')

    def test_invalid_email_validation(self):
        member = Member(name='Bob', email='not-an-email')
        with self.assertRaises(ValidationError):
            member.full_clean()


class AuthenticationTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_signup_creates_and_logs_in_account(self):
        response = self.client.post(reverse('signup'), {
            'name': 'Library Admin',
            'email': 'ADMIN@example.com',
            'password1': 'Testpass!13579',
            'password2': 'Testpass!13579',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(get_user_model().objects.filter(email__iexact='admin@example.com').count(), 1)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_can_sign_in_with_email(self):
        user = get_user_model().objects.create_user(
            username='reader@example.com',
            email='reader@example.com',
            password='Testpass!13579',
        )
        response = self.client.post(reverse('login'), {
            'username': 'READER@example.com',
            'password': 'Testpass!13579',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.pk, user.pk)

    def test_signup_rejects_duplicate_email_case_insensitively(self):
        get_user_model().objects.create_user(
            username='reader@example.com',
            email='reader@example.com',
            password='Testpass!13579',
        )
        response = self.client.post(reverse('signup'), {
            'name': 'Another Reader',
            'email': 'READER@example.com',
            'password1': 'Different!13579',
            'password2': 'Different!13579',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email address already exists.')
        self.assertEqual(get_user_model().objects.filter(email__iexact='reader@example.com').count(), 1)


class IssueBusinessLogicTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title='Django for Beginners', author='Jane Doe', category='Technology', copies=2)
        self.member = Member.objects.create(name='Charlie', email='charlie@example.com')
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='librarian@example.com',
            email='librarian@example.com',
            password='Testpass!13579',
        )
        self.client.force_login(self.user)

    def test_successful_issue(self):
        response = self.client.post(reverse('issue_book'), {'book': self.book.pk, 'member': self.member.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Issue.objects.count(), 1)
        self.assertEqual(self.book.available_copies, 1)

    def test_issue_when_no_copies_exist(self):
        self.book.copies = 0
        self.book.save()
        response = self.client.post(reverse('issue_book'), {'book': self.book.pk, 'member': self.member.pk})
        self.assertContains(response, 'No copies available.')

    def test_successful_return(self):
        issue = Issue.objects.create(
            book=self.book,
            member=self.member,
            issue_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=5),
            fine=0,
        )
        response = self.client.post(reverse('return_book', args=[issue.pk]))
        self.assertEqual(response.status_code, 302)
        issue.refresh_from_db()
        self.assertIsNotNone(issue.return_date)
        self.assertGreater(issue.fine, 0)

    def test_fine_calculation(self):
        today = timezone.now().date()

        issue = Issue.objects.create(
            book=self.book,
            member=self.member,
            issue_date=today - timedelta(days=20),
            due_date=today - timedelta(days=2),
        )
        self.assertEqual(calculate_fine_for_issue(issue, today), 10)

        issue2 = Issue.objects.create(
            book=self.book,
            member=self.member,
            issue_date=today - timedelta(days=20),
            due_date=today + timedelta(days=5),
        )
        self.assertEqual(calculate_fine_for_issue(issue2, today), 0)

    def test_duplicate_return_prevention(self):
        issue = Issue.objects.create(
            book=self.book,
            member=self.member,
            issue_date=timezone.now().date() - timedelta(days=10),
            due_date=timezone.now().date() + timedelta(days=4),
            return_date=timezone.now().date(),
            fine=0,
        )
        response = self.client.post(reverse('return_book', args=[issue.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('issue_list'))
