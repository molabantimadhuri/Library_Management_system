from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Book, Issue, Member


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
        }),
    )


class SignUpForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'Your name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'you@example.com'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Create a password'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Enter it again'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The passwords do not match.')
        if password1 and not self.errors.get('password1'):
            user_model = get_user_model()
            user = user_model(username=cleaned_data.get('email', ''), email=cleaned_data.get('email', ''))
            try:
                validate_password(password1, user=user)
            except ValidationError as error:
                self.add_error('password1', error)
        return cleaned_data

    def save(self):
        user_model = get_user_model()
        email = self.cleaned_data['email']
        return user_model.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['name'].strip(),
        )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'copies']

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Title cannot be empty.')
        return title

    def clean_author(self):
        author = self.cleaned_data.get('author', '').strip()
        if not author:
            raise ValidationError('Author cannot be empty.')
        return author

    def clean_category(self):
        category = self.cleaned_data.get('category', '').strip()
        if not category:
            raise ValidationError('Category cannot be empty.')
        return category

    def clean_copies(self):
        copies = self.cleaned_data.get('copies')
        if copies is None or copies <= 0:
            raise ValidationError('Copies must be a positive integer.')
        return copies


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Name cannot be empty.')
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Email cannot be empty.')
        return email


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['book', 'member']

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        if book and book.available_copies <= 0:
            raise ValidationError('No copies available.')
        return cleaned_data
