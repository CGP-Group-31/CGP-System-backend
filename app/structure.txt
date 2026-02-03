NOT the exact endpoints

app/
├── main.py
│
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── __init__.py
│
├── api/
│   └── v1/
│       ├── caregiver/
│       │   ├── auth/
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   └── __init__.py
│       │   │
│       │   ├── profile/
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   └── __init__.py
│       │   │
│       │   ├── requests/
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   └── __init__.py
│       │   │
│       │   ├── __init__.py
│       │
│       ├── caretaker/
│       │   ├── auth/
│       │   ├── profile/
│       │   ├── requests/
│       │   └── __init__.py
│       │
│       └── __init__.py
│
├── services/
│   ├── fcm_service.py
│   └── scheduler.py
│
└── __init__.py
