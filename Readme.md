# POCUC API

This project was developed for Universidad del Valle, Cali, Colombia, to support the POCC-TVM project proposed by the Universidad Saludable department, as part of the smoke-free university policy.

## Overview

This API powers the backend of an observational data collection platform used to manage research studies. It handles study-specific forms organized by category, tracks observer sessions and visits, and provides progress reports for each study, along with an admin section for managing platform data. It's built with Django REST Framework and designed to be consumed by a separate React frontend. Authentication is handled via Firebase (Google Sign-In).

## Features

- User registration and authentication via Firebase Google Sign-In
- CRUD operations for sessions, visits, and answers (scoped to each observer) and full data access for admins
- Role-based permissions for three user types: observer, staff, and admin
- Study forms organized by category
- Endpoints for data statistics and study progress reports

## Tech Stack

- Django 5.2.6
- Django REST Framework (DRF) 3.16.1
- MySQL database
- Firebase Authentication (Google Sign-In)

## Requirements

- Python 3.11+ (recommended)
- PostgreSQL (via `psycopg2` / `psycopg2-binary`) — MySQL is also supported (`mysqlclient`) if preferred
- A Firebase project with service account credentials (used by `firebase_admin`)
- `pip` and `venv` for dependency management

### Main dependencies

- **Django** 5.2.6
- **djangorestframework** 3.16.1
- **drf-spectacular** — OpenAPI/Swagger schema generation
- **django-cors-headers** — CORS handling for the React frontend
- **firebase_admin** / **google-auth** / **google-cloud-firestore** / **google-cloud-storage** — Firebase authentication and Google Cloud integration
- **dj-database-url** — database configuration via environment variable
- **python-dotenv** — environment variable management

Full pinned versions are listed in [`requirements.txt`](./requirements.txt).

# Installation

```
git clone https://github.com/andresmg42/POCUCAPI.git
cd pocuc
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

# Environment Variables

see the [`.env.example`](./.env.example). file.

# Database SetUp

```
python manage.py migrate
python manage.py createsuperuser

```

# Running the Project

```
python manage.py runserver
```

# API Documentation

- path to swagger documentation: /api/docs/swagger/
- path to redoc documentation: /api/docs/redoc/
- path to schema generations: /api/schema/

## Main Endpoints

### Core resources (standard CRUD)

| Resource       | Endpoint                | Methods                 | Description                                 |
| -------------- | ----------------------- | ----------------------- | ------------------------------------------- |
| Campus         | `/campus/`              | GET, POST               | List / create campuses                      |
| Campus         | `/campus/{id}/`         | GET, PUT, PATCH, DELETE | Retrieve / update / delete a campus         |
| Category       | `/category/`            | GET, POST               | List / create categories                    |
| Category       | `/category/{id}/`       | GET, PUT, PATCH, DELETE | Retrieve / update / delete a category       |
| Subcategory    | `/subcategory/`         | GET, POST               | List / create subcategories                 |
| Subcategory    | `/subcategory/{id}/`    | GET, PUT, PATCH, DELETE | Retrieve / update / delete a subcategory    |
| Zone           | `/zone/`                | GET, POST               | List / create zones                         |
| Zone           | `/zone/{id}/`           | GET, PUT, PATCH, DELETE | Retrieve / update / delete a zone           |
| Observer       | `/observer/`            | GET, POST               | List / create observers                     |
| Observer       | `/observer/{id}/`       | GET, PUT, PATCH, DELETE | Retrieve / update / delete an observer      |
| Question       | `/question/`            | GET, POST               | List / create survey questions              |
| Question       | `/question/{id}/`       | GET, PUT, PATCH, DELETE | Retrieve / update / delete a question       |
| Options        | `/options/`             | GET, POST               | List / create question options              |
| Options        | `/options/{id}/`        | GET, PUT, PATCH, DELETE | Retrieve / update / delete an option        |
| Survey         | `/survey/surveys/`      | GET, POST               | List / create surveys                       |
| Survey         | `/survey/surveys/{id}/` | GET, PUT, PATCH, DELETE | Retrieve / update / delete a survey         |
| Survey Session | `/surveysession/`       | GET, POST               | List / create survey sessions               |
| Survey Session | `/surveysession/{id}/`  | GET, PUT, PATCH, DELETE | Retrieve / update / delete a survey session |
| Visit          | `/visit/`               | GET, POST               | List / create visits                        |
| Visit          | `/visit/{id}/`          | GET, PUT, PATCH, DELETE | Retrieve / update / delete a visit          |
| Response       | `/response/`            | GET, POST               | List / create observer answers              |
| Response       | `/response/{id}/`       | GET, PUT, PATCH, DELETE | Retrieve / update / delete an answer        |

### Custom / additional endpoints

| Endpoint                                         | Method | Description                               |
| ------------------------------------------------ | ------ | ----------------------------------------- |
| `/category/category_completed/`                  | GET    | Check completion status of a category     |
| `/category/list/`                                | GET    | Simplified list of categories             |
| `/observer/create/`                              | POST   | Custom observer creation flow             |
| `/observer/get_table_observer_info/`             | GET    | Tabular observer info for dashboards      |
| `/question/get_questions_bank`                   | GET    | Retrieve the question bank                |
| `/question/get_questions_by_survey`              | GET    | Get questions filtered by survey          |
| `/question/reorder_questions`                    | POST   | Reorder questions (drag-and-drop support) |
| `/response/create/`                              | POST   | Custom response creation flow             |
| `/response/delete_responses_by_category/`        | DELETE | Bulk-delete responses by category         |
| `/survey/get_survey/`                            | GET    | Retrieve a specific survey                |
| `/survey/list/`                                  | GET    | Simplified list of surveys                |
| `/surveysession/get_survey_session_by_survey_id` | GET    | Get sessions filtered by survey ID        |
| `/surveysession/get_table_session_info/`         | GET    | Tabular session info for dashboards       |
| `/surveysession/update_start_session/`           | POST   | Mark a session as started                 |
| `/visit/sessionvisits/`                          | GET    | List visits for a given session           |
| `/visit/update_start_date/`                      | POST   | Update the start date of a visit          |
| `/zone/get_zones_by_campus/`                     | GET    | Get zones filtered by campus              |
| `/users/get_role_status`                         | GET    | Get the current user's role/status        |
| `/pocucstats/descriptive_analisis_by_question/`  | GET    | Descriptive statistics per question       |
| `/api/schema/`                                   | GET    | OpenAPI schema (this document)            |

> Full interactive documentation available at `/api/schema/` (Swagger/Redoc via drf-spectacular).

## Authentication

This API uses **Firebase Authentication (Google Sign-In)** rather than Django's built-in session or token auth.

**Flow:**

1. The frontend (React) handles the Google sign-in popup via the Firebase client SDK and obtains a Firebase ID token.
2. The frontend sends this token with every request in the `Authorization` header:

```
   Authorization: Bearer <firebase_id_token>
```

3. The backend verifies the token using `firebase_admin.auth.verify_id_token()`.
4. **On first sign-in, an Observer record is automatically created** and linked to the verified Firebase account — this is the only role provisioned through the Google sign-in flow.
5. **Staff and Admin accounts are not created via Firebase sign-in.** They are created manually through the Django admin panel by an existing admin.
6. Endpoints enforce **role-based permissions** on top of authentication.

**Token expiration:** Firebase ID tokens expire after 1 hour. The frontend refreshes them automatically via the Firebase SDK; no manual refresh endpoint is needed on this API.

> Note: This API does not issue its own JWTs or handle passwords — Firebase is the sole identity provider, and it only auto-provisions the Observer role. Staff/Admin access is granted manually.

## Project Structure

```
POCUC/
├── campus/              # Campus model, views, serializers
├── category/             # Survey category app
├── observer/             # Observer role management
├── option/                # Question options app
├── phpmyadmin/            # phpMyAdmin config/assets (legacy MySQL admin tooling)
├── pocuc/                 # Main Django project settings (settings.py, urls.py, wsgi/asgi)
├── pocucstats/            # Statistics and reporting endpoints
├── question/              # Survey questions app
├── response/              # Observer answers/responses app
├── subcategory/           # Survey subcategory app
├── survey/                # Survey definitions app
├── surveysession/         # Survey session tracking app
├── users/                 # User/role management, Firebase auth integration
├── visit/                 # Visit tracking app
├── zone/                  # Zone management app
├── .env                   # Local environment variables (not committed)
├── .env.example           # Environment variable template
├── .gitignore
├── entity_relation.md     # Entity-relationship documentation
├── manage.py              # Django management script
├── Readme.md
└── requirements.txt
```

Each app follows Django's standard structure (`models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`).

## Contributing

- Follow standard branch naming (`feature/`, `fix/`, `chore/`)
- Run linting/formatting before opening a PR
- Describe changes clearly in PR descriptions

## License

This project currently has no license. All rights reserved — please contact the author before reusing any part of this code.
