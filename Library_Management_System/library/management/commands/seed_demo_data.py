from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from library.models import Book, Issue, Member


BOOKS = [
    ('The Midnight Library', 'Matt Haig', 'Fiction', 4),
    ('The Alchemist', 'Paulo Coelho', 'Fiction', 5),
    ('Pride and Prejudice', 'Jane Austen', 'Classic', 3),
    ('To Kill a Mockingbird', 'Harper Lee', 'Classic', 3),
    ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 4),
    ('Harry Potter and the Philosopher’s Stone', 'J.K. Rowling', 'Fantasy', 5),
    ('Sapiens', 'Yuval Noah Harari', 'History', 3),
    ('Atomic Habits', 'James Clear', 'Self-help', 4),
    ('A Brief History of Time', 'Stephen Hawking', 'Science', 2),
    ('The Psychology of Money', 'Morgan Housel', 'Finance', 3),
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic', 3),
    ('Educated', 'Tara Westover', 'Biography', 2),
]

MEMBERS = [
    ('Aarav Sharma', 'aarav.sharma@example.com'),
    ('Ananya Patel', 'ananya.patel@example.com'),
    ('Rohan Mehta', 'rohan.mehta@example.com'),
    ('Isha Reddy', 'isha.reddy@example.com'),
    ('Kabir Nair', 'kabir.nair@example.com'),
    ('Meera Iyer', 'meera.iyer@example.com'),
]


class Command(BaseCommand):
    help = 'Add repeatable example books, members, and issue activity.'

    @transaction.atomic
    def handle(self, *args, **options):
        books = {}
        members = {}
        book_count = 0
        member_count = 0

        for title, author, category, copies in BOOKS:
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={'author': author, 'category': category, 'copies': copies},
            )
            books[title] = book
            book_count += int(created)

        for name, email in MEMBERS:
            member, created = Member.objects.get_or_create(
                email=email,
                defaults={'name': name},
            )
            members[email] = member
            member_count += int(created)

        today = timezone.localdate()
        active_book = books['The Midnight Library']
        active_member = members['aarav.sharma@example.com']
        Issue.objects.get_or_create(
            book=active_book,
            member=active_member,
            issue_date=today,
            defaults={'due_date': today + timedelta(days=14)},
        )

        returned_book = books['The Alchemist']
        returned_member = members['ananya.patel@example.com']
        Issue.objects.get_or_create(
            book=returned_book,
            member=returned_member,
            issue_date=today - timedelta(days=20),
            defaults={
                'due_date': today - timedelta(days=6),
                'return_date': today - timedelta(days=4),
                'fine': 10,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready: {book_count} books and {member_count} members added; sample issue activity is available.'
        ))
