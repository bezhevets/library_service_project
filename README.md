# Library Service Project

The Library Service Project is a comprehensive online management system tailored to address the challenges encountered by local libraries in manually tracking books, borrowings, users, and payments. The primary objective is to streamline administrative processes, enhance user experience, and introduce seamless online payment capabilities.

## Table of Contents
- [Features](#features)
- [Installation Git](#installation)
- [Run with Docker](#run-with-docker)

---
### Features:
The Library Service Project incorporates a range of features to efficiently manage library operations and provide a seamless experience for users. Here are some key features:

1. **Book Management:**
   - Add, edit, and delete books in the library catalog.

2. **User Management:**
   - Create and manage user accounts.

3. **Borrowing Operations:**

   - Borrow and return books with automated due date calculations.
   - Receive **notifications** for new borrowing.
   - Receive **notifications** for overdue books.

4. **Payment Integration:**

   - Enable secure online payments for fines and fees.
   - Integrated with Stripe for reliable and secure payment processing.

5. **Notifications:**

    - Receive notifications via Telegram for important events (book borrowings, overdue reminders).

6. **Authentication and Authorization:**

    - Implement JWT token-based authentication for secure user access.
    - Define roles and permissions to control access to different functionalities.

7. **Swagger Documentation:**

   - Utilize Swagger for comprehensive and interactive API documentation.

8. **Celery for Background Tasks:**

   - Utilize Celery for handling background tasks such as asynchronous notifications sending.
---
## Installation

1. Clone the repository:

   ```
   https://github.com/bezhevets/library_service_project.git
   ```
2. Copy .env_sample -> env. and populate with all required data:
   ```
   look env_sample file 
   
   POSTGRES_HOST= your db host
   POSTGRES_DB= name of your db
   POSTGRES_USER= username of your db user
   POSTGRES_PASSWORD= your db password
   SECRET_key=" your django secret key "
   ```
3. Create a virtual environment (OR LOOK WITH DOCKER):
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:

   - On macOS and Linux:
   ```source venv/bin/activate```
   - On Windows:
   ```venv\Scripts\activate```
5. Install project dependencie:
   ```
    pip install -r requirements.txt
   ```
6. Run database migrations:
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```
7. Run Celery:
   ```
   celery -A library_service_project worker -l INFO
   ```
8. Run Celery Beat:
   ```
   celery -A library_service_project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```
### Or take the first 3 steps and run with Docker
   Docker must be already installed
   ```
   docker-compose up --build
   ```
---   
## Run with Docker
Docker should be installed.

1. Pull docker container:

   ```
   docker pull ke1erman/library-service-project
   ```
2. Run docker container
   ```
    docker-compose build
    docker-compose up
   ```
---

You can test project with admin user:
```
email: admin@admin.com
password: 123456
```