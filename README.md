# Freelancer Job Board API

A RESTful API for a Freelancer Job Board platform built with Django and Django REST Framework. This API allows clients to post jobs, freelancers to apply, and both parties to interact through reviews and hiring actions.

## Features

- JWT Authentication (access/refresh)
- Role-based permissions for Clients and Freelancers
- Job posting with filters, search, ordering, and pagination
- Freelancers can apply to jobs (with limits and duplication checks)
- Clients can hire applicants and auto-close jobs based on max applications
- Reviews system (with reply support)
- Swagger/OpenAPI documentation
- 100% test coverage with `pytest`

## Getting Started

### Requirements

- Python 3.9+
- pip
- SQLite
- Virtualenv

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/freelancer-job-board-api.git
cd freelancer-job-board-api

python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate

pip install -r requirements.txt
```
Create a .env file in the root directory:

DEBUG=
SECRET_KEY=
ALLOWED_HOSTS=
DATABASE_URL=

Run migrate 

```bash
python manage.py migrate
```
Run the Server

```bash
python manage.py runserver
```
Now you can import the postman collection into postman and test the API endpoints.

