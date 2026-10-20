# CloudAttend — Enhanced Edition Setup Guide

## Requirements
- Python 3.12+
- pip

## Quick Start (Local / SQLite)

```bash
# 1. Install dependencies
pip install -r requirements.txt
```

On Windows, `mysqlclient` is skipped because the local setup uses SQLite. The AWS Linux deployment still installs it for MySQL.

```bash
# 2. Apply migrations
python manage.py migrate

# 3. Create admin superuser
python manage.py createsuperuser

# 4. Create the "Student" group (required for role-based access)
python manage.py shell -c "
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='Student')
print('Student group ready.')
"

# 5. Run development server
python manage.py runserver
```

Open http://localhost:8000 — redirects to login, then to the dashboard.

## Separate Student and Admin Accounts

At `/accounts/login/`, choose the Student or Admin sign-in page. Students can create an account at `/accounts/student/signup/`; registration creates their student profile and signs them in. Existing enrolled students should use their assigned username and password.

Admin registration at `/accounts/admin/signup/` submits an access request and does not grant access immediately. An existing staff administrator approves requests in Django Admin (`/admin/`): open **Admin signup requests**, select pending requests, and choose **Approve selected admin signup requests**. Only approved staff accounts can use the admin portal.

## AWS Elastic Beanstalk (Production)

Set these environment variables in EB:
```
RDS_HOSTNAME   = <your-rds-endpoint>
RDS_DB_NAME    = attendance_db
RDS_USERNAME   = <db-user>
RDS_PASSWORD   = <db-password>
RDS_PORT       = 3306
SECRET_KEY     = <random-50-char-string>
DEBUG          = False
ALLOWED_HOSTS  = <your-eb-domain>
```

## User Roles

| Role      | Access                                     |
|-----------|---------------------------------------------|
| Admin/Staff| Full CRUD — students, attendance, subjects |
| Student   | Personal dashboard & attendance records     |

Students are **automatically** given a login account when created by admin.
Default password format: `Student@<last4-chars-of-uuid>`

## New Features vs Original

| Feature             | Old (Django 2.2) | New (Django 5.0) |
|---------------------|------------------|-------------------|
| Bulk attendance mark| ❌               | ✅                |
| Analytics dashboard | ❌               | ✅ Chart.js       |
| Department model    | ❌               | ✅                |
| Attendance reports  | ❌               | ✅                |
| REST API v2         | Basic            | Paginated + auth  |
| UI                  | Bootstrap 3      | Dark glassmorphism|
| Python version      | 3.6/3.7          | 3.12              |
| Profile photos      | ❌               | ✅                |
| Attendance %        | ❌               | ✅ Live calc      |
| Late/Excused status | ❌               | ✅                |
