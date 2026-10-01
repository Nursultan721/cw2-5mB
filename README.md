# Notes API

REST API на Django REST Framework для регистрации пользователей и работы с заметками.

## Запуск

```bash
python -m venv .venv
```

Активируйте виртуальное окружение, затем выполните:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Swagger UI доступен по адресу `http://127.0.0.1:8000/api/docs/`.

## Эндпоинты

- `POST /register/` — создать пользователя (`username`, `password`, необязательно `email`).
- `POST /login/` — получить токен (`username`, `password`).
- `GET /profile/` — получить профиль текущего пользователя.
- `/notes/` — список и создание заметок; `GET`, `POST`.
- `/notes/<id>/` — просмотр, частичное изменение и удаление заметки.
- `GET /api/schema/` — схема OpenAPI.

Для защищённых запросов передавайте заголовок `Authorization: Token <token>`. Поиск выполняется через `?search=`, фильтрация по названию через `?title=` или `?title__icontains=`, сортировка через `?ordering=title` или `?ordering=-id`. Пагинация использует `?page=` и `?page_size=`.
