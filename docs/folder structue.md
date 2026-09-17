test-flow/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       │
│   │       ├── auth.py
│   │       └── users.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── role.py
│   │   └── user_role.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organization.py
│   │   └── user.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   └── role.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   └── token.py
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── permissions.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── auth/
│   │   ├── test_register.py
│   │   ├── test_login.py
│   │   └── test_password.py
│   │
│   └── users/
│       ├── test_create_user.py
│       └── test_user_list.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── Dockerfile