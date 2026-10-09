from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookForm, IssueForm, MemberForm, SignUpForm
from .models import Book, Issue, Member, calculate_fine_for_issue


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='library.authentication.EmailBackend')
            messages.success(request, 'Your account is ready. Welcome to the library!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'library/signup.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.now().date()
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    total_available = sum(book.available_copies for book in Book.objects.all())
    issued_books = Issue.objects.filter(return_date__isnull=True).count()
    returned_books = Issue.objects.filter(return_date__isnull=False).count()
    overdue_books = Issue.objects.filter(return_date__isnull=True, due_date__lt=today).count()
    total_fines = Issue.objects.filter(return_date__isnull=False).aggregate(total=Sum('fine'))['total'] or 0
    recent_activity = Issue.objects.select_related('book', 'member').order_by('-issue_date')[:8]

    context = {
        'total_books': total_books,
        'total_available': total_available,
        'total_members': total_members,
        'issued_books': issued_books,
        'returned_books': returned_books,
        'overdue_books': overdue_books,
        'total_fines': total_fines,
        'recent_activity': recent_activity,
    }
    return render(request, 'library/dashboard.html', context)


@login_required
def book_list(request):
    books = Book.objects.all()
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category:
        books = books.filter(category__iexact=category)

    categories = Book.objects.order_by('category').values_list('category', flat=True).distinct()
    context = {
        'books': books,
        'query': query,
        'selected_category': category,
        'categories': categories,
    }
    return render(request, 'library/book_list.html', context)


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add Book'})


@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'book': book, 'title': 'Edit Book'})


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    issues = book.issues.select_related('member').all()
    context = {'book': book, 'issues': issues}
    return render(request, 'library/book_detail.html', context)


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    active_issues = book.issues.filter(return_date__isnull=True).exists()
    if request.method == 'POST':
        if active_issues:
            messages.error(request, 'Cannot delete this book because it has active issues.')
            return redirect('book_detail', pk=book.pk)
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')

    context = {'object': book, 'title': 'Delete Book', 'message': 'Are you sure you want to delete this book?'}
    return render(request, 'library/confirm_delete.html', context)


@login_required
def member_list(request):
    members = Member.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        members = members.filter(Q(name__icontains=query) | Q(email__icontains=query))

    context = {'members': members, 'query': query}
    return render(request, 'library/member_list.html', context)


@login_required
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member registered successfully.')
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'library/member_form.html', {'form': form, 'title': 'Register Member'})


@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully.')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)
    return render(request, 'library/member_form.html', {'form': form, 'member': member, 'title': 'Edit Member'})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    issues = member.issues.select_related('book').all()
    context = {'member': member, 'issues': issues}
    return render(request, 'library/member_detail.html', context)


@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    active_issues = member.issues.filter(return_date__isnull=True).exists()
    if request.method == 'POST':
        if active_issues:
            messages.error(request, 'Cannot delete this member because they have active issues.')
            return redirect('member_detail', pk=member.pk)
        member.delete()
        messages.success(request, 'Member deleted successfully.')
        return redirect('member_list')

    context = {'object': member, 'title': 'Delete Member', 'message': 'Are you sure you want to delete this member?'}
    return render(request, 'library/confirm_delete.html', context)


@login_required
def issue_book(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            member = form.cleaned_data['member']
            if book.available_copies <= 0:
                messages.error(request, 'Book is currently unavailable. No copies available.')
                return render(request, 'library/issue_book.html', {'form': form})

            issue = form.save(commit=False)
            issue.issue_date = timezone.now().date()
            issue.due_date = issue.issue_date + timedelta(days=14)
            issue.fine = 0
            issue.save()
            messages.success(request, f'Book issued to {member.name} successfully.')
            return redirect('issue_list')
    else:
        form = IssueForm()
    return render(request, 'library/issue_book.html', {'form': form})


@login_required
def issue_list(request):
    issues = Issue.objects.select_related('book', 'member').all()
    filter_status = request.GET.get('status', '').strip()
    today = timezone.now().date()

    if filter_status == 'issued':
        issues = issues.filter(return_date__isnull=True, due_date__gte=today)
    elif filter_status == 'returned':
        issues = issues.filter(return_date__isnull=False)
    elif filter_status == 'overdue':
        issues = issues.filter(return_date__isnull=True, due_date__lt=today)

    context = {'issues': issues, 'filter_status': filter_status}
    return render(request, 'library/issue_list.html', context)


@login_required
def return_book(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        if issue.return_date is not None:
            messages.error(request, 'This book has already been returned.')
            return redirect('issue_list')

        return_date = timezone.now().date()
        issue.return_date = return_date
        issue.fine = calculate_fine_for_issue(issue, return_date)
        issue.save()
        messages.success(request, f'Book returned successfully. Fine: ₹{issue.fine}')
        return redirect('issue_list')

    return redirect('issue_list')
