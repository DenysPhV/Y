# Y
* PhotoShare/
* ├── app/
* │   ├── api/
* │   │   ├── endpoints/
* │   │   │   ├── authentication.py
* │   │   │   ├── photos.py
* │   │   │   └── comments.py
* │   │   └── api.py
* │   ├── core/
* │   │   ├── config.py
* │   │   └── database.py
* │   ├── models/
* │   │   ├── user.py
* │   │   ├── photo.py
* │   │   └── comment.py
* │   ├── schemas/
* │   │   ├── user.py
* │   │   ├── photo.py
* │   │   └── comment.py
* │   ├── services/
* │   │   ├── auth_service.py
* │   │   └── photo_service.py
* │   ├── main.py
* │   └── requirements.txt
* ├── tests/
* │   ├── test_auth.py
* │   ├── test_photos.py
* │   └── test_comments.py
* ├── pyproject.toml
* ├── Dockerfile
* └── README.md



# Опис структури:

* app/: Головна директорія для коду проекту.
  * api/: Зберігає всі API endpoints.
    * endpoints/: Конкретні модулі для кожного набору endpoints (аутентифікація, фотографії, коментарі).
  * core/: Загальні налаштування та конфігурація.
  * models/: ORM моделі для взаємодії з базою даних.
  * schemas/: Pydantic моделі для валідації вхідних і вихідних даних.
  * services/: Логіка додатку, така як аутентифікація, завантаження фото, і т.д.
  * main.py: Точка входу для FastAPI додатку.
  * requirements.txt: Залежності проекту.
* tests/: Модульні тести для проекту.

* Dockerfile: Для контейнеризації проекту.
* README.md: Документація та інструкції.