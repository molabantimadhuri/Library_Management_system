from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

FINE_PER_DAY = 5


def calculate_fine_for_issue(issue, return_date=None):
    if return_date is None:
        return_date = timezone.now().date()

    if return_date > issue.due_date:
        overdue_days = (return_date - issue.due_date).days
        return overdue_days * FINE_PER_DAY
    return 0


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    copies = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['title']

    @property
    def available_copies(self):
        active_issues = self.issues.filter(return_date__isnull=True).count()
        return self.copies - active_issues

    @property
    def issued_copies(self):
        return self.issues.filter(return_date__isnull=True).count()

    def __str__(self):
        return self.title


class Member(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ['name']

    @property
    def books_issued(self):
        return self.issues.filter(return_date__isnull=True).count()

    def __str__(self):
        return self.name


class Issue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='issues')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='issues')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-issue_date']

    @property
    def status(self):
        if self.return_date is not None:
            return 'Returned'
        if timezone.now().date() > self.due_date:
            return 'Overdue'
        return 'Issued'

    def __str__(self):
        return f'{self.book.title} - {self.member.name}'
