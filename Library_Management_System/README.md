# Library Management System

## Objective
The Library Management System is a full-stack Django web application built to manage books, library members, issue/return operations, due dates, and fines. It is designed for beginners and is suitable for college-level projects.

## Features
- Email/password sign-in and account registration
- Library pages require an authenticated account
- Dashboard with summary cards and recent activity
- Book management with add, edit, delete, search, and filtering
- Member management with add, edit, delete, and search
- Issue books with validation and due date logic
- Return books with overdue fine calculation
- History page with filters for issued, returned, and overdue records
- Admin support for database management
- Responsive user interface using Bootstrap 5

## Technologies
- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap 5

## Database Design
book (one) -> issue (many)
member (one) -> issue (many)

ER diagram:

```text
BOOK
  |
  | 1
  |
  |----< ISSUE >----|
                     |
                     | 1
                     |
                  MEMBER
```

### Models
- Book: id, title, author, category, copies
- Member: id, name, email
- Issue: id, book, member, issue_date, due_date, return_date, fine

## Installation
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Usage
1. On the first visit, select **Create an account** and register with your name, email, and password. The new account is signed in automatically.
2. On later visits, sign in using that email address and password.
3. Use **Log out** in the navigation bar when finished.
4. The sample books, member profiles, and issue activity are loaded by `python manage.py seed_demo_data`. The command is safe to rerun.
5. Add books from the Books page.
6. Register library members.
7. Issue a book by selecting a book and member.
8. Return the book to calculate overdue fine.
9. Check the dashboard and issue history for statistics.
10. Search and filter books or members as needed.

The sample library members are directory records, not login accounts. Create a separate staff login from the sign-up page.

## Fine Calculation
Late fine is calculated by the backend using this rule:

```text
If return_date > due_date:
    overdue_days = return_date - due_date
    fine = overdue_days * ₹5
else:
    fine = ₹0
```

## Screenshots
Placeholders for screenshots:
1. Dashboard
2. Books/Search page
3. Add Book form
4. Members page
5. Issue Book form
6. Issue/Return History with fine details

## Project Structure
```text
Library_Management_System/
├── library_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── library/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
└── .gitignore
```
