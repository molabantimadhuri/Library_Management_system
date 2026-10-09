from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import EmailAuthenticationForm

urlpatterns = [
    path('accounts/login/', LoginView.as_view(
        authentication_form=EmailAuthenticationForm,
        template_name='library/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_create, name='member_create'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_update, name='member_update'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/issue/', views.issue_book, name='issue_book'),
    path('issues/<int:pk>/return/', views.return_book, name='return_book'),
]
